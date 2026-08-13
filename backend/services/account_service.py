from domain.account import Account
from exceptions import (
    AccountAlreadyExistsError,
    AccountNotFoundError,
)
from schemas.account import AccountResponse
from unit_of_work.abstract_account_unit_of_work import AbstractAccountUnitOfWork

class AccountService:
    def __init__(self, unit_of_work: AbstractAccountUnitOfWork):
        self.unit_of_work = unit_of_work

    async def create_account(
        self,
        user_id: int,
    ) -> AccountResponse:
        async with self.unit_of_work as uow:
            existing_account = await self.repository.get_by_user(user_id)
            if existing_account is not None:
                raise AccountAlreadyExistsError()

            account = await self.repository.add(Account(user_id=user_id))
            await uow.commit()
            return AccountResponse.model_validate(account)

    async def get_account(
        self,
        user_id: int,
    ) -> AccountResponse:
        async with self.unit_of_work as uow:
            account = await uow.accounts.get_by_user(user_id)
            if account is None:
                raise AccountNotFoundError()
            return AccountResponse.model_validate(account)
