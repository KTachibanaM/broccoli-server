import logging
import minio
import io
import json
from minio.error import BucketAlreadyExists, BucketAlreadyOwnedByYou


class S3Wrapper(object):
    def __init__(self, endpoint_url: str, access_key: str, secret_key: str, region: str, bucket_name: str,
                 use_ssl: bool, logger: logging.Logger):
        self.minio_client = minio.Minio(
            endpoint_url,
            access_key=access_key,
            secret_key=secret_key,
            secure=use_ssl
        )
        self.bucket_name = bucket_name
        try:
            logger.info(f"Creating bucket {bucket_name} in region {region if region else 'null'}")
            # todo: failures?
            self.minio_client.make_bucket(bucket_name, location=region)
        except BucketAlreadyExists:
            logger.info(f"Bucket with name {bucket_name} already exists in region {region if region else 'null'}")
        except BucketAlreadyOwnedByYou as e:
            logger.info(f"Bucket with name {bucket_name} already owned by you "
                        f"in region {region if region else 'null'}, error {e.message}")
        self.minio_client.set_bucket_policy(
            bucket_name,
            json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": ["s3:GetObject"],
                            "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
                        }
                    ]
                }
            )
        )

    def put_object(self, object_name, raw_bytes):
        self.minio_client.put_object(
            self.bucket_name,
            object_name,
            io.BytesIO(raw_bytes),
            len(raw_bytes),
            "application/octet-stream",
            None
        )

    def get_object(self, object_name) -> bytes:
        return self.minio_client.get_object(
            self.bucket_name,
            object_name
        ).read()
