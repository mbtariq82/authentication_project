from abc import ABC, abstractmethod

from domain.beneficiary import Beneficiary


class AbstractBeneficiaryRepository(ABC):
    @abstractmethod
    async def add(self, beneficiary: Beneficiary) -> Beneficiary:
        raise NotImplementedError

    @abstractmethod
    async def list_by_user(
        self,
        user_id: int,
        *,
        include_inactive: bool = False,
    ) -> list[Beneficiary]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(
        self,
        beneficiary_id: int,
        user_id: int,
    ) -> Beneficiary | None:
        raise NotImplementedError

    @abstractmethod
    async def update(
        self,
        beneficiary_id: int,
        user_id: int,
        changes: dict[str, object],
    ) -> Beneficiary | None:
        raise NotImplementedError

    @abstractmethod
    async def deactivate(
        self,
        beneficiary_id: int,
        user_id: int,
    ) -> Beneficiary | None:
        raise NotImplementedError
