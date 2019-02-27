import logging
from broccoli_common.logging import DefaultHandler

logger = logging.getLogger('broccoli.worker_manager')
logger.setLevel(logging.INFO)
logger.addHandler(DefaultHandler)
