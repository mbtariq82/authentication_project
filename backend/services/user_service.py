from schemas import UserResponse

from unit_of_work.abstract_user_unit_of_work import AbstractUserUnitOfWork

class UserService:
    def __init__(self, uow: AbstractUserUnitOfWork):
        self.uow = uow

    async def get_by_id(
        self,
        user_id: int,
    ) -> UserResponse | None:
        async with self.uow:
            cached_user = await self.uow.user_cache.get_by_id(user_id)
            if cached_user:
                return UserResponse.model_validate(cached_user)
            user = await self.uow.users.get_by_id(user_id)
            if not user:
                return None
            response = UserResponse.model_validate(user)
            await self.uow.user_cache.set(response)
            return response