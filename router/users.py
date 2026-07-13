from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserResponse
from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError, jwt

from config import SECRET_KEY, ALGORITHM

from security import oauth2_scheme

router = APIRouter(prefix="/users", tags=["users"])

def get_current_user(
    access_token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid access token") from exc
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user = (
        db.query(User)
        .filter(User.id == int(payload.get("sub")))
        .first()
    )
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/me", response_model=UserResponse)
def me(
    current_user: User = Depends(get_current_user),
):
    return current_user
