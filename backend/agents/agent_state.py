from typing import TypedDict, Any


class AgentState(TypedDict, total=False):
    # Request
    question: str

    # Planning
    intent: str
    plan: list[str]

    # SQL
    schema: str
    sql_query: str
    query_result: list[dict[str, Any]]

    # Excel
    excel_required: bool
    excel_path: str

    # Email
    email_required: bool
    email_recipients: list[str]
    email_subject: str
    email_body: str

    # Instagram
    instagram_required: bool
    instagram_caption: str
    instagram_image_url: str

    # Approval
    requires_approval: bool
    approval_id: int
    approved: bool

    # Result
    final_answer: str
    error: str