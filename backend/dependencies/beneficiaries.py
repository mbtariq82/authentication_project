from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from repositories.abstract_beneficiary_repository import (
    AbstractBeneficiaryRepository,
)
from repositories.sqlalchemy_beneficiary_repository import (
    SqlAlchemyBeneficiaryRepository,
)
from services.beneficiary_service import BeneficiaryService


def get_beneficiary_repository(
    session: AsyncSession = Depends(get_db),
) -> AbstractBeneficiaryRepository:
    return SqlAlchemyBeneficiaryRepository(session)


def get_beneficiary_service(
    repository: AbstractBeneficiaryRepository = Depends(
        get_beneficiary_repository
    ),
) -> BeneficiaryService:
    return BeneficiaryService(repository)