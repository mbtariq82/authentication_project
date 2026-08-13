from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.users import get_user_repository
from repositories.abstract_user_repository import AbstractUserRepository
from repositories.abstract_card_repository import AbstractCardRepository
from repositories.sqlalchemy_card_repository import SqlAlchemyCardRepository
from services.card_service import CardService

def get_card_repository(session: AsyncSession = Depends(get_db)) -> AbstractCardRepository:
    return SqlAlchemyCardRepository(session)

def get_card_service(card_repository: AbstractCardRepository = Depends(get_card_repository),
                     user_repository: AbstractUserRepository = Depends(get_user_repository)) -> CardService:
    return CardService(card_repository, user_repository)