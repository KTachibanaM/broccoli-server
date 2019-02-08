import logging
from common.logging import DefaultHandler

logger = logging.getLogger('broccoli.server')
logger.setLevel(logging.INFO)
logger.addHandler(DefaultHandler)
