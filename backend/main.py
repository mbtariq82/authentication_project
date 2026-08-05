from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from redis_client import redis_client
from exception_handlers import register_exception_handlers

from router import auth, users, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_client.ping()
    print("Connected to Redis")
    yield
    await redis_client.aclose()

app = FastAPI(lifespan=lifespan)

@app.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "healthy"}

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://authentication-project-frontend-651980295854.s3-website.eu-west-2.amazonaws.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)