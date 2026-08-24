from typing import TypedDict, Any


class AgentState(TypedDict, total=False):
    question: str
    schema: str
    sql_query: str
    query_result: list[dict[str, Any]]
    final_answer: str
    error: str