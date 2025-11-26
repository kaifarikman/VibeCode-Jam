from pydantic import BaseModel, EmailStr, Field

from .user import UserRead


class AuthRegisterRequest(BaseModel):
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class AuthLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class AuthCodeVerify(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class AuthSuccessResponse(TokenResponse):
    user: UserRead


