from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.card import Card
from models.account import AccountRow
from models.card import CardRow
from repositories.abstract_card_repository import AbstractCardRepository

class SqlAlchemyCardRepository(AbstractCardRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_domain(row: CardRow) -> Card:
        return Card(
        id=row.id,
        account_id=row.account_id,
        card_number=row.card_number,
        expiry_date=row.expiry_date,
        cvc = row.cvc,
        status=row.status,
        created_at=row.created_at,
    )

    async def card_number_exists(self, card_number: str) -> bool:
        result = await self.session.execute(
            select(CardRow.id).where(
                CardRow.card_number == card_number
            )
        )

        return result.scalar_one_or_none() is not None

    async def get_account_by_user(self, account_id, user_id):
        result = await self.session.execute(
            select(AccountRow).where(
                AccountRow.id == account_id,
                AccountRow.user_id == user_id
            )
        )        

        return result.scalar_one_or_none()


    async def get_active_or_frozen_card(self, account_id: int, user_id: int) -> Optional[Card]:
        result = await self.session.execute(
            select(CardRow).where(
                CardRow.account_id == account_id,
                CardRow.status.in_(["ACTIVE", "FROZEN"]),
            )
        )

        row = result.scalar_one_or_none()

        if row is None: return None

        return self._to_domain(row)

    async def update_card(self, card: Card) -> Card:
        result = await self.session.execute(
            select(CardRow).where(CardRow.id == card.id)
        )

        row = result.scalar_one()

        row.status = card.status

        await self.session.commit()
        await self.session.refresh(row)

        return self._to_domain(row)

    async def create_card(self, card: Card) -> Card:
        row = CardRow(
            account_id=card.account_id,
            card_number=card.card_number,
            expiry_date=card.expiry_date,
            cvc = card.cvc,
            status=card.status,
        )

        self.session.add(row)

        await self.session.commit()
        await self.session.refresh(row)

        return self._to_domain(row)

    async def get_user_cards(self, account_id, user_id):
        result = await self.session.execute(
            select(CardRow).join(AccountRow, CardRow.account_id == AccountRow.id)
            .where(
                AccountRow.id == account_id,
                AccountRow.user_id == user_id,
                CardRow.status == "ACTIVE"
            )
        )

        row = result.scalar_one_or_none()

        if row is None: 
            return None

        return self._to_domain(row)