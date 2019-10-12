import logging
from broccoli_server.common import DefaultHandler, get_logging_level

logger = logging.getLogger('scheduler')
logger.setLevel(get_logging_level())
logger.addHandler(DefaultHandler)
