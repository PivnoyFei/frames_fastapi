from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from db import database
from users import utils
from users.models import User
from users.schemas import GetUser, TokenSchema, UserBase, UserCreate

user_router = APIRouter(prefix='/users', tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scheme_name="JWT")
db_user = User(database)


@user_router.post("/signup", response_model=GetUser)
async def create_user(data: UserCreate):
    """Создает нового пользователя."""
    if await db_user.get_user_by_email(data.email):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Email already exists"}
        )
    if await db_user.get_user_by_username(data.username):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Username already exists"}
        )
    data.password = await utils.get_hashed_password(data.password)
    await db_user.create_user(data)
    return await db_user.get_user_full(data.username)


@user_router.post('/login', response_model=TokenSchema)
async def login(data: OAuth2PasswordRequestForm = Depends()):
    """Создает и обновляет токены пользователя."""
    user = await db_user.get_user_password_by_username(data.username)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Incorrect username"}
        )
    if not await utils.verify_password(data.password, user["password"]):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Incorrect password"}
        )
    return {
        "access_token": await utils.create_access_token(user["username"]),
        "refresh_token": await utils.create_access_token(user["username"]),
    }


@user_router.get('/me', response_model=UserBase)
async def get_me(data: UserBase = Depends(utils.get_current_user)):
    """Получает информацию об авторизированном пользователе."""
    return data
