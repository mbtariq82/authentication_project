from uuid import uuid4

import pytest
from pydantic import ValidationError

from schemas.ai_chatbot_schema import ChatRequest, PublicChatRequest


def test_chat_request_strips_message_whitespace():
    request = ChatRequest(message="  Why is my transaction pending?  ")

    assert request.message == "Why is my transaction pending?"


@pytest.mark.parametrize("message", ["", "   ", "x" * 2001])
def test_chat_request_rejects_invalid_message(message: str):
    with pytest.raises(ValidationError):
        ChatRequest(message=message)


def test_public_chat_request_requires_a_valid_guest_session_id():
    request = PublicChatRequest(
        message="Hello",
        guest_session_id=uuid4(),
    )

    assert request.guest_session_id