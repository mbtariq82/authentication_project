from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
from models import RefreshToken, User
from schemas import UserLogin, TokenResponse, UserCreate, UserResponse

from config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)

# def hash_password(password: str) -> str:
#     return pwd_context.hash(password)

def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": subject,
        "exp": expire,
        "type": "access",
    }     # might be good to include iat as well
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": subject,
        "exp": expire,
        "type": "refresh",
    }     # might be good to include iat as well
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

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
    if not user:
        raise HTTPException(
            status_code=401, 
            detail="Username not found"
        )
    if not pwd_context.verify(
        user_login.password, 
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401, 
            detail="Incorrect password"
        )
    access_token = create_access_token(subject=user.username)
    refresh_token = create_refresh_token(subject=user.username)

    refresh_record = RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(refresh_record)
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

    hashed_password = pwd_context.hash(user_create.password)
    new_user = User(
        username=user_create.username,
        hashed_password=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/refresh", response_model=TokenResponse)





# async def get_current_user(
#     token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(get_db)]
# ) -> User:
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str | None = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#     except JWTError as exc:
#         raise credentials_exception from exc

#     result = await db.execute(select(User).where(User.username == username))
#     user = result.scalar_one_or_none()
#     if user is None:
#         raise credentials_exception
#     return user



# @router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# async def register_user(user_data: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
#     existing_user = await db.scalar(
#         select(User).where(or_(User.username == user_data.username, User.email == user_data.email))
#     )
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Username or email already registered")

#     user = User(
#         username=user_data.username,
#         email=str(user_data.email),
#         full_name=user_data.full_name,
#         hashed_password=get_password_hash(user_data.password),
#         role=RoleEnum.USER,
#         is_active=True,
#     )
#     db.add(user)
#     await db.commit()
#     await db.refresh(user)
#     return user

# @router.post("/refresh", response_model=TokenResponse)
# async def refresh_token(
#     token: str,
#     db: Annotated[AsyncSession, Depends(get_db)],
# # ):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#     except JWTError as exc:
#         raise HTTPException(status_code=401, detail="Invalid refresh token") from exc

#     if payload.get("type") != "refresh":
#         raise HTTPException(status_code=401, detail="Invalid refresh token")

#     result = await db.execute(select(RefreshToken).where(RefreshToken.token == token))
#     refresh_record = result.scalar_one_or_none()
#     if not refresh_record or refresh_record.revoked or refresh_record.expires_at < datetime.now(timezone.utc):
#         raise HTTPException(status_code=401, detail="Refresh token expired or revoked")

#     result = await db.execute(select(User).where(User.username == payload.get("sub")))
#     user = result.scalar_one_or_none()
#     if not user:
#         raise HTTPException(status_code=401, detail="User not found")

#     new_access_token = create_access_token(subject=user.username)
#     new_refresh_token = create_refresh_token(subject=user.username)
#     refresh_record.token = new_refresh_token
#     refresh_record.expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
#     await db.commit()

#     return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token, token_type="bearer")