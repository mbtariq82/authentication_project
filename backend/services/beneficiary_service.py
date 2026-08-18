from domain.beneficiary import Beneficiary
from exceptions import (
    BeneficiaryNotFoundError,
    InvalidBeneficiaryUpdateError,
)
from repositories.abstract_beneficiary_repository import (
    AbstractBeneficiaryRepository,
)
from schemas.beneficiary import (
    BeneficiaryCreate,
    BeneficiaryResponse,
    BeneficiaryUpdate,
)


class BeneficiaryService:
    def __init__(self, repository: AbstractBeneficiaryRepository):
        self.repository = repository

    async def create(
        self,
        user_id: int,
        command: BeneficiaryCreate,
    ) -> BeneficiaryResponse:
        beneficiary = await self.repository.add(
            Beneficiary(
                user_id=user_id,
                name=command.name,
                account_number=command.account_number,
                sort_code=command.sort_code,
                bank_name=command.bank_name,
                reference=command.reference,
            )
        )
        return BeneficiaryResponse.model_validate(beneficiary)

    async def list(
        self,
        user_id: int,
        *,
        include_inactive: bool = False,
    ) -> list[BeneficiaryResponse]:
        beneficiaries = await self.repository.list_by_user(
            user_id,
            include_inactive=include_inactive,
        )
        return [
            BeneficiaryResponse.model_validate(beneficiary)
            for beneficiary in beneficiaries
        ]

    async def get(
        self,
        user_id: int,
        beneficiary_id: int,
        *,
        include_inactive: bool = False,
    ) -> BeneficiaryResponse:
        beneficiary = await self.repository.get_by_id(
            beneficiary_id,
            user_id,
        )
        if beneficiary is None or (
            not include_inactive and not beneficiary.is_active
        ):
            raise BeneficiaryNotFoundError()
        return BeneficiaryResponse.model_validate(beneficiary)

    async def update(
        self,
        user_id: int,
        beneficiary_id: int,
        command: BeneficiaryUpdate,
    ) -> BeneficiaryResponse:
        changes = command.model_dump(exclude_unset=True)
        if not changes:
            raise InvalidBeneficiaryUpdateError()

        beneficiary = await self.repository.get_by_id(
            beneficiary_id,
            user_id,
        )
        if beneficiary is None or not beneficiary.is_active:
            raise BeneficiaryNotFoundError()

        updated = await self.repository.update(
            beneficiary_id,
            user_id,
            changes,
        )
        if updated is None:
            raise BeneficiaryNotFoundError()
        return BeneficiaryResponse.model_validate(updated)

    async def deactivate(
        self,
        user_id: int,
        beneficiary_id: int,
    ) -> BeneficiaryResponse:
        beneficiary = await self.repository.get_by_id(
            beneficiary_id,
            user_id,
        )
        if beneficiary is None or not beneficiary.is_active:
            raise BeneficiaryNotFoundError()

        deactivated = await self.repository.deactivate(
            beneficiary_id,
            user_id,
        )
        if deactivated is None:
            raise BeneficiaryNotFoundError()
        return BeneficiaryResponse.model_validate(deactivated)