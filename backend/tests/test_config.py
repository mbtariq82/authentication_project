import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config


def test_google_client_id_is_present():
    assert config.GOOGLE_CLIENT_ID is not None
    assert config.GOOGLE_CLIENT_ID.endswith(".apps.googleusercontent.com")


def test_algorithm_is_set():
    assert config.ALGORITHM == "HS256"