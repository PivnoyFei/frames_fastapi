from datetime import datetime, timedelta

from fastapi import Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError

import settings
from users.models import User
from users.schemas import TokenPayload

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/login",
    scheme_name="JWT"
)


def get_hashed_password(password: str) -> str:
    """Хеширует пароль пользователя."""
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    """Проверяет хешированный пароль входящего пользователя."""
    return password_context.verify(password, hashed_pass)


def __get_token(secret, expire_minutes, subject, expires_delta) -> str:
    """Вызывается из create_access_token и create_refresh_token."""
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=expire_minutes)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, secret, settings.ALGORITHM)
    return encoded_jwt


def create_access_token(subject: str, expires_delta: int = None) -> str:
    """Создает access token."""
    return __get_token(
        settings.JWT_SECRET_KEY,
        settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        subject,
        expires_delta
    )


def create_refresh_token(subject: str, expires_delta: int = None) -> str:
    """Создает refresh token."""
    return __get_token(
        settings.JWT_REFRESH_SECRET_KEY,
        settings.REFRESH_TOKEN_EXPIRE_MINUTES,
        subject,
        expires_delta
    )


async def get_current_user(token: str = Depends(reuseable_oauth)) -> User:
    """Проверяет текущего авторизированного пользователя."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (JWTError, ValidationError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await User.objects.get_or_none(username=token_data.sub)
    if not user:
        raise JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Could not find user"},
        )
    return user
