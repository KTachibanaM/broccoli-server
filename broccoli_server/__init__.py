import logging
import os

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter("[%(asctime)s][%(name)s][%(levelname)s] %(message)s"))

root_logger = logging.getLogger(__name__)
root_logger.addHandler(stream_handler)

worker_logger = logging.getLogger("broccoli.worker")
worker_logger.addHandler(stream_handler)

one_off_job_logger = logging.getLogger("broccoli.one_off_job")
one_off_job_logger.addHandler(stream_handler)

if os.environ.get("LOGGING_DEBUG", "false") == "true":
    root_logger.setLevel(logging.DEBUG)
    worker_logger.setLevel(logging.DEBUG)
    one_off_job_logger.setLevel(logging.DEBUG)
else:
    root_logger.setLevel(logging.INFO)
    worker_logger.setLevel(logging.INFO)
    one_off_job_logger.setLevel(logging.INFO)
