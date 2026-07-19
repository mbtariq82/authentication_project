"""
Pydantic schemas define the data exchanged through the API.

These models are intentionally separate from the SQLAlchemy ORM models.
This allows us to:
- expose only the fields intended for clients (e.g. never `hashed_password`)
- validate incoming requests and outgoing responses
- keep the public API contract independent of the database schema

This separation means the database can evolve without unnecessarily
breaking the API, and vice versa.
"""

from pydantic import BaseModel, ConfigDict#, Field

class RegisterCommand(BaseModel):
    username: str
    password: str
    #email
    #full_name

class LoginCommand(BaseModel):
    username: str
    password: str
    #captcha
    #mfa

class LogoutCommand(BaseModel):
    token: str
    #session_id

class RefreshCommand(BaseModel):
    token: str
    #session_id

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# Public representation of a User returned by the API.
# Keeping this separate from the SQLAlchemy User model prevents exposing
# internal fields (e.g. hashed_password) and decouples the API contract
# from the database schema.
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str