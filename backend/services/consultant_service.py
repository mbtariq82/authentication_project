from repositories.abstract_consultant_repository import AbstractConsultantRepository
from schemas import ConsultantPage

class ConsultantService:
    def __init__(self, repository: AbstractConsultantRepository):
        self.repository = repository

    async def list_consultants(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> ConsultantPage:
        offset = (page - 1) * page_size
        consultants, total = await self.repository.list_consultants(
            offset=offset,
            limit=page_size,
        )
        return ConsultantPage(
            items=consultants,
            page=page,
            page_size=page_size,
            total=total,
            total_pages=(total + page_size - 1) // page_size,
        )