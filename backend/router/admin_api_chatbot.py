from fastapi import APIRouter, Depends
from dependencies.auth import require_admin
from schemas.admin_agent_schema import AdminAgentRequest
from dependencies.auth import get_current_user
from agents.admin_sql_agent import AdminSQLAgent
from fastapi.concurrency import run_in_threadpool

from agents.excel_export import excel_streaming_response

router = APIRouter(
    prefix="/admin", 
    tags=["Admin AI"],
    dependencies=[Depends(require_admin)]
)


agent = AdminSQLAgent()


@router.post("/ask")
async def ask_admin_agent(
    request: AdminAgentRequest,
):
    result = await run_in_threadpool(
        agent.query,
        request.question,
    )

    return result


@router.post("/ask/export")
async def export_admin_agent_result(
    request: AdminAgentRequest,
):
    """
    Same flow as /ask, but returns the query result as a
    downloadable .xlsx file instead of JSON. Useful when the admin
    wants to open the result in Excel or share it with someone
    outside the dashboard.
    """

    result = await run_in_threadpool(
        agent.query,
        request.question,
    )

    return excel_streaming_response(
        rows=result.get("rows", []),
        question=result.get("question", request.question),
        sql_query=result.get("sql_query", ""),
        answer=result.get("answer", ""),
        filename_prefix="admin_query_result",
    )