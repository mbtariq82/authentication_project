from fastapi import FastAPI, status, Depends, HTTPException
import models
from database import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
import auth
from auth import get_current_user

# Main FastAPI application object.
app = FastAPI()

# Register the authentication routes under /auth.
app.include_router(auth.router)

# Create database tables when the app starts.
models.Base.metadata.create_all(bind=engine)

# Dependency that gives each request a database session.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Type aliases used by FastAPI dependency injection.
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
    
# Protected root route: it only returns data when a valid JWT is present.
@app.get("/", status_code=status.HTTP_200_OK)
async def user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return {"User": user}

