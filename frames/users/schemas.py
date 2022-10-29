import datetime
from typing import Union

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
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class Userfull(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    timestamp: datetime.date


class UserUpdate(BaseModel):
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    email: Union[EmailStr, None] = None


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None
