import logging
from broccoli_common.logging import DefaultHandler

logger = logging.getLogger('broccoli.server')
logger.setLevel(logging.INFO)
logger.addHandler(DefaultHandler)
