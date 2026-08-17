import asyncio
from uuid import uuid4

from botocore.exceptions import BotoCoreError, ClientError

from exceptions import ProfileImageStorageError
from storage.abstract_profile_image_storage import AbstractProfileImageStorage


class S3ProfileImageStorage(AbstractProfileImageStorage):
    def __init__(
        self,
        client,
        bucket: str,
        url_expiry_seconds: int,
    ) -> None:
        self.client = client
        self.bucket = bucket
        self.url_expiry_seconds = url_expiry_seconds

    async def save(self, user_id: int, image: bytes) -> str:
        key = f"profile-images/{user_id}/{uuid4().hex}.webp"
        try:
            await asyncio.to_thread(
                self.client.put_object,
                Bucket=self.bucket,
                Key=key,
                Body=image,
                ContentType="image/webp",
                CacheControl="private, max-age=3600",
            )
        except (BotoCoreError, ClientError) as exc:
            raise ProfileImageStorageError() from exc
        return key

    async def delete(self, key: str) -> None:
        try:
            await asyncio.to_thread(
                self.client.delete_object,
                Bucket=self.bucket,
                Key=key,
            )
        except (BotoCoreError, ClientError) as exc:
            raise ProfileImageStorageError() from exc

    async def get_url(self, key: str) -> str:
        try:
            return await asyncio.to_thread(
                self.client.generate_presigned_url,
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=self.url_expiry_seconds,
            )
        except (BotoCoreError, ClientError) as exc:
            raise ProfileImageStorageError() from exc
