class ApplicationError(Exception):
    """Base class for expected application errors."""

class AuthenticationError(ApplicationError):
    """Base class for authentication failures."""

class EmailAlreadyRegisteredError(ApplicationError):
    pass

class InvalidCredentialsError(AuthenticationError):
    pass

class InvalidAccessTokenError(AuthenticationError):
    pass

class InvalidRefreshTokenError(AuthenticationError):
    pass

class InvalidGoogleTokenError(AuthenticationError): # TODO
    pass

class GoogleEmailNotVerifiedError(AuthenticationError):
    pass

class GoogleAccountConflictError(AuthenticationError):
    pass

class InvalidCompanyEmailError(AuthenticationError):
    pass

class PermissionDeniedError(ApplicationError):
    pass


class AccountNotFoundError(ApplicationError):
    pass


class AccountAlreadyExistsError(ApplicationError):
    pass
