import warnings
from io import BytesIO

from PIL import Image
from starlette.datastructures import UploadFile

from exceptions import InvalidProfileImageError, ProfileImageTooLargeError

ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_PROFILE_IMAGE_BYTES = 5 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
OUTPUT_DIMENSIONS = (1024, 1024)


async def read_profile_image(upload: UploadFile) -> bytes:
    try:
        image_bytes = await upload.read(MAX_PROFILE_IMAGE_BYTES + 1)
    finally:
        await upload.close()

    if len(image_bytes) > MAX_PROFILE_IMAGE_BYTES:
        raise ProfileImageTooLargeError()
    return image_bytes


def normalize_profile_image(image_bytes: bytes) -> bytes:
    if not image_bytes:
        raise InvalidProfileImageError("Profile image is empty")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(image_bytes)) as source:
                if source.format not in ALLOWED_IMAGE_FORMATS:
                    raise InvalidProfileImageError(
                        "Profile image must be JPEG, PNG, or WebP"
                    )
                if source.width * source.height > MAX_IMAGE_PIXELS:
                    raise InvalidProfileImageError(
                        "Profile image dimensions are too large"
                    )
                source.verify()

            with Image.open(BytesIO(image_bytes)) as source:
                source.thumbnail(OUTPUT_DIMENSIONS, Image.Resampling.LANCZOS)
                normalized = source.convert("RGB")
                output = BytesIO()
                normalized.save(output, format="WEBP", quality=85, method=6)
                return output.getvalue()
    except InvalidProfileImageError:
        raise
    except (Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise InvalidProfileImageError(
            "Profile image dimensions are too large"
        ) from exc
    except (OSError, ValueError) as exc:
        raise InvalidProfileImageError("Profile image is invalid") from exc
