import io
import uuid

import boto3
from botocore.client import Config

from app.core.config import settings


s3 = boto3.client(
    "s3",
    endpoint_url=f"http://{settings.minio_endpoint}",
    aws_access_key_id=settings.minio_access_key,
    aws_secret_access_key=settings.minio_secret_key,
    config=Config(signature_version="s3v4"),
)


def ensure_bucket():
    buckets = s3.list_buckets()

    names = [
        bucket["Name"]
        for bucket in buckets.get("Buckets", [])
    ]

    if settings.minio_bucket not in names:
        s3.create_bucket(
            Bucket=settings.minio_bucket
        )


def upload_file(
    content: bytes,
    original_name: str,
    content_type: str,
    folder: str,
) -> str:

    extension = ""

    if "." in original_name:
        extension = "." + original_name.rsplit(".", 1)[1]

    key = (
        f"{folder}/"
        f"{uuid.uuid4().hex}"
        f"{extension}"
    )

    s3.upload_fileobj(
        io.BytesIO(content),
        settings.minio_bucket,
        key,
        ExtraArgs={
            "ContentType": content_type,
        },
    )

    return key


def download_file(key: str) -> bytes:

    response = s3.get_object(
        Bucket=settings.minio_bucket,
        Key=key,
    )

    return response["Body"].read()