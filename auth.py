from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

# Secret key used to sign and verify JWT tokens.
SECRET_KEY = 'rP2G5WrneOzGca0XIH1CyJUhtIZK5f_eujwPKUcRkxE'
ALGORITHM = 'HS256'

# bcrypt is used here to store passwords safely before saving them.
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
# This dependency reads the bearer token from the Authorization header.
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

# Request body used when creating a new user.
class CreateUserRequest(BaseModel):
    username: str
    password: str

# Response body returned after successful login.
class Token(BaseModel):
    access_token: str
    token_type: str

# Shared database session dependency.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_depency = Annotated[Session, Depends(get_db)]

# Register a new user by hashing the password before saving it.
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_depency, create_user_request: CreateUserRequest):
    if len(create_user_request.password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be 72 bytes or fewer for bcrypt",
        )

    create_user_model = Users(
        username=create_user_request.username,
        hashed_password=bcrypt_context.hash(create_user_request.password),
    )

    db.add(create_user_model)
    db.commit()

# Authenticate the user and return a JWT access token.
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_depency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
    token = create_access_token(user.username, user.id, timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}

# Compare the submitted password with the stored password hash.
def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

# Build a signed JWT payload with username, user id, and expiration time.
def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

# Read and validate the JWT passed in the Authorization header.
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        user_id = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
        return {'username': username, 'id': user_id}
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")