from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from exceptions import (
    GoogleAccountConflictError,
    GoogleEmailNotVerifiedError,
    InactiveUserError,
    InvalidAccessTokenError,
    InvalidCredentialsError,
    InvalidGoogleTokenError,
    InvalidRefreshTokenError,
    UsernameAlreadyRegisteredError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(UsernameAlreadyRegisteredError)
    async def username_already_registered_handler(
        request: Request,
        exc: UsernameAlreadyRegisteredError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Username already registered"},
        )

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(
        request: Request,
        exc: InvalidCredentialsError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid username or password"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(InvalidAccessTokenError)
    async def invalid_access_token_handler(
        request: Request,
        exc: InvalidAccessTokenError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid or expired access token"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(InvalidRefreshTokenError)
    async def invalid_refresh_token_handler(
        request: Request,
        exc: InvalidRefreshTokenError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid or expired refresh token"},
        )

    @app.exception_handler(InactiveUserError)
    async def inactive_user_handler(
        request: Request,
        exc: InactiveUserError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "User account is inactive"},
        )

    @app.exception_handler(InvalidGoogleTokenError)
    async def invalid_google_token_handler(
        request: Request,
        exc: InvalidGoogleTokenError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid Google identity token"},
        )

    @app.exception_handler(GoogleEmailNotVerifiedError)
    async def google_email_not_verified_handler(
        request: Request,
        exc: GoogleEmailNotVerifiedError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Google email is not verified"},
        )

    @app.exception_handler(GoogleAccountConflictError)
    async def google_account_conflict_handler(
        request: Request,
        exc: GoogleAccountConflictError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Account is linked to another Google identity"},
        )