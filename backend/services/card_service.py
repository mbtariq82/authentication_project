import secrets
import asyncio
from datetime import datetime, timedelta, timezone
from repositories.abstract_card_repository import AbstractCardRepository
from repositories.abstract_user_repository import AbstractUserRepository
from schemas.card import CardResponse, CardDetailsResponse
from domain.card import Card
from exceptions import AccountNotFoundError, CardNotFoundError, InvalidCredentialsError
from security import pwd_context

class CardService:

    def __init__(self, card_repository: AbstractCardRepository, user_repository: AbstractUserRepository):
        self.card_repository = card_repository
        self.user_repository = user_repository

    def _generate_cvc(self) -> str:
        return "".join(str(secrets.randbelow(10)) for _ in range(3))

    def _generate_card_number(self) -> str:
        prefix = secrets.choice([
            str(secrets.randbelow(5) + 51),
            str(secrets.randbelow(500) + 2221),
        ])

        digits = prefix + "".join(
            str(secrets.randbelow(10))
            for _ in range(15 - len(prefix))
        )

        total = 0

        for i, digit in enumerate(digits):
            value = int(digit)

            if i % 2 == 0:
                value *= 2

                if value > 9:
                    value -= 9

            total += value

        check_digit = (10 - (total % 10)) % 10

        return digits + str(check_digit)

    async def _generate_unique_card_number(self):
        while True:
            card_number = self._generate_card_number()

            if not await self.card_repository.card_number_exists(card_number):
                return card_number

    async def create_card(self, account_id, user_id):
        account = await self.card_repository.get_account_by_user(
            account_id,
            user_id,
        )

        if account is None:
            raise AccountNotFoundError()

        existing_card = await self.card_repository.get_active_or_frozen_card(account.id, user_id)

        if existing_card is not None:
            existing_card.status = "CANCELLED"

            await self.card_repository.update_card(existing_card)

        card_number = await self._generate_unique_card_number()
        expiry_date = datetime.now(timezone.utc) + timedelta(days=365 * 3)

        card = await self.card_repository.create_card(Card(
            account_id=account.id,
            card_number=card_number,
            expiry_date=expiry_date,
            cvc = self._generate_cvc(),
            status="ACTIVE"
        ))

        return CardResponse.model_validate(card)


    def _mask_card_number(self, card_number: str) -> str:
        return "*" * (len(card_number) - 4) + card_number[-4:]

    def _mask_cvc(self, cvc: str) -> str:
        return "***"

    async def _get_user_card(self, account_id: int, user_id: int) -> Card:

        card = await self.card_repository.get_user_cards(
            account_id,
            user_id,
        )

        if card is None:
            raise CardNotFoundError()

        return card

    async def get_user_card(self, account_id: int, user_id: int) -> CardResponse:

        card = await self._get_user_card(
            account_id,
            user_id,
        )

        return CardDetailsResponse(
            card_number=self._mask_card_number(card.card_number),
            expiry_date=card.expiry_date,
            cvc=self._mask_cvc(card.cvc)
        )

    async def get_unmasked_card(self, account_id: int, email: str, password: str) -> CardDetailsResponse:

        user = await self.user_repository.get_by_email(email)

        if user is None:
            raise InvalidCredentialsError()
        card = await self._get_user_card(
            account_id,
            user.id,
        )

        if not await asyncio.to_thread(
            pwd_context.verify, 
            password, 
            user.hashed_password
        ):
            raise InvalidCredentialsError


        return CardDetailsResponse(
            card_number=card.card_number,
            expiry_date=card.expiry_date,
            cvc=card.cvc,
        )
        