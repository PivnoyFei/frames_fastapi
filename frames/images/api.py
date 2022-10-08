import os
from typing import List
from uuid import uuid4

import aiofiles
from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import JSONResponse

from images.models import Image
from settings import STATIC_ROOT
from users import utils
from users.models import User

images_router = APIRouter(prefix='/frames', tags=["frames"])


@images_router.get("/{pk}")
async def get_frames(
    pk: int, user: User = Depends(utils.get_current_user)
):
    """Выдает информацию об изображении в формате JSON."""
    file = await Image.objects.get_or_none(id=pk)
    if not file:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "No file"}
        )
    return file


@images_router.delete("/{pk}")
async def get_frames_delete(
    pk: int, user: User = Depends(utils.get_current_user)
):
    """Удаляет файл по id."""
    file = await Image.objects.get_or_none(id=pk)
    if not file:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "No file"}
        )
    if user.id == file.user.id:
        f = os.path.join(STATIC_ROOT, file.title)
        if os.path.isfile(f):
            os.remove(f)
        await file.delete()
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
    user: User = Depends(utils.get_current_user)
):
    """
    Принимает от 1 до 15 изображений в формате jpeg
    Сохраняет с именами <UUID>.jpg.
    """
    error, save = {}, {}
    if len(files) > 15:
        files = files[:15]
        error["limit"] = "You have submitted more than 15 images"

    for file in files:
        print(file)
        filename = file.filename
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
            await Image.objects.create(user=user, title=title)
            save[filename] = {"status": status.HTTP_201_CREATED}
        except Exception as e:
            error[filename] = {
                "message": str(e),
                "status": status.HTTP_400_BAD_REQUEST
            }
            continue
        finally:
            file.file.close()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": save, "error": error}
    )
