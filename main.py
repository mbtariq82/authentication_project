from fastapi import FastAPI

from database import Base, engine
from router import auth, users

app = FastAPI(title="JWT Authentication Project")
app.include_router(auth.router)
app.include_router(users.router)


Base.metadata.create_all(bind=engine)