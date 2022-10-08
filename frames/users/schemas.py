from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
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


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None
