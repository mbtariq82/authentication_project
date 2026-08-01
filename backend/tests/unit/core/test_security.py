from unittest.mock import patch

import pytest
from fastapi import HTTPException

from security import verify_google_id_token


@patch("security.id_token.verify_oauth2_token")
def test_verify_google_id_token_returns_google_identity(
    mock_verify_oauth2_token,
):
    mock_verify_oauth2_token.return_value = {
        "sub": "google-user-123",
        "email": "user@informationtechconsultants.co.uk",
        "email_verified": True,
    }

    identity = verify_google_id_token("valid-google-token")

    assert identity.subject == "google-user-123"
    assert identity.email == "user@informationtechconsultants.co.uk"
    assert identity.email_verified is True


@patch("security.id_token.verify_oauth2_token")
def test_verify_google_id_token_raises_401_for_invalid_token(
    mock_verify_oauth2_token,
):
    mock_verify_oauth2_token.side_effect = ValueError(
        "Token has wrong audience"
    )

    with pytest.raises(HTTPException) as exc_info:
        verify_google_id_token("invalid-google-token")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid Google ID token"