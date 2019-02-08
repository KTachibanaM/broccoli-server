import logging
import json
import boto3
from botocore.client import Config


class S3Wrapper(object):
    def __init__(self, endpoint_url: str, access_key: str, secret_key: str, region: str, bucket_name: str,
                 logger: logging.Logger):
        self.s3 = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4'),
            region_name=region
        )
        self.endpoint_url = endpoint_url
        self.region = region
        self.bucket_name = bucket_name
        bucket_names = map(lambda b: b['Name'], self.s3.list_buckets()['Buckets'])
        if self.bucket_name not in bucket_names:
            logger.info(f"Creating bucket {self.bucket_name}")
            # todo: failures?
            self.s3.create_bucket(Bucket=self.bucket_name)
            self.s3.put_bucket_policy(Bucket=self.bucket_name, Policy=json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": ["s3:GetObject"],
                        "Resource":[f"arn:aws:s3:::{self.bucket_name}/*"]
                    }
                ]
            }))
        else:
            logger.info(f"Bucket with name {bucket_name} already exists in region {region}")

    def __str__(self):
        return f"{self.region}.{self.endpoint_url}/{self.bucket_name}"
