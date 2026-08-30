import os
import time

import httpx


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

    This is best-effort: callers should catch exceptions and fall
    back to leaving image_url unset, letting the admin attach an
    image manually when approving the post (see
    POST /admin/approve/{id}?image_url=...).
    """

    CREATE_URL = "https://api.kie.ai/api/v1/jobs/createTask"
    STATUS_URL = "https://api.kie.ai/api/v1/jobs/recordInfo"

    def __init__(
        self,
        poll_interval: float = 3.0,
        timeout_seconds: float = 120.0,
    ):
        self.api_key = os.getenv("KIE_API_KEY")
        self.poll_interval = poll_interval
        self.timeout_seconds = timeout_seconds

    def generate(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        resolution: str = "1K",
        output_format: str = "png",
    ) -> str:

        if not self.api_key:
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
                "prompt": prompt,
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
                raise RuntimeError(
                    f"kie.ai task creation failed: "
                    f"{create_data.get('msg')}"
                )

            task_id = create_data["data"]["taskId"]

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

                if state == "success":
                    import json as _json

                    result = _json.loads(status_data["resultJson"])
                    urls = result.get("resultUrls", [])

                    if not urls:
                        raise RuntimeError(
                            "kie.ai task succeeded but returned no "
                            "resultUrls"
                        )

                    return urls[0]

                if state == "fail":
                    raise RuntimeError(
                        f"kie.ai task failed: "
                        f"{status_data.get('failMsg')} "
                        f"(code={status_data.get('failCode')})"
                    )

                time.sleep(self.poll_interval)

        raise TimeoutError(
            f"kie.ai task {task_id} did not complete within "
            f"{self.timeout_seconds} seconds"
        )