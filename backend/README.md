## Apache Kafka vs SQS
- Kafka behaves like a durable event log

## MSK


## SNS/SQS
- SNS: notifications
- SQS: queue
- transaction outbox pattern


## Apache Kafka: distributed logs
- decoupling system dependencies
- APIs: producer, consumer, streams (transforming data), connector (build reusable producers/consumers)
- topic: ordered list of events, analogous to a named stream
- broker: kafka server
- cluster: collection of brokers
- partitions ( )
- leader partition ( )
- replica partition ( )
- key ( )
- consumer groups: consumers grouped together, kafka distributes the partitions among them
    - within 1 consumer group, a partition is processed by at most one consumer at a time
- offsets: inside each partition, kafka numbers the events
- To publish (write) and subscribe to (read) streams of events, including continuous import/export of your data from other systems.
- To store streams of events durably and reliably for as long as you want.
- To process streams of events as they occur or retrospectively.

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