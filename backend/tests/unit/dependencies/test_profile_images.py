from dependencies import profile_images
from storage.s3_profile_image_storage import S3ProfileImageStorage


def test_s3_storage_uses_regional_virtual_host_addressing(monkeypatch):
    client = object()

    def make_client(service_name, *, region_name, config):
        assert service_name == "s3"
        assert region_name == profile_images.AWS_REGION
        assert config.signature_version == "s3v4"
        assert config.s3 == {"addressing_style": "virtual"}
        return client

    monkeypatch.setattr(
        profile_images,
        "PROFILE_IMAGE_STORAGE_BACKEND",
        "s3",
    )
    monkeypatch.setattr(profile_images.boto3, "client", make_client)
    profile_images.get_profile_image_storage.cache_clear()

    try:
        storage = profile_images.get_profile_image_storage()
    finally:
        profile_images.get_profile_image_storage.cache_clear()

    assert isinstance(storage, S3ProfileImageStorage)
    assert storage.client is client
