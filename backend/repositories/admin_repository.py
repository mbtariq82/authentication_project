from unittest import result

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.loan import LoanRow
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
    ):
        stmt = (
            select(AccountRow, UserRow)
            .join(
                UserRow,
                AccountRow.user_id == UserRow.id,
            )
            .where(AccountRow.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)

        rows = result.all()
        return [
            {
                "id": account.id,
                "user_id": account.user_id,
                "sort_code": account.sort_code,
                "branch": account.branch,
                "account_type": account.account_type,
                "account_number": account.account_number,
                "balance": account.balance,
                "account_status": account.account_status,
                "is_deleted": account.is_deleted,
                "close_reason": account.close_reason,
                "closed_at": account.closed_at,
                "created_at": account.created_at,
                "updated_at": account.updated_at,

                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            }
            for account, user in rows
        ]
    async def get_by_id(
        self,
        account_id: int,
    ):
        result = await self.db.execute(
            select(AccountRow).where(
                AccountRow.id == account_id
            )
        )

        return result.scalar_one_or_none()


    async def save(
        self,
        account: AccountRow,
    ):
        self.db.add(account)
        await self.db.flush()
        await self.db.refresh(account)

        return account





class CardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_cards(
        self,
        skip: int = 0,
        limit: int = 100,
    ):
        stmt = (
            select(CardRow, AccountRow, UserRow)
            .join(
                AccountRow,
                CardRow.account_id == AccountRow.id,
            )
            .join(
                UserRow,
                AccountRow.user_id == UserRow.id,
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)

        rows = result.all()

        return [
            {
                "id": card.id,
                "account_id": card.account_id,
                "card_number": card.card_number,
                "cvc": card.cvc,
                "expiry_date": card.expiry_date,
                "status": card.status,
                "created_at": card.created_at,

                "user_id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            }
            for card, account, user in rows
        ]
    async def get_by_account_id(
        self,
        account_id: int,
    ):
        result = await self.db.execute(
            select(CardRow).where(
                CardRow.account_id == account_id
            )
        )

        return result.scalar_one_or_none()

    async def save(
        self,
        card: CardRow,
    ):
        self.db.add(card)
        await self.db.flush()
        await self.db.refresh(card)

        return card

    async def get_by_id(self, card_id: int):
        result = await self.db.execute(
            select(CardRow).where(
                CardRow.id == card_id
            )
        )

        return result.scalar_one_or_none()




class LoanRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_loans(
        self,
        skip: int = 0,
        limit: int = 100,
    ):
        stmt = (
            select(
                LoanRow,
                AccountRow,
                UserRow,
            )
            .join(
                AccountRow,
                LoanRow.account_id == AccountRow.id,
            )
            .join(
                UserRow,
                AccountRow.user_id == UserRow.id,
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)

        rows = result.all()

        return [
            {
                "id": loan.id,
                "loan_type": loan.loan_type,
                "loan_amount": loan.loan_amount,
                "duration": loan.duration,
                "interest": loan.interest,
                "emi": loan.emi,
                "current_loan_status": loan.current_loan_status,

                "user_id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            }
            for loan, account, user in rows
        ]