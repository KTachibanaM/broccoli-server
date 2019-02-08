import sys
import logging

DefaultHandler = logging.StreamHandler()
DefaultHandler.setFormatter(logging.Formatter("[%(asctime)s][%(name)s][%(levelname)s] %(message)s"))
