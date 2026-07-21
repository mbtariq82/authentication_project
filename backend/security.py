from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException
from uuid import uuid4
from google.auth.transport import requests
from google.oauth2 import id_token

from schemas import GoogleIdentity
from config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    GOOGLE_CLIENT_ID
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Could not decode token") from exc
    return payload


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": subject,
        "exp": expire,
        "type": "access",
    }     # might be good to include iat as well
    return jwt.encode(
        payload, 
        SECRET_KEY, 
        algorithm=ALGORITHM
    )

def create_refresh_token(subject: str) -> tuple[str, datetime]:
    expire = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": subject,
        "exp": expire,
        "type": "refresh",
        "jti": str(uuid4()),
    }     

    jwt_token = jwt.encode(
        payload, 
        SECRET_KEY, 
        algorithm=ALGORITHM
    )
    return (jwt_token, expire)

def verify_google_id_token(token: str) -> GoogleIdentity:
    try:
        payload = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID,
        )
    except ValueError as exc:
        print(exc)
        raise HTTPException(
            status_code=401,
            detail="Invalid Google ID token",
        ) from exc

    return GoogleIdentity(
        subject=payload["sub"],
        email=payload["email"],
        email_verified=payload["email_verified"],
    )