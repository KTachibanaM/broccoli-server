import logging

DefaultHandler = logging.StreamHandler()
DefaultHandler.setFormatter(logging.Formatter("[%(asctime)s][%(name)s][%(levelname)s] %(message)s"))


def configure_werkzeug_logger():
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.ERROR)
