from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# for validating responses with access and refresh tokens
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# for validating the login request
class UserLogin(BaseModel):
    username: str
    password: str

# for validating the registration request
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=100)

# for validating the registration response
class UserResponse(BaseModel):
    username: str

class RefreshTokenRequest(BaseModel):
    token: str