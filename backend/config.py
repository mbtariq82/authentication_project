import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = ".env"

load_dotenv(BASE_DIR / ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
REDIS_URL = os.getenv("REDIS_URL")
PROFILE_IMAGE_STORAGE_BACKEND = os.getenv(
    "PROFILE_IMAGE_STORAGE_BACKEND",
    "local",
).lower()
PROFILE_IMAGE_LOCAL_DIR = Path(
    os.getenv("PROFILE_IMAGE_LOCAL_DIR", BASE_DIR / "uploads")
).resolve()
PROFILE_IMAGE_URL_PREFIX = os.getenv(
    "PROFILE_IMAGE_URL_PREFIX",
    "/profile-images",
)
PROFILE_IMAGES_BUCKET = os.getenv("PROFILE_IMAGES_BUCKET")
AWS_REGION = os.getenv("AWS_REGION", "eu-west-2")
PROFILE_IMAGE_URL_EXPIRY_SECONDS = int(
    os.getenv("PROFILE_IMAGE_URL_EXPIRY_SECONDS", "3600")
)

if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL environment variable is not set")

if SECRET_KEY is None:
    raise RuntimeError("SECRET_KEY environment variable is not set")

if PROFILE_IMAGE_STORAGE_BACKEND not in {"local", "s3"}:
    raise RuntimeError(
        "PROFILE_IMAGE_STORAGE_BACKEND must be either 'local' or 's3'"
    )

if PROFILE_IMAGE_STORAGE_BACKEND == "s3" and not PROFILE_IMAGES_BUCKET:
    raise RuntimeError(
        "PROFILE_IMAGES_BUCKET must be set when profile image storage uses S3"
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1
REFRESH_TOKEN_EXPIRE_DAYS = 7
