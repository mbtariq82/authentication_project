from typing import TypedDict


class AgentState(TypedDict, total=False):
    question: str
    schema: str
    sql_query: str
    query_result: str
    final_answer: str
    error: str