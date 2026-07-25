from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from exceptions import (
    GoogleAccountConflictError,
    GoogleEmailNotVerifiedError,
    InvalidAccessTokenError,
    InvalidCredentialsError,
    InvalidGoogleTokenError,
    InvalidRefreshTokenError,
    EmailAlreadyRegisteredError,
    InvalidCompanyEmailError,
    PermissionDeniedError
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(EmailAlreadyRegisteredError)
    async def email_already_registered_handler(
        request: Request,
        exc: EmailAlreadyRegisteredError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Email already registered"},
        )

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(
        request: Request,
        exc: InvalidCredentialsError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid email or password"},
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
    
    @app.exception_handler(InvalidCompanyEmailError)
    async def invalid_company_email_handler(
        request: Request,
        error: InvalidCompanyEmailError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "detail": (
                    "Please sign in with your "
                    "@informationtechconsultants.co.uk email address."
                )
            },
        )
    
    @app.exception_handler(PermissionDeniedError)
    async def permission_denied_handler(
        request: Request,
        error: PermissionDeniedError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={"detail": str(error)},
        )