from pydantic import BaseModel#, Field

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