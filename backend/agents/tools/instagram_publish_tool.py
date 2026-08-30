from agents.services.instagram_service import InstagramService


class InstagramPublishTool:

    def __init__(self):
        self.instagram_service = InstagramService()

    async def publish(
        self,
        image_url: str,
        caption: str,
        approved: bool,
    ):

        if not approved:
            raise PermissionError(
                "Human approval is required "
                "before publishing to Instagram."
            )

        return await self.instagram_service.publish_post(
            image_url=image_url,
            caption=caption,
        )
