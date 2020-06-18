import logging
import os

root_handler = logging.StreamHandler()
root_handler.setFormatter(logging.Formatter("[%(asctime)s][%(name)s][%(levelname)s] %(message)s"))
logger = logging.getLogger(__name__)
logger.addHandler(root_handler)
if os.environ.get("LOGGING_DEBUG", "false") == "true":
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
