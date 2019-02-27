import logging
from broccoli_common.logging import DefaultHandler

logger = logging.getLogger('broccoli.api')
logger.setLevel(logging.INFO)
logger.addHandler(DefaultHandler)
