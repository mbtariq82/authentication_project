import asyncio
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4

from exceptions import ProfileImageStorageError
from storage.abstract_profile_image_storage import AbstractProfileImageStorage


class LocalProfileImageStorage(AbstractProfileImageStorage):
    def __init__(self, root: Path, url_prefix: str) -> None:
        self.root = root.resolve()
        self.url_prefix = url_prefix.rstrip("/")

    async def save(self, user_id: int, image: bytes) -> str:
        key = f"profile-images/{user_id}/{uuid4().hex}.webp"
        destination = self._path_for(key)

        try:
            await asyncio.to_thread(
                destination.parent.mkdir,
                parents=True,
                exist_ok=True,
            )
            await asyncio.to_thread(destination.write_bytes, image)
        except OSError as exc:
            raise ProfileImageStorageError() from exc
        return key

    async def delete(self, key: str) -> None:
        path = self._path_for(key)
        try:
            await asyncio.to_thread(path.unlink, missing_ok=True)
        except OSError as exc:
            raise ProfileImageStorageError() from exc

    async def get_url(self, key: str) -> str:
        relative_key = key.removeprefix("profile-images/")
        return f"{self.url_prefix}/{quote(relative_key, safe='/')}"

    def _path_for(self, key: str) -> Path:
        path = (self.root / key).resolve()
        if self.root not in path.parents:
            raise ProfileImageStorageError()
        return path
