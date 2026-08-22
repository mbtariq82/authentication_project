import os
from functools import lru_cache

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import (
    create_stuff_documents_chain,
)

from dependencies.auth import get_current_user
from domain.user import User
from schemas.ai_chatbot_schema import ChatRequest, ChatResponse


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


# ---------------------------------------------------------
# RAG system prompt
# ---------------------------------------------------------

SYSTEM_PROMPT = """
You are a grounded banking RAG assistant.

Your task is to answer the user's question using ONLY the information
contained in the retrieved context.

Rules:

1. Treat the retrieved context as the only source of truth.

2. Do NOT use outside knowledge to fill in missing information.

3. Do NOT invent:
   - facts
   - names
   - dates
   - numbers
   - banking policies
   - requirements
   - URLs
   - procedures
   - conclusions

4. Every factual claim in your answer must be supported by the
   retrieved context.

5. If the retrieved context does not contain enough information
   to answer the question, respond with:

   "I could not find enough information in the provided knowledge
   base to answer that."

6. If the context contains conflicting information, clearly state
   that there is conflicting information.

7. Do not choose one conflicting statement unless the retrieved
   context provides enough evidence.

8. If the user's question is unrelated to the retrieved documents,
   clearly say that the requested information is not available in
   the knowledge base.

9. Do not make assumptions.

10. Keep the answer clear, concise, and factual.

11. When source metadata is available, mention the source of the
    information.

Before answering, internally verify:

- Is every important statement supported by the context?
- Did I introduce any information not contained in the context?
- Does the answer directly answer the user's question?

If any statement is unsupported, remove it.

Retrieved context:

<context>
{context}
</context>
"""


# ---------------------------------------------------------
# Prompt template
# ---------------------------------------------------------

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            SYSTEM_PROMPT,
        ),
        (
            "human",
            "{input}",
        ),
    ]
)


# ---------------------------------------------------------
# Create RAG chain
# ---------------------------------------------------------

@lru_cache(maxsize=1)
def get_rag_chain():
    """
    Creates the RAG chain once and caches it.

    Flow:
    PDF
      -> text chunks
      -> embeddings
      -> Chroma vector store
      -> retriever
      -> prompt
      -> LLM
    """

    # -----------------------------------------------------
    # Check OpenAI API key
    # -----------------------------------------------------

    openai_api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    if not openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    # -----------------------------------------------------
    # Load PDF
    # -----------------------------------------------------

    pdf_path = "llm_document/card_document.pdf"

    if not os.path.exists(pdf_path):
        raise RuntimeError(
            f"PDF file not found: {pdf_path}"
        )

    pdf_loader = PyPDFLoader(
        pdf_path
    )

    pdf_documents = pdf_loader.load()

    if not pdf_documents:
        raise RuntimeError(
            "No content could be loaded "
            "from the PDF document."
        )

    # -----------------------------------------------------
    # Split document into chunks
    # -----------------------------------------------------

    text_splitter = (
        RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
    )

    document_chunks = (
        text_splitter.split_documents(
            pdf_documents
        )
    )

    if not document_chunks:
        raise RuntimeError(
            "No document chunks were created."
        )

    # -----------------------------------------------------
    # Create embeddings
    # -----------------------------------------------------

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    # -----------------------------------------------------
    # Create Chroma vector database
    # -----------------------------------------------------

    vectorstore = Chroma.from_documents(
        documents=document_chunks,
        embedding=embeddings,
        collection_name=(
            "bank_registration_documents"
        ),
    )

    # -----------------------------------------------------
    # Create retriever
    # -----------------------------------------------------

    retriever = (
        vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 3,
            },
        )
    )

    # -----------------------------------------------------
    # Create LLM
    # -----------------------------------------------------

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
    )

    # -----------------------------------------------------
    # Create question-answer chain
    # -----------------------------------------------------

    question_answering_chain = (
        create_stuff_documents_chain(
            llm=llm,
            prompt=prompt,
        )
    )

    # -----------------------------------------------------
    # Connect Retriever + LLM
    # -----------------------------------------------------

    rag_chain = create_retrieval_chain(
        retriever=retriever,
        combine_docs_chain=(
            question_answering_chain
        ),
    )

    return rag_chain


# ---------------------------------------------------------
# Customer chatbot endpoint
# ---------------------------------------------------------

@router.post(
    "/customer",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
async def customer_chat(
    data: ChatRequest,
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Customer RAG chatbot endpoint.

    The authenticated customer sends a message.

    The message is:
    1. searched against the banking PDF
    2. relevant chunks are retrieved
    3. chunks are provided to the LLM
    4. a grounded answer is returned
    """

    try:

        # ---------------------------------------------
        # Get cached RAG chain
        # ---------------------------------------------

        rag_chain = get_rag_chain()

        # ---------------------------------------------
        # Ask RAG
        # ---------------------------------------------

        response = rag_chain.invoke(
            {
                "input": data.message,
            }
        )

        # ---------------------------------------------
        # Extract final answer
        # ---------------------------------------------

        answer = response.get(
            "answer"
        )

        if not answer:
            return ChatResponse(
                answer=(
                    "I could not find enough "
                    "information in the provided "
                    "knowledge base to answer that."
                )
            )

        return ChatResponse(
            answer=answer
        )

    except RuntimeError as exc:

        print(
            f"RAG configuration error: {exc}"
        )

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=str(exc),
        )

    except Exception as exc:

        print(
            f"RAG chatbot error: {exc}"
        )

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Unable to process chatbot request."
            ),
        )