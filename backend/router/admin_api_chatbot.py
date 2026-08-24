from fastapi import APIRouter, Depends
from dependencies.auth import require_admin
from schemas.admin_agent_schema import AdminAgentRequest
from dependencies.auth import get_current_user
from agents.admin_sql_agent import AdminSQLAgent
from fastapi.concurrency import run_in_threadpool

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