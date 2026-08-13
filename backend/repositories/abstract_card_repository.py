from abc import ABC, abstractmethod

from domain.card import Card

class AbstractCardRepository(ABC):
    @abstractmethod
    async def card_number_exists(self, card_number: str) -> bool:
        raise NotImplementedError
    
    @abstractmethod
    async def get_account_by_user(self, account_id: int, user_id: int):
        raise NotImplementedError

    @abstractmethod
    async def get_active_or_frozen_card(self, account_id: int, user_id: int):
        raise NotImplementedError

    @abstractmethod
    async def update_card(self, card: Card):
        raise NotImplementedError

    @abstractmethod
    async def create_card(self, card: Card):
        raise NotImplementedError

    @abstractmethod
    async def get_user_cards(self, account_id: int, user_id: int):
        raise NotImplementedError