from datetime import datetime, timezone
# we need this for commiting to the DB but we could remove this by introducing a unit of work
from sqlalchemy.ext.asyncio import AsyncSession 
from jose import JWTError

from models import User
from schemas import (
    RegisterCommand, LoginCommand, LogoutCommand, TokenResponse, RefreshCommand, 
    GoogleLoginCommand
)
from repositories.user_repository import UserRepository
from repositories.refresh_token_repository import RefreshTokenRepository
from security import (
    create_access_token, create_refresh_token, pwd_context, decode_token, 
    verify_google_id_token
)
from exceptions import (
    UsernameAlreadyRegisteredError, InvalidCredentialsError, InvalidRefreshTokenError,
    InvalidGoogleTokenError, GoogleEmailNotVerifiedError, GoogleAccountConflictError
)

class AuthService:
    def __init__(
        self,
        db: AsyncSession,         # commit should be in the service because of atomicity
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
    ):
        self.db = db
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository
 
    async def register(self, command: RegisterCommand) -> TokenResponse:
        existing_user = await self.user_repository.get_by_username(command.username)
        if existing_user:
            raise UsernameAlreadyRegisteredError()
        new_user = User(
            username=command.username,
            hashed_password=pwd_context.hash(command.password),
        )

        try:
            await self.user_repository.add(new_user)
            # Ensures the INSERT runs and new_user.id is populated,
            # without committing the transaction yet.
            token_response = await self._issue_tokens(new_user)
            await self.db.commit()
            return token_response

        except Exception:
            await self.db.rollback()
            raise

    async def login(self, command: LoginCommand) -> TokenResponse:
        user = await self.user_repository.get_by_username(command.username)
        if not user or not pwd_context.verify(command.password, user.hashed_password): # verify should run in a seperate thread and not block the rest of the function
            raise InvalidCredentialsError()

        try:
            token_response = await self._issue_tokens(user)
            await self.db.commit()
            return token_response
        except Exception:
            await self.db.rollback()
            raise
    
    async def refresh(self, command: RefreshCommand) -> TokenResponse:
        try:
            payload = decode_token(command.token)
        except (JWTError, TypeError, ValueError) as exc:
            raise InvalidRefreshTokenError() from exc
        if payload.get("type") != "refresh":
            raise InvalidRefreshTokenError()
        stored_token = await self.refresh_token_repository.get_by_token(command.token)
        if not stored_token or stored_token.expires_at < datetime.now(timezone.utc):
            raise InvalidRefreshTokenError()
        user = await self.user_repository.get_by_id(int(payload.get("sub")))
        if not user:
            raise InvalidRefreshTokenError()
        
        try:
            # Rotation: invalidate the old token before issuing a new one.
            await self.refresh_token_repository.delete(stored_token)
            token_response = await self._issue_tokens(user)
            await self.db.commit()
            return token_response
        except Exception:
            await self.db.rollback()
            raise

    async def logout(self, command: LogoutCommand) -> None:
        stored_token = await self.refresh_token_repository.get_by_token(command.token)
        if not stored_token:
            return
        try:
            await self.refresh_token_repository.delete(stored_token)
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise

    # # change name to get_user_from_access_token
    # async def authenticate(self, access_token: str) -> User:
    #     try:
    #         payload = decode_token(access_token)
    #         token_type = payload.get("type")
    #         subject = payload.get("sub")
    #         user_id = int(subject)
    #     except Exception:
    #         raise

    #     # cache-aside pattern
    #     # user = await self.

    #     user = await self.user_repository.get_by_id(user_id)
    #     if user is None:
    #         raise 
    #     return user
    
    async def google_login(self, command: GoogleLoginCommand) -> TokenResponse:
        google_identity = verify_google_id_token(command.id_token)
        if not google_identity.email_verified:
            raise GoogleEmailNotVerifiedError()

        user = await self.user_repository.get_by_google_subject(
            google_identity.subject
        )
        if not user:
            user = await self.user_repository.get_by_email(
                google_identity.email
            )
        if not user:
            user = User(
                email=google_identity.email,
                google_subject=google_identity.subject
            )
            await self.user_repository.add(user)
        elif user.google_subject is None:
            user.google_subject = google_identity.subject
        
        if (
            user.google_subject is not None
            and user.google_subject != google_identity.subject
        ):
            raise GoogleAccountConflictError()

        token_response = await self._issue_tokens(user)
        await self.db.commit()

        return token_response

    async def _issue_tokens(self, user: User) -> TokenResponse:
        access_token = create_access_token(subject=str(user.id))
        refresh_token, expires_at = create_refresh_token(subject=str(user.id))
        await self.refresh_token_repository.create(
            token=refresh_token,
            user_id=user.id,
            expires_at=expires_at,
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )