from sqlalchemy.ext.asyncio import AsyncSession

from repositories.sqlalchemy_card_repository import (
    SqlAlchemyCardRepository,
)

from repositories.sqlalchemy_user_repository import (
    SqlAlchemyUserRepository
)

from unit_of_work.abstract_card_unit_of_work import (
    AbstractCardUnitOfWork,
)


class SqlAlchemyCardUnitOfWork(AbstractCardUnitOfWork):

    def __init__(self, session: AsyncSession):
        self.session = session

        self.card_repository = SqlAlchemyCardRepository(session)
        self.user_repository = SqlAlchemyUserRepository(session)

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()