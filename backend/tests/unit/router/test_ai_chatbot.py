from dataclasses import dataclass
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient

from dependencies.auth import get_current_user
from dependencies.rate_limiting import get_public_chat_rate_limiter
from enums import Role
import router.ai_chatbot as ai_chatbot
from schemas.user import UserResponse


class FakeAgent:
    def __init__(self) -> None:
        self.thread_ids: list[str] = []

    def invoke(self, _input: object, config: dict) -> dict:
        thread_id = config["configurable"]["thread_id"]
        self.thread_ids.append(thread_id)
        return {"messages": [SimpleNamespace(content=f"Answer for {thread_id}")]}


class FakeRateLimiter:
    def __init__(self, is_limited: bool = False) -> None:
        self.is_limited = is_limited
        self.identifiers: list[str] = []

    async def check(self, identifier: str) -> None:
        self.identifiers.append(identifier)
        if self.is_limited:
            raise HTTPException(
                status_code=429,
                detail="Too many chat requests. Please try again later.",
                headers={"Retry-After": "60"},
            )


@dataclass
class TestDocument:
    page_content: str
    metadata: dict[str, str]


def make_app(agent: FakeAgent, limiter: FakeRateLimiter) -> FastAPI:
    app = FastAPI()
    app.include_router(ai_chatbot.router)
    app.dependency_overrides[get_public_chat_rate_limiter] = lambda: limiter
    app.dependency_overrides[get_current_user] = lambda: UserResponse(
        id=7,
        email="customer@example.com",
        first_name="Amina",
        last_name="Khan",
        role=Role.USER,
    )
    return app


@pytest.mark.asyncio
async def test_public_chat_keeps_guest_conversations_isolated(monkeypatch):
    agent = FakeAgent()
    limiter = FakeRateLimiter()
    monkeypatch.setattr(ai_chatbot, "get_agent", lambda: agent)
    transport = ASGITransport(app=make_app(agent, limiter))
    first_guest = uuid4()
    second_guest = uuid4()

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        first_response = await client.post(
            "/chatbot/public",
            json={"message": "Why is my transaction pending?", "guest_session_id": str(first_guest)},
        )
        second_response = await client.post(
            "/chatbot/public",
            json={"message": "Why is my transaction pending?", "guest_session_id": str(second_guest)},
        )

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert agent.thread_ids == [f"guest:{first_guest}", f"guest:{second_guest}"]
    assert limiter.identifiers[0] != limiter.identifiers[1]


@pytest.mark.asyncio
async def test_public_chat_returns_rate_limit_response(monkeypatch):
    agent = FakeAgent()
    limiter = FakeRateLimiter(is_limited=True)
    monkeypatch.setattr(ai_chatbot, "get_agent", lambda: agent)
    transport = ASGITransport(app=make_app(agent, limiter))

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/chatbot/public",
            json={"message": "Hello", "guest_session_id": str(uuid4())},
        )

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "60"
    assert agent.thread_ids == []


@pytest.mark.asyncio
async def test_authenticated_chat_uses_the_customer_thread(monkeypatch):
    agent = FakeAgent()
    monkeypatch.setattr(ai_chatbot, "get_agent", lambda: agent)
    transport = ASGITransport(app=make_app(agent, FakeRateLimiter()))

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/chatbot/customer",
            json={"message": "Why is my transaction pending?"},
        )

    assert response.status_code == 200
    assert response.json() == {"answer": "Answer for 7"}
    assert agent.thread_ids == ["7"]


def test_retriever_indexes_the_transactions_document(monkeypatch):
    loaded_paths: list[str] = []
    indexed_documents: list[TestDocument] = []

    class FakeLoader:
        def __init__(self, path: str) -> None:
            self.path = path

        def load(self) -> list[TestDocument]:
            loaded_paths.append(self.path)
            return [TestDocument(page_content=self.path, metadata={})]

    class FakeSplitter:
        def split_documents(
            self,
            documents: list[TestDocument],
        ) -> list[TestDocument]:
            return documents

    class FakeVectorStore:
        def as_retriever(self, **_kwargs: object) -> object:
            return object()

    def capture_documents(
        *,
        documents: list[TestDocument],
        **_kwargs: object,
    ) -> FakeVectorStore:
        indexed_documents.extend(documents)
        return FakeVectorStore()

    ai_chatbot.get_retriever.cache_clear()
    monkeypatch.setattr(
        ai_chatbot.glob,
        "glob",
        lambda _pattern: ["llm_document/card_document.pdf", "llm_document/transactions_document.pdf"],
    )
    monkeypatch.setattr(ai_chatbot, "PyPDFLoader", FakeLoader)
    monkeypatch.setattr(ai_chatbot, "RecursiveCharacterTextSplitter", lambda **_kwargs: FakeSplitter())
    monkeypatch.setattr(ai_chatbot, "OpenAIEmbeddings", lambda **_kwargs: object())
    monkeypatch.setattr(
        ai_chatbot.Chroma,
        "from_documents",
        staticmethod(capture_documents),
    )
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    ai_chatbot.get_retriever()
    ai_chatbot.get_retriever.cache_clear()

    assert "llm_document/transactions_document.pdf" in loaded_paths
    assert [document.page_content for document in indexed_documents] == loaded_paths