import logging
from common.logging import DefaultHandler

logger = logging.getLogger('scheduler')
logger.setLevel(logging.INFO)
logger.addHandler(DefaultHandler)
