import os

from dotenv import load_dotenv

load_dotenv()

import boto3


class S3Connector:
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    virginia_bucket_name = "mailpocket"
    seoul_bucket_name = "mailpocket-seoul"

    def __init__(self) -> None:
        self.virginia_s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )
        self.seoul_s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )
