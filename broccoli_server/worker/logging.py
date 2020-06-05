import logging
from broccoli_server.utils import DefaultHandler, get_logging_level

logger = logging.getLogger('worker')
logger.setLevel(get_logging_level())
logger.addHandler(DefaultHandler)
