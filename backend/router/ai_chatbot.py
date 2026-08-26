import glob
import json
import os
import glob
from functools import lru_cache

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request, status

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from dependencies.auth import get_current_user
from dependencies.rate_limiting import get_public_chat_rate_limiter
from domain.user import User
from rate_limiting.chat_rate_limiter import PublicChatRateLimiter
from schemas.ai_chatbot_schema import ChatRequest, ChatResponse, PublicChatRequest


# ---------------------------------------------------------
# Environment variables
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# Router
# ---------------------------------------------------------

router = APIRouter(
    prefix="/chatbot",
    tags=["Customer Chatbot"],
)


NOT_FOUND_MESSAGE = (
    "I could not find enough information in the provided knowledge "
    "base to answer that."
)

NO_RESULTS_TOOL_OUTPUT = "No relevant documents were found for this query."


# ---------------------------------------------------------
# Agent system prompt
# ---------------------------------------------------------
# Same grounding rules as before, now framed as instructions
# for an agent that DECIDES when to call the retrieval tool,
# rather than a chain that always retrieves first.

SYSTEM_PROMPT = f"""
You are a grounded banking assistant with access to a document
search tool called `search_banking_documents`.

Routing rules:

1. If the user's message is a greeting, small talk, or does not
   require factual banking information (e.g. "hi", "thanks",
   "what can you help with?"), respond directly WITHOUT calling
   the search tool.

2. If the user's question requires factual information about
   banking products, cards, fees, policies, or procedures, you
   MUST call `search_banking_documents` before answering. Do not
   answer from memory or general knowledge.

3. You may call the tool more than once if the first search does
   not return enough information to answer confidently.

Grounding rules (apply whenever you use retrieved context):

1. Treat the retrieved context as the only source of truth for
   factual claims.

2. Do NOT use outside knowledge to fill in missing information.

3. Do NOT invent facts, names, dates, numbers, banking policies,
   requirements, URLs, procedures, or conclusions.

4. Every factual claim in your answer must be supported by the
   retrieved context.

5. If the retrieved context does not contain enough information
   to answer the question, respond with EXACTLY this message and
   nothing else — no elaboration, no apology, no suggestions to
   "contact the bank" or "visit the website," and no phone
   numbers, emails, or URLs, since none of that is present in the
   retrieved context and you cannot verify it is accurate:

   "{NOT_FOUND_MESSAGE}"

6. If the tool result contains conflicting information, clearly
   state that there is conflicting information rather than
   picking one side.

7. If the user's question is unrelated to banking documents and
   the tool returns nothing relevant, clearly say that the
   requested information is not available in the knowledge base.

8. Keep answers clear, concise, and factual.

9. When source metadata is available in the tool result, mention
   the source of the information.

Before answering, internally verify:
- Did I need to search, and did I search if so?
- Is every important statement supported by the retrieved context?
- Did I introduce any information not contained in the context?
- Does the answer directly answer the user's question?

If any statement is unsupported, remove it.
"""


# ---------------------------------------------------------
# Retrieval tool (wraps the old RAG chain's retriever)
# ---------------------------------------------------------

@lru_cache(maxsize=1)
def get_retriever():
    """
    Builds the Chroma retriever once and caches it.

    Loads every .pdf file found in the `llm_document/` directory
    (not just one file), so you can add more banking documents by
    dropping additional PDFs into that folder.

    Flow:
    PDFs -> text chunks -> embeddings -> Chroma vector store -> retriever
    """

    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    pdf_dir = "llm_document"
    pdf_paths = sorted(glob.glob(os.path.join(pdf_dir, "*.pdf")))

    if not pdf_paths:
        raise RuntimeError(f"No PDF files found in: {pdf_dir}")

    pdf_documents = []
    for pdf_path in pdf_paths:
        try:
            pdf_documents.extend(PyPDFLoader(pdf_path).load())
        except Exception as exc:
            print(f"Skipping unreadable PDF '{pdf_path}': {exc}")

    if not pdf_documents:
        raise RuntimeError("No content could be loaded from any PDF document.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    document_chunks = text_splitter.split_documents(pdf_documents)

    if not document_chunks:
        raise RuntimeError("No document chunks were created.")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vectorstore = Chroma.from_documents(
        documents=document_chunks,
        embedding=embeddings,
        collection_name="bank_documents",
    )

    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3},
    )


@tool
def search_banking_documents(query: str) -> str:
    """
    Search the bank's document knowledge base
    for information relevant to the query. Use this whenever the
    user asks a factual question about banking products, cards,
    fees, policies, or procedures. Returns the top matching
    passages along with their source page metadata.
    """

    retriever = get_retriever()
    results = retriever.invoke(query)

    if not results:
        return NO_RESULTS_TOOL_OUTPUT

    formatted = []
    for i, doc in enumerate(results, start=1):
        source = doc.metadata.get("source", "unknown source")
        page = doc.metadata.get("page")
        location = f"{source}" + (f", page {page}" if page is not None else "")
        formatted.append(f"[{i}] (source: {location})\n{doc.page_content}")

    return "\n\n".join(formatted)


# ---------------------------------------------------------
# Create the agent (cached singleton, same lifecycle as the
# old RAG chain). MemorySaver holds conversation state
# in-process only — it resets whenever the app restarts.
# ---------------------------------------------------------

@lru_cache(maxsize=1)
def get_agent():
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,  # deterministic answers for factual questions
    )

    checkpointer = MemorySaver()

    agent = create_react_agent(
        model=llm,
        tools=[search_banking_documents],
        prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )

    return agent


# ---------------------------------------------------------
# Deterministic guard against ungrounded elaboration
# ---------------------------------------------------------
# The prompt asks the LLM to reply with an exact fixed message
# when nothing relevant was found, but prompts aren't guarantees
# — models sometimes pad a correct "not found" with unverified
# extras ("try the website", "call support"). Rather than trust
# wording alone, check what the tool actually returned and force
# the canonical message when every search came back empty.

def _search_found_nothing(messages: list) -> bool:
    """
    True only if search_banking_documents was called at least once
    AND every call came back empty. If the tool was never called
    (e.g. the user just said "hi"), this returns False — there's
    nothing to override, the LLM's direct reply stands.
    """

    tool_messages = [
        message
        for message in messages
        if isinstance(message, ToolMessage)
        and message.name == "search_banking_documents"
    ]

    if not tool_messages:
        return False

    def _normalize_tool_content(content):
        if isinstance(content, list):
            normalized_parts = []
            for item in content:
                if isinstance(item, str):
                    normalized_parts.append(item)
                elif isinstance(item, dict):
                    normalized_parts.append(json.dumps(item, default=str))
                else:
                    normalized_parts.append(str(item))
            return " ".join(normalized_parts)
        return str(content or "")

    return all(
        _normalize_tool_content(message.content).strip() == NO_RESULTS_TOOL_OUTPUT
        for message in tool_messages
    )


# ---------------------------------------------------------
# Customer chatbot endpoint
# ---------------------------------------------------------

@router.post(
    "/public",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
async def public_chat(
    data: PublicChatRequest,
    request: Request,
    rate_limiter: PublicChatRateLimiter = Depends(get_public_chat_rate_limiter),
):
    """Public banking agent endpoint without user authentication."""

    try:
        client_ip = request.client.host if request.client else "unknown"
        await rate_limiter.check(f"{client_ip}:{data.guest_session_id}")

        agent = get_agent()
        config: RunnableConfig = {
            "configurable": {"thread_id": f"guest:{data.guest_session_id}"}
        }

        result = agent.invoke(
            {"messages": [HumanMessage(content=data.message)]},
            config=config,
        )

        messages = result.get("messages", [])
        answer = messages[-1].content if messages else None

        if not answer:
            return ChatResponse(
                answer=(
                    "I could not find enough information in the "
                    "provided knowledge base to answer that."
                )
            )

        return ChatResponse(answer=answer)

    except HTTPException:
        raise

    except RuntimeError as exc:
        print(f"Agent configuration error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process chatbot request.",
        )

    except Exception as exc:
        print(f"Agent chatbot error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process chatbot request.",
        )


@router.post(
    "/customer",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
async def customer_chat(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Customer banking agent endpoint.

    This agent decides per-message whether it needs to search the
    banking document knowledge base, and keeps a running
    conversation per user via an in-memory checkpointer
    (thread_id = user id).
    """

    try:
        agent = get_agent()

        # thread_id scopes memory per user; swap for a session id
        # if you want separate memory per conversation/tab instead.
        config: RunnableConfig = {
            "configurable": {"thread_id": str(current_user.id)}
        }

        result = agent.invoke(
            {"messages": [HumanMessage(content=data.message)]},
            config=config,
        )

        messages = result.get("messages", [])

        if not messages:
            return ChatResponse(answer=NOT_FOUND_MESSAGE)

        answer = messages[-1].content

        if not answer:
            return ChatResponse(answer=NOT_FOUND_MESSAGE)

        # Override ungrounded elaboration: if every search came back
        # empty, ignore whatever extra text the LLM added and return
        # exactly the canonical fallback message instead.
        if _search_found_nothing(messages):
            answer = NOT_FOUND_MESSAGE

        return ChatResponse(answer=answer)

    except RuntimeError as exc:
        print(f"Agent configuration error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    except Exception as exc:
        print(f"Agent chatbot error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process chatbot request.",
        )