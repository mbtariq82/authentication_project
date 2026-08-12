from datetime import datetime, timezone
from jose import JWTError

from domain.user import User

from schemas.auth import (
    RegisterCommand, LoginCommand, LogoutCommand, TokenResponse, RefreshCommand, 
    GoogleLoginCommand
)
from security import (
    create_access_token, create_refresh_token, pwd_context, decode_token, 
    verify_google_id_token
)
from exceptions import (
    EmailAlreadyRegisteredError, InvalidCredentialsError, InvalidRefreshTokenError,
    GoogleEmailNotVerifiedError, InvalidCompanyEmailError
)
from unit_of_work.abstract_auth_unit_of_work import AbstractAuthUnitOfWork

class AuthService:
    def __init__(self, uow: AbstractAuthUnitOfWork):  
        self.uow = uow
 
    async def register(self, command: RegisterCommand) -> TokenResponse:
        async with self.uow:
            existing_user = await self.uow.users.get_by_email(command.email)
            if existing_user:
                raise EmailAlreadyRegisteredError()
            new_user = User(
                first_name=command.first_name,
                last_name=command.last_name,
                email=command.email,
                hashed_password=pwd_context.hash(command.password),
            )
            new_user =await self.uow.users.add(new_user)
            token_response = await self._issue_tokens(new_user)
            await self.uow.commit()
            return token_response

    async def login(self, command: LoginCommand) -> TokenResponse:
        async with self.uow:
            user = await self.uow.users.get_by_email(command.email)
            if (
                not user
                or not user.hashed_password
                or not pwd_context.verify(command.password, user.hashed_password)
            ): # verify should run in a separate thread and not block the rest of the function
                raise InvalidCredentialsError()
            token_response = await self._issue_tokens(user)
            await self.uow.commit()
            return token_response
    
    async def refresh(self, command: RefreshCommand) -> TokenResponse:
        try:
            payload = decode_token(command.token)
            if payload.get("type") != "refresh":
                raise InvalidRefreshTokenError()
            subject = payload.get("sub")
            if subject is None:
                raise InvalidRefreshTokenError()
            user_id = int(subject)
        except (JWTError, TypeError, ValueError) as exc:
            raise InvalidRefreshTokenError() from exc
        async with self.uow:
            stored_token = await self.uow.refresh_tokens.get_by_token(
                command.token
            )
            if (
                stored_token is None
                or stored_token.expires_at < datetime.now(timezone.utc)
            ):
                raise InvalidRefreshTokenError()
            user = await self.uow.users.get_by_id(user_id)
            if user is None:
                raise InvalidRefreshTokenError()
            await self.uow.refresh_tokens.delete(stored_token)
            token_response = await self._issue_tokens(user)
            await self.uow.commit()
            return token_response

    async def logout(self, command: LogoutCommand) -> None:
        async with self.uow:
            stored_token = await self.uow.refresh_tokens.get_by_token(command.token)
            if not stored_token:
                return
            await self.uow.refresh_tokens.delete(stored_token)
            await self.uow.commit()

    async def google_login(self, command: GoogleLoginCommand) -> TokenResponse:
        google_identity = verify_google_id_token(command.id_token)
        email = google_identity.email.strip().lower()
        if not email.endswith("@informationtechconsultants.co.uk"):
            raise InvalidCompanyEmailError()
        if not google_identity.email_verified:
            raise GoogleEmailNotVerifiedError()
        async with self.uow:
            user = await self.uow.users.get_by_email(email)
            if not user:
                email_name = email.partition("@")[0]
                user = User(
                    email=email,
                    first_name=google_identity.first_name or email_name,
                    last_name=google_identity.last_name or "",
                )
                user = await self.uow.users.add(user)
            token_response = await self._issue_tokens(user)
            await self.uow.commit()
            return token_response

    async def _issue_tokens(self, user: User) -> TokenResponse:
        access_token = create_access_token(subject=str(user.id))
        refresh_token, expires_at = create_refresh_token(subject=str(user.id))
        await self.uow.refresh_tokens.add(
            token=refresh_token,
            user_id=user.id,
            expires_at=expires_at
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
