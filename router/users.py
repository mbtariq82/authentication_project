from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User
from schemas import UserResponse
# from router.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


# @router.get("/me", response_model=UserResponse)
# async def read_current_user(
#     current_user: Annotated[User, Depends(get_current_user)],
#     db: Annotated[AsyncSession, Depends(get_db)],
# ):
#     return current_user
