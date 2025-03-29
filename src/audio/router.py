from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.core.database import get_db
from src.shared.utils.get_current_user import get_current_user
from src.users.model import User
from src.audio.schema import AudioInDB
from src.audio.service import AudioService

AudioRouter = APIRouter(tags=["Audio"])

@AudioRouter.post("/upload", response_model=AudioInDB, status_code=201)
async def upload_audio(
    file: UploadFile = File(...),
    title: str = Form(...),
    is_public: bool = Form(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = AudioService(db)
    audio = await service.upload_audio_file(
        file=file,
        title=title,
        is_public=is_public,
        user_id=current_user.id
    )
    return AudioInDB.model_validate(audio)

@AudioRouter.get("/me", response_model=list[AudioInDB])
async def get_my_audios(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = AudioService(db)
    audios = await service.get_user_audios(current_user.id)
    return [AudioInDB.model_validate(a) for a in audios]

@AudioRouter.get("/public", response_model=list[AudioInDB])
async def get_public_audios(db: AsyncSession = Depends(get_db)):
    service = AudioService(db)
    audios = await service.get_public_audios()
    return [AudioInDB.model_validate(a) for a in audios]

@AudioRouter.delete("/{audio_id}", status_code=204)
async def delete_audio(
    audio_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = AudioService(db)
    await service.delete_user_audio(audio_id, current_user.id, current_user.is_superuser)

@AudioRouter.get("/download/{audio_id}")
async def download_audio(
    audio_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = AudioService(db)
    return await service.download_audio_file(
        audio_id=audio_id,
        user_id=current_user.id if current_user else None,
        is_superuser=current_user.is_superuser if current_user else False
    )