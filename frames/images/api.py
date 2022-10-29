import os
from datetime import datetime
from typing import List
from uuid import uuid4

import aiofiles
from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import JSONResponse

from db import database
from images.models import Inbox
from settings import STATIC_ROOT
from users.models import User
from users.utils import get_current_user

images_router = APIRouter(prefix='/frames', tags=["frames"])
db_inbox = Inbox(database)


@images_router.get("/{pk}")
async def get_frames(
    pk: int, user: User = Depends(get_current_user)
):
    """Выдает информацию об изображении в формате JSON."""
    file = await db_inbox.get_image(pk)
    if not file:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "No file"}
        )
    return file


@images_router.delete("/{pk}")
async def get_frames_delete(
    pk: int, user: User = Depends(get_current_user)
):
    """Удаляет файл по id."""
    file = await db_inbox.get_image_user_title(pk)
    if not file:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "No file"}
        )
    if user["id"] == file["user"]:
        f = os.path.join(STATIC_ROOT, file["title"])
        if os.path.isfile(f):
            os.remove(f)
        await db_inbox.delete_image(pk)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "File deleted"}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "You are not the author"}
        )


@images_router.post("/")
async def get_frames_save(
    files: List[UploadFile] = File(...),
    user: User = Depends(get_current_user)
):
    """
    Принимает от 1 до 15 изображений в формате jpeg.
    Если изображений больше сохраняет только первые 15
    и сообщает пользователю.
    Сохраняет с именами <UUID>.jpg.
    """
    error, save = {}, {}
    if len(files) > 15:
        files = files[:15]
        error["limit"] = "You have submitted more than 15 images"

    for file in files:
        filename = file.filename

        """
        Если изображение не подходит по формату,
        записывает его в сообщение об ошибке пользователю и идет дальше.
        """
        if not filename.lower().endswith(('.jpg', '.jpeg')):
            error[filename] = {
                "message": "File extension not jpg or jpeg",
                "status": status.HTTP_400_BAD_REQUEST
            }
            continue
        title = f"{uuid4()}.jpg"

        try:
            async with aiofiles.open(
                os.path.join(STATIC_ROOT, title), "wb"
            ) as buffer:
                await buffer.write(await file.read())
            await db_inbox.create_image(
                user["id"], title, str(datetime.now().strftime("%Y%m%d"))
            )
            save[filename] = {"status": status.HTTP_201_CREATED}

        except Exception as e:
            buffer = os.path.join(STATIC_ROOT, title)
            if os.path.isfile(buffer):
                os.remove(buffer)
            error[filename] = {
                "message": str(e),
                "status": status.HTTP_400_BAD_REQUEST
            }
            continue

        finally:
            file.file.close()

    """Возвращает перечень созданных элементов"""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": save, "error": error}
    )
