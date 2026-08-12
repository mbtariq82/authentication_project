from domain.account import Account
from exceptions import (
    AccountAlreadyExistsError,
    AccountNotFoundError,
)
from repositories.abstract_account_repository import AbstractAccountRepository
from schemas.account import AccountResponse


class AccountService:
    def __init__(self, repository: AbstractAccountRepository):
        self.repository = repository

    async def create_account(
        self,
        user_id: int,
    ) -> AccountResponse:
        existing_account = await self.repository.get_by_user(user_id)
        if existing_account is not None:
            raise AccountAlreadyExistsError()

        account = await self.repository.add(Account(user_id=user_id))
        return AccountResponse.model_validate(account)

    async def get_account(
        self,
        user_id: int,
    ) -> AccountResponse:
        account = await self.repository.get_by_user(user_id)
        if account is None:
            raise AccountNotFoundError()
        return AccountResponse.model_validate(account)
