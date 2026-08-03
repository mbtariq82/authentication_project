from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from repositories.abstract_consultant_repository import AbstractConsultantRepository
from schemas import (
    ConsultantPage, ListConsultantsQuery, UserResponse, RegisterConsultantCommand,
    ConsultantResponse
)
from models import ConsultantRow
from domain.user import User
from domain.consultant import Consultant

class ConsultantService:
    def __init__(
        self, 
        repository: AbstractConsultantRepository,
        session: AsyncSession
    ):
        self.repository = repository
        self.session = session

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

    async def list_unassigned_users(
        self,
    ) -> list[UserResponse]:
        users = await self.repository.list_unassigned_users()
        return [
            UserResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role
            )
            for user in users
        ]

    async def create_consultant(
        self,
        request: RegisterConsultantCommand,
    ) -> ConsultantResponse:
        user = await self.repository.get_user(request.user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )
        existing_consultant = await self.repository.get_by_user_id(
            request.user_id
        )
        if existing_consultant:
            raise HTTPException(
                status_code=409,
                detail="This user is already a consultant",
            )
        consultant = ConsultantRow(
            user_id=request.user_id,
            batch=request.batch,
            placement_status=request.placement_status,
            client=request.client.strip() if request.client else None,
        )
        try:
            await self.repository.add(consultant)
            await self.session.commit()
        except:
            await self.session.rollback()
            raise HTTPException(
                status_code=409,
                detail="This user is already a consultant",
            )
        created_consultant = await self.repository.get_with_user(
            consultant.id
        )
        if not created_consultant:
            raise HTTPException(
                status_code=500,
                detail="Consultant could not be loaded after creation",
            )
        return ConsultantResponse(
            id=created_consultant.id,
            user_id=created_consultant.user_id,
            email=created_consultant.user.email,
            first_name=created_consultant.user.first_name,
            last_name=created_consultant.user.last_name,
            batch=created_consultant.batch,
            placement_status=created_consultant.placement_status,
            client=created_consultant.client,
        )