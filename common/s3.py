import os

from dotenv import load_dotenv

load_dotenv()

import boto3


class S3Connector:
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    bucket_name = "mailpocket-email"

    def __init__(self) -> None:
        self.s3_clinet = boto3.client(
            "s3",
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name="ap-northeast-2",
        )
