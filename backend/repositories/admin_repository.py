from unittest import result

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import UserRow
from models.account import AccountRow
from models.card import CardRow


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[UserRow]:

        result = await self.db.execute(
            select(UserRow)
            .where(UserRow.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_id(
        self,
        user_id: int,
    ) -> UserRow | None:

        result = await self.db.execute(
            select(UserRow).where(UserRow.id == user_id)
        )

        return result.scalar_one_or_none()

    async def save(
        self,
        user: UserRow,
    ) -> UserRow:

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user


class AccountRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_account_number(
        self,
        account_number: str,
    ) -> AccountRow | None:

        result = await self.db.execute(
            select(AccountRow).where(
                AccountRow.account_number == account_number
            )
        )

        return result.scalar_one_or_none()

    async def get_by_user_id(
        self,
        user_id: int,
    ) -> AccountRow | None:

        result = await self.db.execute(
            select(AccountRow).where(
                AccountRow.user_id == user_id
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        account: AccountRow,
    ) -> AccountRow:

        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)

        return account
    
    async def list_accounts(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AccountRow]:

        result = await self.db.execute(
            select(AccountRow)
            .where(AccountRow.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())


class CardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_cards(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CardRow]:

        result = await self.db.execute(
            select(CardRow)
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())