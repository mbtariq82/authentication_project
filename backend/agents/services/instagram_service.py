class InstagramService:

    async def publish_post(
        self,
        image_url: str,
        caption: str,
    ) -> dict:

        # Meta Graph API call goes here

        ...

        return {
            "status": "published",
            "post_id": "...",
        }