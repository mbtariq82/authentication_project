import logging
import os
import time

import httpx

logger = logging.getLogger(__name__)


class ImageGeneratorTool:
    """
    Generates an image from a text prompt using Nano Banana Pro via
    the kie.ai API (https://kie.ai). Used to turn the Instagram
    tool's IMAGE_PROMPT into an actual image_url before the post is
    held for human approval.

    kie.ai's create-task/poll flow is asynchronous under the hood, so
    this wraps that as a single blocking call: submit the task, then
    poll recordInfo until it's done (or times out).

    Configure via environment variables:
      KIE_API_KEY — from https://kie.ai/api-key
      IMAGE_GEN_TIMEOUT_SECONDS — how long to wait before giving up
        (default 240 seconds). Nano Banana Pro's generation time
        varies with kie.ai's current load and can occasionally run
        past 2 minutes even for a normal request — this was raised
        from an original 120s default after hitting real timeouts.

    This is best-effort: callers should catch exceptions and fall
    back to leaving image_url unset, letting the admin attach an
    image manually when approving the post (see
    POST /admin/approve/{id}?image_url=...). If a task times out
    here, it's usually still finishing on kie.ai's side — check its
    status with the task_id from the timeout log line:
      curl "https://api.kie.ai/api/v1/jobs/recordInfo?taskId=TASK_ID" \
        -H "Authorization: Bearer $KIE_API_KEY"
    """

    CREATE_URL = "https://api.kie.ai/api/v1/jobs/createTask"
    STATUS_URL = "https://api.kie.ai/api/v1/jobs/recordInfo"

    def __init__(
        self,
        poll_interval: float = 3.0,
        timeout_seconds: float | None = None,
    ):
        self.api_key = os.getenv("KIE_API_KEY")
        self.poll_interval = poll_interval
        self.timeout_seconds = timeout_seconds or float(
            os.getenv("IMAGE_GEN_TIMEOUT_SECONDS", "240")
        )

        logger.info(
            "ImageGeneratorTool initialized | configured=%s",
            bool(self.api_key),
        )

    def generate(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        resolution: str = "1K",
        output_format: str = "png",
    ) -> str:

        # Append a hard negative instruction regardless of what the
        # caller's prompt already says — image models frequently add
        # invented logos/text/watermarks to "brand-adjacent" scenes
        # (banking, retail, etc.) even when not asked to. The real
        # logo gets composited on afterward by image_branding.py, so
        # any logo the model draws here would just be a second, wrong
        # one layered under it.
        full_prompt = (
            f"{prompt}\n\n"
            "Do not include any logos, brand names, watermarks, text, "
            "lettering, signage, or labels anywhere in the image. "
            "Photo-realistic scene only, no text overlays of any kind."
        )

        logger.info("IMAGE_GEN | generate | prompt=%r", prompt)

        if not self.api_key:
            logger.error("IMAGE_GEN | KIE_API_KEY not configured")
            raise RuntimeError(
                "kie.ai is not configured. Set the KIE_API_KEY "
                "environment variable."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        body = {
            "model": "nano-banana-pro",
            "input": {
                "prompt": full_prompt,
                "image_input": [],
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "output_format": output_format,
            },
        }

        with httpx.Client(timeout=30.0) as client:

            create_response = client.post(
                self.CREATE_URL,
                json=body,
                headers=headers,
            )
            create_response.raise_for_status()
            create_data = create_response.json()

            if create_data.get("code") != 200:
                logger.error(
                    "IMAGE_GEN | task creation failed | msg=%s",
                    create_data.get("msg"),
                )
                raise RuntimeError(
                    f"kie.ai task creation failed: "
                    f"{create_data.get('msg')}"
                )

            task_id = create_data["data"]["taskId"]

            logger.info("IMAGE_GEN | task created | task_id=%s", task_id)

            deadline = time.monotonic() + self.timeout_seconds

            while time.monotonic() < deadline:

                status_response = client.get(
                    self.STATUS_URL,
                    params={"taskId": task_id},
                    headers=headers,
                )
                status_response.raise_for_status()
                status_data = status_response.json()["data"]

                state = status_data.get("state")

                logger.info(
                    "IMAGE_GEN | polling | task_id=%s | state=%s",
                    task_id, state,
                )

                if state == "success":
                    import json as _json

                    result = _json.loads(status_data["resultJson"])
                    urls = result.get("resultUrls", [])

                    if not urls:
                        logger.error(
                            "IMAGE_GEN | task_id=%s | succeeded but no resultUrls",
                            task_id,
                        )
                        raise RuntimeError(
                            "kie.ai task succeeded but returned no "
                            "resultUrls"
                        )

                    logger.info(
                        "IMAGE_GEN | task_id=%s | success | url=%s",
                        task_id, urls[0],
                    )

                    return urls[0]

                if state == "fail":
                    logger.error(
                        "IMAGE_GEN | task_id=%s | failed | fail_msg=%s | fail_code=%s",
                        task_id, status_data.get("failMsg"), status_data.get("failCode"),
                    )
                    raise RuntimeError(
                        f"kie.ai task failed: "
                        f"{status_data.get('failMsg')} "
                        f"(code={status_data.get('failCode')})"
                    )

                time.sleep(self.poll_interval)

        logger.error(
            "IMAGE_GEN | task_id=%s | timed out after %ss",
            task_id, self.timeout_seconds,
        )

        raise TimeoutError(
            f"kie.ai task {task_id} did not complete within "
            f"{self.timeout_seconds} seconds"
        )