import uuid
import os
from urllib.request import urlopen
from broccoli_plugin_base.base_worker import BaseWorker
from .s3_wrapper import S3Wrapper


class S3ImageHoarder(BaseWorker):
    def __init__(self):
        super(S3ImageHoarder, self).__init__("s3_image_hoarder")
        self.image_s3 = None

    def pre_work(self):
        self.image_s3 = S3Wrapper(
            endpoint_url=os.getenv("S3_ENDPOINT_URL"),
            access_key=os.getenv("S3_ACCESS_KEY"),
            secret_key=os.getenv("S3_SECRET_KEY"),
            region=os.getenv("S3_REGION"),
            bucket_name='broccoli',
            use_ssl=True if os.getenv("S3_USE_SSL", "false") == "true" else False,
            logger=self.logger
        )

    def work(self):
        documents = self.rpc_client.blocking_query({
            "image_url": {
                "$exists": True,
            },
            "s3_image_id": {
                "$exists": False
            }
        }, limit=50)
        if not documents:
            self.logger.info("No image to hoard")
            return
        self.logger.info(f"{len(documents)} images to hoard")
        for document in documents:
            if type(document['image_url']) != str:
                self.logger.error(f"Invalid image url in document {document}")
                continue
            image_url = document['image_url']  # type: str

            self.upload(image_url)

    def upload(self, image_url: str):
        # todo: check for uuid duplication
        s3_image_id = str(uuid.uuid4())

        self.logger.debug(f"Downloading image at url {image_url}")
        # todo: timeout
        res = urlopen(image_url)
        image_bytes = res.read()

        self.logger.debug(f"Uploading image at url {image_url} to S3 {self.image_s3}/{s3_image_id}")
        # todo: s3 upload failure?
        # todo: reaper to remove keys without actual image in metadata
        self.image_s3.put_object(s3_image_id, image_bytes)

        self.rpc_client.blocking_update_one(
            filter_q={
                "image_url": image_url
            },
            update_doc={
                "$set": {
                    "s3_image_id": s3_image_id
                }
            }
        )
