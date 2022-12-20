from datetime import datetime, timedelta

from fastapi import Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError

import settings
from db import database
from users.models import User
from users.schemas import TokenPayload

db_user = User(database)
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/users/login",
    scheme_name="JWT"
)


async def get_hashed_password(password: str) -> str:
    """Хэширует пароль пользователя."""
    return password_context.hash(password)


async def verify_password(password: str, hashed_pass: str) -> bool:
    """Проверяет хэшированный пароль входящего пользователя."""
    return password_context.verify(password, hashed_pass)


async def __get_token(secret, expire_minutes, user, expires_delta) -> str:
    """Вызывается из create_access_token и create_refresh_token."""
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=expire_minutes)
    to_encode = {"exp": expires_delta, "sub": str(user)}
    encoded_jwt = jwt.encode(to_encode, secret, settings.ALGORITHM)
    return encoded_jwt


async def create_access_token(user: str, expires_delta: int = None) -> str:
    """Создает access token."""
    return await __get_token(
        settings.JWT_SECRET_KEY,
        settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        user,
        expires_delta
    )


async def create_refresh_token(user: str, expires_delta: int = None) -> str:
    """Создает refresh token."""
    return await __get_token(
        settings.JWT_REFRESH_SECRET_KEY,
        settings.REFRESH_TOKEN_EXPIRE_MINUTES,
        user,
        expires_delta
    )


async def get_current_user(token: str = Depends(reuseable_oauth)):
    """Проверяет текущего авторизированного пользователя."""
    credentials_exception = JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"message": "Could not validate credentials"}
    )
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            return credentials_exception

    except (JWTError, ValidationError):
        return credentials_exception

    user = await db_user.get_user_full(token_data.sub)
    if user:
        return user
    return credentials_exception
