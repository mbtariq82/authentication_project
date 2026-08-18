from decimal import Decimal

from repositories.abstract_account_repository import AbstractAccountRepository
from schemas.account import AccountResponse


class AccountBalanceService:
    def __init__(self, repository: AbstractAccountRepository):
        self.repository = repository

    async def credit(
        self,
        account_id: int,
        amount: Decimal,
    ) -> AccountResponse:
        account = await self.repository.credit(account_id, amount)
        return AccountResponse.model_validate(account)

    async def debit(
        self,
        account_id: int,
        amount: Decimal,
    ) -> AccountResponse:
        account = await self.repository.debit(account_id, amount)
        return AccountResponse.model_validate(account)