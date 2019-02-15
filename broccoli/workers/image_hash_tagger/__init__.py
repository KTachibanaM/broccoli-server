import io
import imagehash
from PIL import Image
from worker_manager.base_worker import BaseWorker
from worker_manager.clients.s3_wrapper import S3Wrapper


class ImageHashTagger(BaseWorker):
    def __init__(self, image_s3: S3Wrapper):
        super(ImageHashTagger, self).__init__("image_hash_tagger")
        self.image_s3 = image_s3

    def pre_work(self):
        pass

    def work(self):
        documents = self.rpc_client.blocking_query({
            "s3_image_id": {
                "$exists": True
            },
            "image_dhash": {
                "$exists": False
            }
        }, limit=50)
        if not documents:
            self.logger.info("No image to tag hash")
            return
        self.logger.info(f"Tagging hash for {len(documents)} images")
        for document in documents:
            if type(document["s3_image_id"]) != str:
                self.logger.error(f"Invalid s3 image id in document {document}")
                continue
            s3_image_id = document['s3_image_id']  # type: str

            self.logger.debug(f"Getting image from S3 {self.image_s3}/{s3_image_id}")
            image_bytes = self.image_s3.get_object(s3_image_id)

            self.logger.debug(f"Computing and updating image hash for {s3_image_id}")
            pil_image = Image.open(io.BytesIO(image_bytes))
            dhash_binary_string = imagehash.dhash(pil_image).hash.flatten().tolist()
            self.rpc_client.blocking_update_one_binary_string(
                filter_q={
                    "s3_image_id": s3_image_id
                },
                key="image_dhash",
                binary_string=dhash_binary_string
            )
