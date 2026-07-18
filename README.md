## TO DO:
- move non-HTTP logic out of users router
- complete DDD concepts
- redis
- react + vite

## Issues
- store hash of refresh key instead of raw key
- 204 No Content response

### Clean architecture
- bounded context
- context mapping
- dependency injection (x)
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
- layered architecture (x)