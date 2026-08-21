from unittest.mock import MagicMock

from dependencies.card import (
    get_card_uow,
    get_card_repository,
    get_card_service,
)
from repositories.abstract_card_repository import AbstractCardRepository
from repositories.sqlalchemy_card_repository import SqlAlchemyCardRepository
from services.card_service import CardService
from unit_of_work.abstract_card_unit_of_work import AbstractCardUnitOfWork
from unit_of_work.sqlalchemy_card_unit_of_work import SqlAlchemyCardUnitOfWork


class TestGetCardUow:

    def test_returns_sqlalchemy_card_uow(self):
        session = MagicMock()

        uow = get_card_uow(session)

        assert isinstance(uow, SqlAlchemyCardUnitOfWork)
        assert isinstance(uow, AbstractCardUnitOfWork)
        assert uow.session is session


class TestGetCardRepository:

    def test_returns_sqlalchemy_card_repository(self):
        session = MagicMock()

        repository = get_card_repository(session)

        assert isinstance(repository, SqlAlchemyCardRepository)
        assert isinstance(repository, AbstractCardRepository)
        assert repository.session is session


class TestGetCardService:

    def test_returns_card_service(self):
        uow = MagicMock(spec=AbstractCardUnitOfWork)

        service = get_card_service(uow)

        assert isinstance(service, CardService)
        assert service.uow is uow