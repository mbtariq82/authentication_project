## TO DO:
- move non-HTTP logic out of users router
- complete DDD concepts
- redis
- react + vite

## Issues
- store hash of refresh key instead of raw key
- 204 No Content response
- implement abstract repos
- implement a unit of work object
- implement value objects

## SQLAlchemy
- Session / AsyncSession
    - track Python objects, changes, manages transactions and uses a database connection when needed
    - Think of it as a workspace: Session, Current transaction, Objects being tracked, Changes waiting to be saved, Database connection
- flush
- the lifecycle of ORM objects:
    - Transient – a new Python object that the session doesn't know about.
    - Pending – added to the session, waiting to be inserted.
    - Persistent – stored in the database and tracked by the session.
    - Detached – no longer associated with a session

## Clean architecture
- bounded context
- context mapping
- dependency injection (x)
    - An object does not construct its own dependencies; another part of the application constructs them and supplies them
    - in fastapi, Depends()
- domain events (x)
- aggegrate and aggregrate root (x)
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
- service layer (x)
- SOLID (x)

## Frontend notes
ANIMATED BACKGROUND VS AROURA/GRADIENT BACKGROUND VS GLASSMORPHISM VS SPLIT SCREEN PREVIEW





- react/svelte/vue: UI libraries
- vite: client-side build tool
- next.js/remix/tanstack start: full-stack frontend framework
- generally you choose either a client-side build tool (like Vite) or a full-stack framework (like Next.js or Remix) as the foundation of your app
- next.js is built on top of react