from domain.account import Account
from decimal import Decimal
from enums import AccountStatus

# import block:
from exceptions import (
    AccountAlreadyClosedError,
    AccountAlreadyExistsError,
    AccountAlreadyFrozenError,
    AccountBalanceNotZeroError,
    AccountNotFoundError,
    AccountNotFrozenError,
)
from schemas.account import AccountResponse
from unit_of_work.abstract_account_unit_of_work import AbstractAccountUnitOfWork

class AccountService:
    def __init__(self, unit_of_work: AbstractAccountUnitOfWork):
        self.unit_of_work = unit_of_work

    async def get_account(
        self,
        user_id: int,
    ) -> AccountResponse:
        async with self.unit_of_work as uow:
            account = await uow.accounts.get_by_user(user_id)
            if account is None:
                raise AccountNotFoundError()
            return AccountResponse.model_validate(account)

    async def close_account(
        self,
        user_id: int,
        close_reason: str,
    ) -> AccountResponse:
        async with self.unit_of_work as uow:
            account = await uow.accounts.get_by_user(user_id)
            if account is None:
                raise AccountNotFoundError()
            if account.is_deleted:
                raise AccountAlreadyClosedError()
            if account.balance != Decimal("0.00"):
                raise AccountBalanceNotZeroError(
                    "Live money still in account. "
                    "Please transfer before going further."
                )

            closed = await uow.accounts.close(account.id, close_reason)
            await uow.commit()
            return AccountResponse.model_validate(closed)

    async def freeze_account(self, user_id: int) -> AccountResponse:
        async with self.unit_of_work as uow:
            account = await uow.accounts.get_by_user(user_id)
            if account is None:
                raise AccountNotFoundError()
            if account.is_deleted or account.account_status == AccountStatus.CLOSED:
                raise AccountAlreadyClosedError()
            if account.account_status == AccountStatus.FROZEN:
                raise AccountAlreadyFrozenError()

            frozen = await uow.accounts.set_status(
                account.id, AccountStatus.FROZEN.value
            )
            await uow.commit()
            return AccountResponse.model_validate(frozen)

    async def unfreeze_account(self, user_id: int) -> AccountResponse:
        async with self.unit_of_work as uow:
            account = await uow.accounts.get_by_user(user_id)
            if account is None:
                raise AccountNotFoundError()
            if account.account_status != AccountStatus.FROZEN:
                raise AccountNotFrozenError()

            approved = await uow.accounts.set_status(
                account.id, AccountStatus.APPROVED.value
            )
            await uow.commit()
            return AccountResponse.model_validate(approved)