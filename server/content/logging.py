import logging
from common.logging import DefaultHandler

logger = logging.getLogger('content')
logger.setLevel(logging.INFO)
logger.addHandler(DefaultHandler)
