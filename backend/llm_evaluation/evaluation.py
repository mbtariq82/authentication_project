import logging
import re
import time

from concurrent.futures import ThreadPoolExecutor, as_completed

from langchain_core.messages import HumanMessage, ToolMessage
from tqdm import tqdm
from datasets import Dataset

from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    context_precision,
    context_recall,
    faithfulness,
)
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    before_sleep_log,
)
from tenacity.wait import wait_base

from openai import RateLimitError

from router.ai_chatbot import get_agent


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Rate-limit retry strategy
# ---------------------------------------------------------

class WaitForRateLimit(wait_base):
    def __init__(self, fallback_min=1, fallback_max=30):
        self.fallback_min = fallback_min
        self.fallback_max = fallback_max

    def __call__(self, retry_state):
        exception = retry_state.outcome.exception()

        if isinstance(exception, RateLimitError):
            response = getattr(exception, "response", None)

            if response is not None:
                retry_after = response.headers.get("retry-after")

                if retry_after:
                    try:
                        return float(retry_after)
                    except ValueError:
                        pass

        # Fallback to exponential backoff
        attempt = retry_state.attempt_number

        return min(
            self.fallback_min * (2 ** (attempt - 1)),
            self.fallback_max,
        )


# ---------------------------------------------------------
# Evaluation LLM
# ---------------------------------------------------------

evaluator_llm = LangchainLLMWrapper(
    ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
    )
)

# ---------------------------------------------------------
# Run chatbot
# ---------------------------------------------------------

def extract_contexts(content: str) -> list[str]:
    parts = re.split(r"\n\n(?=\[\d+\] \(source:)", content)

    contexts = []

    for part in parts:
        if part.strip():
            context = re.sub(
                r"^\[\d+\] \(source:.*?\)\n",
                "",
                part,
            )
            contexts.append(context.strip())

    return contexts

@retry(
    retry=retry_if_exception_type(RateLimitError),
    wait=WaitForRateLimit(),
    stop=stop_after_attempt(5),
    before_sleep=before_sleep_log(
        logger,
        logging.WARNING,
    ),
)
def run_agent(question: str) -> tuple[str, list[str]]:
    agent = get_agent()

    config = {
        "configurable": {
            "thread_id": f"evaluation-{hash(question)}",
        }
    }

    result = agent.invoke(
        {
            "messages": [
                HumanMessage(content=question)
            ]
        },
        config=config,
    )

    messages = result.get("messages", [])

    answer = ""

    if messages:
        answer = messages[-1].content or ""

    contexts = []

    for message in messages:
        if (
            isinstance(message, ToolMessage)
            and message.name == "search_banking_documents"
        ):
            content = message.content or ""

            if content != "No relevant documents were found for this query.":
                contexts.extend(extract_contexts(content))

    return answer, contexts


# ---------------------------------------------------------
# Build evaluation dataset
# ---------------------------------------------------------

def build_evaluation_dataset(dataset):
    rows = []

    def process_item(item):
        question = item["question"]
        reference = item["reference"]

        answer, contexts = run_agent(question)

        return {
            "user_input": question,
            "response": answer,
            "retrieved_contexts": contexts,
            "reference": reference,
        }

    # Number of simultaneous chatbot requests
    max_workers = 2

    with ThreadPoolExecutor(max_workers=max_workers) as executor:

        futures = [
            executor.submit(process_item, item)
            for item in dataset
        ]

        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Running chatbot evaluation",
            unit="question",
        ):
            rows.append(future.result())

    return Dataset.from_list(rows)


# ---------------------------------------------------------
# Ragas evaluation
# ---------------------------------------------------------

def evaluate_chatbot(dataset):
    start = time.perf_counter()

    evaluation_dataset = build_evaluation_dataset(dataset)

    dataset_time = time.perf_counter() - start

    print(f"\nChatbot generation took {dataset_time:.2f} seconds")

    faithfulness.llm = evaluator_llm
    answer_relevancy.llm = evaluator_llm
    context_precision.llm = evaluator_llm
    context_recall.llm = evaluator_llm

    ragas_start = time.perf_counter()

    result = evaluate(
        evaluation_dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ],
    )

    ragas_time = time.perf_counter() - ragas_start

    print(f"Ragas evaluation took {ragas_time:.2f} seconds")

    total_time = time.perf_counter() - start

    print(f"Total evaluation took {total_time:.2f} seconds")


    return result