from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.account import Account
from models.account import AccountRow
from repositories.abstract_account_repository import AbstractAccountRepository


class SqlAlchemyAccountRepository(AbstractAccountRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_domain(row: AccountRow) -> Account:
        return Account(
            id=row.id,
            user_id=row.user_id,
            balance=row.balance,
            created_at=row.created_at,
        )

    async def add(self, account: Account) -> Account:
        row = AccountRow(
            user_id=account.user_id,
            balance=account.balance,
        )
        self.session.add(row)
        await self.session.flush()
        return self._to_domain(row)

    async def get_by_user(self, user_id: int) -> Account | None:
        result = await self.session.execute(
            select(AccountRow).where(AccountRow.user_id == user_id)
        )
        row = result.scalar_one_or_none()
        return self._to_domain(row) if row else None
