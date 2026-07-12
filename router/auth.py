from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
from models import RefreshToken, User
from schemas import UserLogin, TokenResponse, UserCreate, UserResponse, RefreshTokenRequest

from config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    }     # might be good to include iat as well

    jwt_token = jwt.encode(
        payload, 
        SECRET_KEY, 
        algorithm=ALGORITHM
    )
    return (jwt_token, expire)

@router.post("/login", response_model=TokenResponse)
def login(
    user_login: UserLogin,
    db: Session = Depends(get_db)      
):
    user = (
        db.query(User)
        .filter(User.username == user_login.username)
        .first()
    )
    if not user or not pwd_context.verify(
        user_login.password, 
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401, 
            detail="Invalid username or password"
        )
    access_token = create_access_token(subject=str(user.id))
    refresh_token, expire = create_refresh_token(subject=str(user.id))

    refresh_token_obj = RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=expire,
    )

    db.add(refresh_token_obj)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

# currently we are not issuing refresh or access tokens during registration
@router.post("/register", response_model=UserResponse)
def register(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.username == user_create.username)
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=409, 
            detail="Username already registered"
        )
        
    new_user = User(
        username=user_create.username,
        hashed_password=pwd_context.hash(user_create.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid refresh token") from exc
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    refresh_record = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == request.token)
        .first()
    )
    if not refresh_record or refresh_record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired or revoked")
    user = (
        db.query(User)
        .filter(User.id == int(payload.get("sub")))
        .first()
    )
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    new_access_token = create_access_token(subject=str(user.id))
    new_refresh_token, new_expire = create_refresh_token(subject=str(user.id))
    refresh_record.token = new_refresh_token
    refresh_record.expires_at = new_expire
    db.commit()
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }
