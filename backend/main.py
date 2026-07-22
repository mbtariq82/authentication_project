from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from redis_client import redis_client

from database import Base, engine
from router import auth, users

@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_client.ping()
    print("Connected to Redis")
    yield
    await redis_client.aclose()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)

#Base.metadata.create_all(bind=engine)