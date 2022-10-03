import os
from typing import List
from uuid import uuid4

import aiofiles
from fastapi import APIRouter, File, UploadFile, status
from fastapi.responses import JSONResponse
from images.models import Image
from settings import STATIC_ROOT

images_router = APIRouter(prefix='/frames', tags=["frames"])


@images_router.get("/{pk}")
async def get_frames(pk: int):
    """Выдает информацию об изображении в формате JSON."""
    try:
        file = await Image.objects.get(id=pk)
    except:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "No file"}
        )
    return file


@images_router.delete("/{pk}")
async def get_frames_delete(pk: int):
    """Удаляет файл по id."""
    try:
        file = await Image.objects.get(id=pk)
        f = dict(file)["title"]
        if os.path.isfile(f):
            os.remove(f)
        await file.delete()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "File deleted"}
        )
    except:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "No file"}
        )


@images_router.post("/")
async def get_frames_save(files: List[UploadFile] = File(...)):
    """
    Принимает от 1 до 15 изображений в формате jpeg
    Сохраняет с именами <UUID>.jpg.
    """
    # user = await User.objects.first()
    error, save = {}, {}
    if len(files) > 15:
        files = files[:15]
        error["limit"] = "You have submitted more than 15 images"

    for file in files:
        filename = file.filename
        if not filename.lower().endswith(('.jpg', '.jpeg')):
            error[filename] = {
                "message": "File extension not jpg or jpeg",
                "status": status.HTTP_400_BAD_REQUEST
            }
            continue
        title = f"{STATIC_ROOT}/{uuid4()}.jpg"

        try:
            async with aiofiles.open(title, "wb") as buffer:
                await buffer.write(await file.read())
            await Image.objects.create(title=title)  # user=user
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
