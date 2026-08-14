import random
import string

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from enums import UserStatus, AccountStatus
from models.account import AccountRow
from repositories.admin_repository import (
    UserRepository,
    AccountRepository,
)

import secrets


def generate_account_number(user_id: int) -> str:
    user_part = str(user_id).zfill(3)

    random_part = "".join(
        str(secrets.randbelow(10))
        for _ in range(5)
    )

    return user_part + random_part


def generate_sort_code() -> str:
    return "-".join(
        "".join(random.choices(string.digits, k=2))
        for _ in range(3)
    )


class AdminUserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.account_repo = AccountRepository(db)

    async def get_user(self, user_id: int):
        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return user

    async def generate_unique_account_number(
        self,
        user_id: int,
    ) -> str:
        for _ in range(10):
            account_number = generate_account_number(user_id)

            existing = await self.account_repo.get_by_account_number(
                account_number
            )

            if not existing:
                return account_number

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate unique account number",
        )

    async def update_status(
        self,
        user_id: int,
        new_status: UserStatus,
        rejection_reason: str | None = None,
    ):
        user = await self.get_user(user_id)

        if new_status == UserStatus.REJECTED:
            if not rejection_reason:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rejection reason is required",
                )

            user.rejection_reason = rejection_reason

        else:
            user.rejection_reason = None

        user.status = new_status.value

        # Create account when user is approved
        if new_status == UserStatus.APPROVED:

            existing_account = await self.account_repo.get_by_user_id(
                user_id
            )

            if not existing_account:
                account_number = (
                    await self.generate_unique_account_number()
                )

                account = AccountRow(
                    user_id=user.id,
                    account_number=account_number,
                    sort_code=generate_sort_code(),
                    branch="London",
                    account_type="savings",
                    balance=0,
                    account_status=AccountStatus.APPROVED.value,
                )

                await self.account_repo.create(account)

        await self.user_repo.save(user)

        return user

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
    ):
        return await self.user_repo.list_users(skip, limit)