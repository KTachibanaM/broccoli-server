import os
import logging
from common.logging import DefaultHandler
from pathlib import Path
from dotenv import load_dotenv
from worker_manager.clients.s3_wrapper import S3Wrapper

if os.path.exists('worker_globals.env'):
    print("Loading worker_globals.env")
    load_dotenv(dotenv_path=Path('worker_globals.env'))
else:
    print("worker_globals.env does not exist")

logger = logging.getLogger('broccoli.workers')
logger.setLevel(logging.INFO)
logger.addHandler(DefaultHandler)

worker_globals = {
    "image_s3": S3Wrapper(
        endpoint_url=os.getenv("S3_ENDPOINT_URL"),
        access_key=os.getenv("S3_ACCESS_KEY"),
        secret_key=os.getenv("S3_SECRET_KEY"),
        region=os.getenv("S3_REGION"),
        bucket_name='broccoli',
        use_ssl=True if os.getenv("S3_USE_SSL", "false") == "true" else False,
        logger=logger
    )
}
