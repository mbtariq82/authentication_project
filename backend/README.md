## TO DO:
- tests

## Clean architecture notes
- SOLID (x)
- dependency injection (x)
    - An object does not construct its own dependencies; another part of the application constructs them and supplies them
    - in fastapi, Depends()
- unit of work (x)
- value objects (x)
    - @dataclass(frozen=True)
    - typical examples: EmailAddress, Username, HashedPassword, Money, Address,
    - PhoneNumber, DateRange, Percentage, OrderNumber, Postcode, Coordinates
    - Pydantic schema validates data crossing the API boundary
- entities vs domains (x)
    - e.g. user.promote_to_admin() NOT service.promote_to_admin(user)
    - e.g. user.deactivate(), user.activate()
- repository pattern (x)
    - Repositories exist for aggregate roots, not for every table.
    - abstract repos (interfaces)
    - only for postgres
- service layer (x)
- bounded context
- context mapping
- domain events
- aggegrate and aggregrate root

example flow for login:
    React LoginPage
        ↓
    LoginForm
        ↓
    useLogin hook
        ↓
    authClient.login()
        ↓
    POST /auth/login
        ↓
    FastAPI auth router
        ↓
    LoginCommand
        ↓
    AuthService.login()
        ↓
    SqlAlchemyAuthUnitOfWork
        ↓
    SqlAlchemyUserRepository
        ↓
    PostgreSQL
        ↓
    Password verification
        ↓
    Create access and refresh tokens
        ↓
    SqlAlchemyRefreshTokenRepository
        ↓
    PostgreSQL
        ↓
    TokenResponse
        ↓
    authClient
        ↓
    tokenStorage
        ↓
    Navigate to DashboardPage