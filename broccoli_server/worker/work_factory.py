import logging
import time
from typing import Optional, Callable, Tuple
from .work_context import WorkContextFactory
from .worker_metadata import WorkerMetadata
from .worker_cache import WorkerCache
from .worker_config_store import WorkerConfigStore
from sentry_sdk import capture_exception
from broccoli_server.interface.worker import Worker

logger = logging.getLogger(__name__)


class WorkFactory(object):
    def __init__(self,
                 work_context_factory: WorkContextFactory,
                 worker_cache: WorkerCache,
                 worker_config_store: WorkerConfigStore,
                 sentry_enabled: bool,
                 pause_workers: bool
                 ):
        self.work_context_factory = work_context_factory
        self.worker_cache = worker_cache
        self.worker_config_store = worker_config_store
        self.sentry_enabled = sentry_enabled
        self.pause_workers = pause_workers

    def get_work_func(self, worker_metadata: WorkerMetadata) -> Optional[Tuple[Callable, str]]:
        module_name, args, error_resiliency = \
            worker_metadata.module_name, worker_metadata.args, worker_metadata.error_resiliency
        status, worker_or_message = self.worker_cache.load(module_name, args)
        if not status:
            logger.error("Fails to load worker", extra={
                'module_name': module_name,
                'args': args,
                'message': worker_or_message
            })
            return None
        worker = worker_or_message  # type: Worker
        worker_id = worker.get_id()
        work_context = self.work_context_factory.build(worker_id)
        worker.pre_work(work_context)

        def work_func():
            if self.pause_workers:
                logger.info("Workers have been globally paused")
                return

            try:
                worker.work(work_context)
                # always reset error count
                ok, err = self.worker_config_store.reset_error_count(worker_id)
                if not ok:
                    logger.error("Fails to reset error count", extra={
                        'worker_id': worker_id,
                        'reason': err
                    })
            except Exception as e:
                report_ex = True
                if error_resiliency > 0:
                    ok, error_count, err = self.worker_config_store.get_error_count(worker_id)
                    if not ok:
                        logger.error("Fails to get error count", extra={
                            'worker_id': worker_id,
                            'reason': err
                        })
                    if error_count < error_resiliency:
                        # only not to report exception when error resiliency is set and error count is below resiliency
                        report_ex = False

                if report_ex:
                    if self.sentry_enabled:
                        capture_exception(e)
                    else:
                        print(str(e))
                        logger.exception("Fails to execute work", extra={
                            'worker_id': worker_id,
                        })
                else:
                    print(str(e))
                    logger.info("Not reporting exception because of error resiliency", extra={
                        'worker_id': worker_id
                    })

                if error_resiliency > 0:
                    # only to touch error count if error resiliency is set
                    ok, err = self.worker_config_store.increment_error_count(worker_id)
                    if not ok:
                        logger.error('Fails to increment error count', extra={
                            'worker_id': worker_id,
                            'reason': err
                        })

            self.worker_config_store.set_last_executed_seconds(worker_id, int(time.time()))

        return work_func, worker_id
