from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import (
    PROFILE_IMAGE_LOCAL_DIR,
    PROFILE_IMAGE_STORAGE_BACKEND,
    PROFILE_IMAGE_URL_PREFIX,
)
from database import engine
from exception_handlers import register_exception_handlers
from redis_client import redis_client
from router import accounts, admin, auth, card, users
from telemetry import configure_telemetry, instrument_application

from router import beneficiaries, transactions

telemetry_providers = configure_telemetry()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await redis_client.ping()
        print("Connected to Redis")
        yield
    finally:
        try:
            await redis_client.aclose()
        finally:
            telemetry_providers.shutdown()

app = FastAPI(lifespan=lifespan)

if PROFILE_IMAGE_STORAGE_BACKEND == "local":
    app.mount(
        PROFILE_IMAGE_URL_PREFIX,
        StaticFiles(
            directory=PROFILE_IMAGE_LOCAL_DIR / "profile-images",
            check_dir=False,
        ),
        name="profile-images",
    )

@app.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "healthy"}

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://authentication-project-frontend-651980295854.s3-website.eu-west-2.amazonaws.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(accounts.router)
app.include_router(beneficiaries.router)
app.include_router(transactions.router)
app.include_router(card.router)

instrument_application(
    app=app,
    engine=engine,
    redis_client=redis_client,
    providers=telemetry_providers,
)
