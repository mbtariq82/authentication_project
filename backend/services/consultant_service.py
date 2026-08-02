from repositories.abstract_consultant_repository import AbstractConsultantRepository
from schemas import ConsultantPage, ListConsultantsQuery

class ConsultantService:
    def __init__(self, repository: AbstractConsultantRepository):
        self.repository = repository

    async def list_consultants(
        self,
        query: ListConsultantsQuery,
    ) -> ConsultantPage:
        offset = (query.page - 1) * query.page_size
        consultants, total = await self.repository.list_consultants(
            offset=offset,
            limit=query.page_size,
        )
        return ConsultantPage(
            items=consultants,
            page=query.page,
            page_size=query.page_size,
            total=total,
            total_pages=(total + query.page_size - 1) // query.page_size,
        )