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

class PermissionDeniedError(ApplicationError):
    pass


class AccountNotFoundError(ApplicationError):
    pass


class AccountAlreadyExistsError(ApplicationError):
    pass


class InsufficientFundsError(ApplicationError):
    pass


class InvalidBalanceAmountError(ApplicationError):
    pass


class InvalidTransactionRuleError(ApplicationError):
    pass


class InvalidTransactionStatusTransitionError(ApplicationError):
    pass


class TransactionNotFoundError(ApplicationError):
    pass


class BeneficiaryNotFoundError(ApplicationError):
    pass


class InvalidBeneficiaryUpdateError(ApplicationError):
    pass
