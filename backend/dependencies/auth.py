from fastapi import Depends
from jose import JWTError

from database import async_session_factory
from dependencies.accounts import get_account_service
from dependencies.profile_images import get_profile_image_storage
from dependencies.users import get_user_service
from domain.card import AuthenticatedUserContext
from enums import Role
from exceptions import (
    AccountNotFoundError,
    InvalidAccessTokenError,
    PermissionDeniedError,
)
from messaging.kafka_producer import EventPublisher, KafkaEventPublisher
from schemas.user import UserResponse
from security import decode_token, oauth2_scheme
from services.auth_service import AuthService
from services.account_service import AccountService
from services.user_service import UserService
from storage.abstract_profile_image_storage import AbstractProfileImageStorage
from unit_of_work.sqlalchemy_auth_unit_of_work import SqlAlchemyAuthUnitOfWork


_kafka_event_publisher: KafkaEventPublisher | None = None


def create_kafka_event_publisher() -> KafkaEventPublisher:
    global _kafka_event_publisher
    _kafka_event_publisher = KafkaEventPublisher()
    return _kafka_event_publisher


async def get_kafka_event_publisher() -> EventPublisher:
    if _kafka_event_publisher is None:
        raise RuntimeError("Kafka event publisher has not been started")
    return _kafka_event_publisher


def get_auth_service(
    image_storage: AbstractProfileImageStorage = Depends(
        get_profile_image_storage
    ),
    event_publisher: EventPublisher = Depends(get_kafka_event_publisher),
) -> AuthService:
    unit_of_work = SqlAlchemyAuthUnitOfWork(async_session_factory)
    return AuthService(unit_of_work, image_storage, event_publisher)


async def get_current_user(
    access_token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    try:
        payload = decode_token(access_token)
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError) as exc:
        raise InvalidAccessTokenError() from exc
    if payload.get("type") != "access":
        raise InvalidAccessTokenError()
    user = await user_service.get_by_id(user_id)
    if not user:
        raise InvalidAccessTokenError()
    return user


async def require_admin(
    user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    if user.role != Role.ADMIN:
        raise PermissionDeniedError()
    return user

async def get_user_account(
    user: UserResponse = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service),
) -> AuthenticatedUserContext:
    account = await account_service.get_account(user.id)
    if not account:
        raise AccountNotFoundError()
    return AuthenticatedUserContext(
        user=user,
        account=account,
    )

