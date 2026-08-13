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
            loan_id=row.loan_id,
            document_id=row.document_id,
            sort_code=row.sort_code,
            account_number=row.account_number,
            balance=row.balance,
            account_status=row.account_status,
            opened_at=row.opened_at,
            closed_at=row.closed_at,
        )

    async def add(self, account: Account) -> Account:
        row = AccountRow(
            user_id=account.user_id,
            loan_id=account.loan_id,
            document_id=account.document_id,
            sort_code=account.sort_code,
            account_number=account.account_number,
            balance=account.balance,
            account_status=account.account_status,
            closed_at=account.closed_at,
        )
        self.session.add(row)
        await self.session.commit()
        return self._to_domain(row)

    async def get_by_user(self, user_id: int) -> Account | None:
        result = await self.session.execute(
            select(AccountRow).where(AccountRow.user_id == user_id)
        )
        row = result.scalar_one_or_none()
        return self._to_domain(row) if row else None
