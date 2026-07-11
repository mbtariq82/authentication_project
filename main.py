from fastapi import FastAPI

from database import Base, engine
from models import *
from router import auth, users

app = FastAPI(title="Authentication Tutorial", version="1.0.0")
app.include_router(auth.router)
app.include_router(users.router)


@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
