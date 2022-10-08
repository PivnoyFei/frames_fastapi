from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from users import utils
from users.models import User
from users.schemas import TokenSchema, UserBase, UserCreate

user_router = APIRouter(prefix='/users', tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scheme_name="JWT")


@user_router.post("/signup", response_model=UserCreate)
async def create_user(user: User):
    """Создает нового пользователя."""
    user.password = utils.get_hashed_password(user.password)
    return await user.save()


@user_router.post('/login', response_model=TokenSchema)
async def login(data: OAuth2PasswordRequestForm = Depends()):
    """Создает и обновляет токены пользователя."""
    user = await User.objects.get_or_none(username=data.username)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Incorrect username"}
        )
    if not utils.verify_password(data.password, user.password):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Incorrect password"}
        )
    return {
        "access_token": utils.create_access_token(user.username),
        "refresh_token": utils.create_access_token(user.username),
    }


@user_router.get('/me', response_model=UserBase)
async def get_me(user: User = Depends(utils.get_current_user)):
    """Получает информацию об авторизированном пользователе."""
    return user
