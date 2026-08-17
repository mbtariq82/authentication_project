from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.users import get_user_repository
from repositories.abstract_user_repository import AbstractUserRepository
from repositories.abstract_card_repository import AbstractCardRepository
from repositories.sqlalchemy_card_repository import SqlAlchemyCardRepository
from services.card_service import CardService
from unit_of_work.abstract_card_unit_of_work import AbstractCardUnitOfWork
from unit_of_work.sqlalchemy_card_unit_of_work import SqlAlchemyCardUnitOfWork

def get_card_uow(
        session: AsyncSession = Depends(get_db)
) -> AbstractCardUnitOfWork:
    return SqlAlchemyCardUnitOfWork(session)

def get_card_repository(session: AsyncSession = Depends(get_db)) -> AbstractCardRepository:
    return SqlAlchemyCardRepository(session)

def get_card_service(uow: AbstractCardUnitOfWork = Depends(get_card_uow)) -> CardService:
    return CardService(uow)