from fastapi import APIRouter, Depends

from domain.user import User
from schemas import UserResponse
from dependencies import require_admin

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)

@router.get("/dashboard")
async def get_admin_dashboard() -> None:
    return
    # TODO: Query the actual data for the admin dashboard and return it in the response