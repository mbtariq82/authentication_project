from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import UserRow
from models.account import AccountRow


class SearchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_customers(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[tuple[UserRow, AccountRow | None]]:
        result = await self.db.execute(
            select(
                UserRow,
                AccountRow,
            )
            .outerjoin(
                AccountRow,
                AccountRow.user_id == UserRow.id,
            )
            .where(
                UserRow.is_deleted == False
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.all())

    async def get_customer_by_id(
        self,
        user_id: int,
    ) -> tuple[UserRow, AccountRow | None] | None:
        result = await self.db.execute(
            select(
                UserRow,
                AccountRow,
            )
            .outerjoin(
                AccountRow,
                AccountRow.user_id == UserRow.id,
            )
            .where(
                UserRow.id == user_id,
                UserRow.is_deleted == False,
            )
        )

        return result.first()