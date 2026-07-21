from datetime import datetime, timezone
from fastapi import HTTPException   # ideally this should be replaced with custom handling
from sqlalchemy.ext.asyncio import AsyncSession # we need this for commiting to the DB but we could remove this by introducing a unit of work
from jose import JWTError

from models import User 
from schemas import RegisterCommand, LoginCommand, LogoutCommand, TokenResponse, RefreshCommand, GoogleLoginCommand
from repositories.user_repository import UserRepository
from repositories.refresh_token_repository import RefreshTokenRepository
from security import create_access_token, create_refresh_token, pwd_context, decode_token, verify_google_id_token

class AuthService:
    def __init__(
        self,
        db: AsyncSession,         # commit should be in the service because of atomicity
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository
    ):
        self.db = db
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository
 
    async def register(self, command: RegisterCommand) -> TokenResponse:
        existing_user = await self.user_repository.get_by_username(command.username)
        if existing_user:
            raise HTTPException(
                status_code=409, 
                detail="Username already registered"
            )
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
        if not user or not pwd_context.verify(command.password, user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )

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
        except JWTError as exc:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        stored_token = await self.refresh_token_repository.get_by_token(command.token)
        if not stored_token or stored_token.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=401, 
                detail="Refresh token expired or revoked"
            )

        user = await self.user_repository.get_by_id(int(payload.get("sub")))
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

    async def authenticate(self, access_token: str) -> User:
        try:
            payload = decode_token(access_token)
            token_type = payload.get("type")
            subject = payload.get("sub")
            user_id = int(subject)
        except Exception:
            raise

        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise 
        return user
    
    async def google_login(self, command: GoogleLoginCommand) -> TokenResponse:
        google_identity = verify_google_id_token(command.id_token)
        if not google_identity.email_verified:
            raise HTTPException(
                status_code=401,
                detail="Google email is not verified",
        )

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
            user.google_subject = google_claims.subject

        await self.db.commit()

        return await self._issue_tokens(user)

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