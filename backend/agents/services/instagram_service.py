import os

import httpx


class InstagramService:
    """
    Publishes to Instagram via Zernio's unified posting API
    (https://docs.zernio.com), instead of calling Meta's Graph API
    directly. This replaces the old stub — no Meta app review, no
    Facebook Page linking, no token refresh cycle required.

    Configure via environment variables:
      ZERNIO_API_KEY     — from the Zernio dashboard's "API Keys" page
      ZERNIO_ACCOUNT_ID  — the connected Instagram account's id,
                            visible on the Connections page (the
                            accountId shown for @nexa_bank_uk)
    """

    BASE_URL = "https://zernio.com/api/v1"

    def __init__(self):
        self.api_key = os.getenv("ZERNIO_API_KEY")
        self.account_id = os.getenv("ZERNIO_ACCOUNT_ID")

    async def publish_post(
        self,
        image_url: str,
        caption: str,
    ) -> dict:

        if not self.api_key or not self.account_id:
            raise RuntimeError(
                "Zernio is not configured. Set ZERNIO_API_KEY and "
                "ZERNIO_ACCOUNT_ID environment variables."
            )

        payload = {
            "content": caption,
            "mediaItems": [
                {
                    "type": "image",
                    "url": image_url,
                }
            ],
            "platforms": [
                {
                    "platform": "instagram",
                    "accountId": self.account_id,
                }
            ],
            "publishNow": True,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.BASE_URL}/posts",
                json=payload,
                headers=headers,
            )

        if response.status_code >= 400:
            raise RuntimeError(
                f"Zernio publish failed "
                f"({response.status_code}): {response.text}"
            )

        data = response.json()
        post = data.get("post", data)

        return {
            "status": "published",
            "post_id": post.get("_id"),
            "raw": post,
        }