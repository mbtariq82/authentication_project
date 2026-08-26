from llm_evaluation.dataset import EVALUATION_DATASET
from llm_evaluation.evaluation import evaluate_chatbot

import math
import random

def sample_dataset(dataset, n: int):
    if n > len(dataset):
        raise ValueError(
            f"Cannot sample {n} questions from a dataset of {len(dataset)} questions."
        )

    return random.sample(dataset, n)

def average(values):
    valid_values = [value for value in values if not math.isnan(value)]
    return sum(valid_values) / len(valid_values) if valid_values else float("nan")

if __name__ == "__main__":
    random.seed(42)
    dataset = sample_dataset(EVALUATION_DATASET, 20)
    result = evaluate_chatbot(dataset)

    faithfulness = average(result["faithfulness"])
    answer_relevancy = average(result["answer_relevancy"])
    context_precision = average(result["context_precision"])
    context_recall = average(result["context_recall"])

    print("\nEvaluation Results")
    print("==================")
    
    print(f"Faithfulness:       {faithfulness:.3f}")
    print(f"Answer Relevancy:   {answer_relevancy:.3f}")
    print(f"Context Precision:  {context_precision:.3f}")
    print(f"Context Recall:     {context_recall:.3f}")