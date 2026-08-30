import io
import logging
import os

import httpx
from PIL import Image

logger = logging.getLogger(__name__)

LOGO_PATH = os.path.join(
    os.path.dirname(__file__),
    "assets",
    "nexa_bank_logo.png",
)

# Where composited post images are saved before being served back out
# via GET /admin/media/{filename}.
#
# IMPORTANT: this must be an absolute path, not a bare relative
# string. A relative path like "generated_media" resolves against
# the process's current working directory — which can silently
# differ between the request that writes the file and a later
# request that reads it (e.g. under `uvicorn --reload` on Windows,
# where a reload can restart the worker with a different cwd). That
# mismatch is exactly what causes a file to save successfully but
# then 404 on GET. Anchoring to this file's own directory avoids it.
_DEFAULT_MEDIA_DIR = os.path.join(os.path.dirname(__file__), "generated_media")
MEDIA_DIR = os.getenv("ADMIN_MEDIA_DIR", _DEFAULT_MEDIA_DIR)


def add_logo_watermark(
    base_image_bytes: bytes,
    corner: str = "bottom-right",
    margin_ratio: float = 0.04,
    logo_width_ratio: float = 0.14,
) -> bytes:
    """
    Composites the actual Nexa Bank logo file onto a generated image,
    so every Instagram post carries identical, pixel-exact branding —
    relying on the image-generation model to redraw the logo from a
    text prompt would never look consistent between posts.

    corner: one of "bottom-right", "bottom-left", "top-right", "top-left"
    logo_width_ratio: logo width as a fraction of the base image width
    margin_ratio: margin from the edge, as a fraction of the base image width

    Returns PNG bytes of the composited image.
    """

    base = Image.open(io.BytesIO(base_image_bytes)).convert("RGBA")
    logo = Image.open(LOGO_PATH).convert("RGBA")

    logo_width = int(base.width * logo_width_ratio)
    logo_height = int(logo.height * (logo_width / logo.width))
    logo = logo.resize((logo_width, logo_height), Image.LANCZOS)

    margin = int(base.width * margin_ratio)

    positions = {
        "bottom-right": (base.width - logo_width - margin, base.height - logo_height - margin),
        "bottom-left": (margin, base.height - logo_height - margin),
        "top-right": (base.width - logo_width - margin, margin),
        "top-left": (margin, margin),
    }

    if corner not in positions:
        raise ValueError(f"Unknown corner: {corner!r}")

    position = positions[corner]

    composited = base.copy()
    composited.paste(logo, position, mask=logo)  # mask=logo preserves alpha transparency

    output = io.BytesIO()
    composited.convert("RGB").save(output, format="PNG")

    return output.getvalue()


def brand_and_save_image(image_url: str) -> str:
    """
    Downloads a generated image from image_url, composites the Nexa
    Bank logo onto it, saves it to MEDIA_DIR, and returns just the
    filename (not the full path) — pair with
    GET /admin/media/{filename} to build a public URL for Zernio to
    fetch when publishing.
    """

    logger.info("IMAGE_BRANDING | downloading base image | url=%s", image_url)

    with httpx.Client(timeout=30.0) as client:
        response = client.get(image_url)
        response.raise_for_status()
        base_image_bytes = response.content

    logger.info("IMAGE_BRANDING | compositing logo")

    branded_bytes = add_logo_watermark(base_image_bytes)

    os.makedirs(MEDIA_DIR, exist_ok=True)

    import uuid
    filename = f"instagram_post_{uuid.uuid4().hex[:12]}.png"
    path = os.path.join(MEDIA_DIR, filename)

    with open(path, "wb") as f:
        f.write(branded_bytes)

    logger.info("IMAGE_BRANDING | saved | path=%s", path)

    return filename