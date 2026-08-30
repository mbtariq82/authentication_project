import logging

from agents.services.instagram_service import InstagramService

logger = logging.getLogger(__name__)


class InstagramPublishTool:

    def __init__(self):
        self.instagram_service = InstagramService()

    async def publish(
        self,
        image_url: str,
        caption: str,
        approved: bool,
    ):
        logger.info(
            "INSTAGRAM_PUBLISH_TOOL | publish | approved=%s | image_url=%s",
            approved, image_url,
        )

        if not approved:
            logger.warning(
                "INSTAGRAM_PUBLISH_TOOL | publish blocked — not approved"
            )
            raise PermissionError(
                "Human approval is required "
                "before publishing to Instagram."
            )

        return await self.instagram_service.publish_post(
            image_url=image_url,
            caption=caption,
        )