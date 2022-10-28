import datetime

from pydantic import BaseModel, EmailStr


class GetUser(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str
    first_name: str
    last_name: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class UserBase(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    timestamp: datetime.date


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None
