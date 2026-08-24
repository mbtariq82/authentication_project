
from uuid import UUID

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class PublicChatRequest(ChatRequest):
    guest_session_id: UUID


class ChatResponse(BaseModel):
    answer: str
