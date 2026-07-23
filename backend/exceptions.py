# exceptions.py


class ApplicationError(Exception):
    """Base class for expected application errors."""


class AuthenticationError(ApplicationError):
    """Base class for authentication failures."""


class UsernameAlreadyRegisteredError(ApplicationError):
    pass


class InvalidCredentialsError(AuthenticationError):
    pass


class InvalidAccessTokenError(AuthenticationError):
    pass


class InvalidRefreshTokenError(AuthenticationError):
    pass


class InactiveUserError(AuthenticationError):
    pass


class InvalidGoogleTokenError(AuthenticationError): # TODO
    pass


class GoogleEmailNotVerifiedError(AuthenticationError):
    pass


class GoogleAccountConflictError(AuthenticationError):
    pass