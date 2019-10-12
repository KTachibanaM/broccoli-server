import logging
import os

DefaultHandler = logging.StreamHandler()
DefaultHandler.setFormatter(logging.Formatter("[%(asctime)s][%(name)s][%(levelname)s] %(message)s"))
DefaultHandler.setLevel(logging.INFO)


def get_logging_level():
    if "LOGGING_DEBUG" in os.environ and os.environ["LOGGING_DEBUG"] == "true":
        return logging.DEBUG
    else:
        return logging.INFO
