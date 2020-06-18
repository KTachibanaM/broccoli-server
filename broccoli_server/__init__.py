import logging
import os

root_handler = logging.StreamHandler()
root_handler.setFormatter(logging.Formatter("[%(asctime)s][%(name)s][%(levelname)s] %(message)s"))
if os.environ.get("LOGGING_DEBUG", "false") == "true":
    root_handler.setLevel(logging.DEBUG)
else:
    root_handler.setLevel(logging.INFO)
logging.getLogger(__name__).addHandler(root_handler)
