from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import engine
from redis_client import redis_client
from exception_handlers import register_exception_handlers
from telemetry import configure_telemetry, instrument_application

from router import auth, users, admin

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

instrument_application(
    app=app,
    engine=engine,
    redis_client=redis_client,
    providers=telemetry_providers,
)
