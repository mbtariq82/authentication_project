from functools import lru_cache

import boto3
from botocore.config import Config

from config import (
    AWS_REGION,
    PROFILE_IMAGE_LOCAL_DIR,
    PROFILE_IMAGE_STORAGE_BACKEND,
    PROFILE_IMAGE_URL_EXPIRY_SECONDS,
    PROFILE_IMAGE_URL_PREFIX,
    PROFILE_IMAGES_BUCKET,
)
from storage.abstract_profile_image_storage import AbstractProfileImageStorage
from storage.local_profile_image_storage import LocalProfileImageStorage
from storage.s3_profile_image_storage import S3ProfileImageStorage


@lru_cache
def get_profile_image_storage() -> AbstractProfileImageStorage:
    if PROFILE_IMAGE_STORAGE_BACKEND == "local":
        return LocalProfileImageStorage(
            root=PROFILE_IMAGE_LOCAL_DIR,
            url_prefix=PROFILE_IMAGE_URL_PREFIX,
        )

    client = boto3.client(
        "s3",
        region_name=AWS_REGION,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "virtual"},
        ),
    )
    return S3ProfileImageStorage(
        client=client,
        bucket=PROFILE_IMAGES_BUCKET,
        url_expiry_seconds=PROFILE_IMAGE_URL_EXPIRY_SECONDS,
    )
