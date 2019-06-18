import logging
from common.logging import DefaultHandler, get_logging_level

logger = logging.getLogger('scheduler')
logger.setLevel(get_logging_level())
logger.addHandler(DefaultHandler)
