from pydantic import BaseModel, EmailStr, Field, field_validator

from .user import UserRead


class AuthRegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(..., max_length=255, description='ФИО (минимум 3 слова)')

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        words = v.strip().split()
        if len(words) < 3:
            raise ValueError('ФИО должно содержать минимум 3 слова (Фамилия Имя Отчество)')
        return v
    password: str = Field(..., min_length=8, max_length=128)


class AuthLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class AuthCodeVerify(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)


class AuthRequestCode(BaseModel):
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class AuthSuccessResponse(TokenResponse):
    user: UserRead


