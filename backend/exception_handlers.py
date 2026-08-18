from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from exceptions import (
    AccountAlreadyExistsError,
    AccountNotFoundError,
    EmailAlreadyRegisteredError,
    BeneficiaryNotFoundError,
    InvalidBeneficiaryUpdateError,
    GoogleAccountConflictError,
    GoogleEmailNotVerifiedError,
    InvalidAccessTokenError,
    InvalidCredentialsError,
    InvalidGoogleTokenError,
    InvalidProfileImageError,
    InvalidProfileUpdateError,
    InvalidRefreshTokenError,
    InsufficientFundsError,
    InvalidTransactionRuleError,
    InvalidTransactionStatusTransitionError,
    TransactionNotFoundError,
    PermissionDeniedError,
    ProfileImageStorageError,
    ProfileImageTooLargeError,
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

    @app.exception_handler(PermissionDeniedError)
    async def permission_denied_handler(
        request: Request,
        error: PermissionDeniedError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={"detail": str(error)},
        )

    @app.exception_handler(AccountNotFoundError)
    async def account_not_found_handler(
        request: Request,
        error: AccountNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Account not found"},
        )

    @app.exception_handler(AccountAlreadyExistsError)
    async def account_already_exists_handler(
        request: Request,
        error: AccountAlreadyExistsError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Account already exists"},
        )

    @app.exception_handler(BeneficiaryNotFoundError)
    async def beneficiary_not_found_handler(
        request: Request,
        error: BeneficiaryNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Beneficiary not found"},
        )

    @app.exception_handler(InvalidBeneficiaryUpdateError)
    async def invalid_beneficiary_update_handler(
        request: Request,
        error: InvalidBeneficiaryUpdateError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "At least one beneficiary field is required"},
        )

    @app.exception_handler(TransactionNotFoundError)
    async def transaction_not_found_handler(
        request: Request,
        error: TransactionNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Transaction not found"},
        )

    @app.exception_handler(InsufficientFundsError)
    async def insufficient_funds_handler(
        request: Request,
        error: InsufficientFundsError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Insufficient funds"},
        )

    @app.exception_handler(InvalidTransactionRuleError)
    async def invalid_transaction_rule_handler(
        request: Request,
        error: InvalidTransactionRuleError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": str(error)},
        )

    @app.exception_handler(InvalidTransactionStatusTransitionError)
    async def invalid_transaction_status_transition_handler(
        request: Request,
        error: InvalidTransactionStatusTransitionError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(error)},
        )

    @app.exception_handler(InvalidProfileImageError)
    async def invalid_profile_image_handler(
        request: Request,
        error: InvalidProfileImageError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(error)},
        )

    @app.exception_handler(ProfileImageTooLargeError)
    async def profile_image_too_large_handler(
        request: Request,
        error: ProfileImageTooLargeError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={"detail": "Profile image must be 5 MB or smaller"},
        )

    @app.exception_handler(InvalidProfileUpdateError)
    async def invalid_profile_update_handler(
        request: Request,
        error: InvalidProfileUpdateError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(error)},
        )

    @app.exception_handler(ProfileImageStorageError)
    async def profile_image_storage_handler(
        request: Request,
        error: ProfileImageStorageError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Profile image storage is unavailable"},
        )
