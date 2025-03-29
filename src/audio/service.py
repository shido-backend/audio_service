import os
import uuid
from typing import List, Optional
from uuid import UUID
from fastapi.responses import FileResponse
from mutagen.mp3 import MP3
from fastapi import Path, UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path as PathLib 

from src.core.storage.service import StorageService
from src.core.config.config import settings
from src.audio.model import Audio
from src.shared.repositories.base import BaseRepository

class AudioService:
    def __init__(self, session: AsyncSession):
        self.repository = BaseRepository(Audio, session)
        self.upload_dir = settings.storage.audio_upload_dir

        self.repository = BaseRepository(Audio, session)
        self.storage = StorageService(settings.storage.audio_upload_dir)
        self.storage.ensure_directory_exists()

    async def _get_audio_duration(self, file_path: str) -> int:
        try:
            audio = MP3(file_path)
            return int(audio.info.length)
        except Exception:
            return 0

    async def _save_audio_file(self, file: UploadFile) -> tuple[str, int, int, str]:
        file_uuid = uuid.uuid4()
        file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'bin'
        filename = f"{file_uuid}.{file_ext}"

        file_path = self.storage.get_full_path(filename)

        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        duration = await self._get_audio_duration(file_path)
        return file_path, duration, len(contents), file_ext

    async def upload_audio_file(
        self,
        file: UploadFile,
        title: str,
        is_public: bool,
        user_id: UUID
    ) -> Audio:
        file_path, duration, size, file_ext = await self._save_audio_file(file)
        
        audio_data = {
            "title": title,
            "duration": duration,
            "size": size,
            "format": file_ext,
            "is_public": is_public,
            "file_path": file_path,
            "user_id": user_id
        }
        
        return await self.repository.create(Audio(**audio_data))

    async def get_audio(self, audio_id: UUID) -> Optional[Audio]:
        return await self.repository.get(audio_id)

    async def get_user_audios(self, user_id: UUID) -> List[Audio]:
        return await self.repository.get_many_by_field("user_id", user_id)

    async def get_public_audios(self) -> List[Audio]:
        return await self.repository.get_many_by_field("is_public", True)

    async def delete_user_audio(
        self,
        audio_id: UUID,
        user_id: UUID,
        is_superuser: bool = False
    ) -> None:
        audio = await self.get_audio(audio_id)
        
        if not audio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audio not found"
            )
        
        if audio.user_id != user_id and not is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )

        try:
            os.remove(audio.file_path)
        except OSError:
            pass
        
        await self.repository.delete(audio_id)

    async def get_audio_for_download(self, audio_id: UUID, user_id: UUID = None, is_superuser: bool = False) -> Audio:
        audio = await self.get_audio(audio_id)
        
        if not audio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audio not found"
            )

        if not audio.is_public and (not user_id or audio.user_id != user_id) and not is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this audio"
            )
        
        return audio
    
    async def download_audio_file(
        self,
        audio_id: UUID,
        user_id: UUID = None,
        is_superuser: bool = False
    ) -> FileResponse:
        audio = await self.get_audio_for_download(audio_id, user_id, is_superuser)
        
        file_path = PathLib(audio.file_path)  
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audio file not found on server"
            )

        filename = f"{audio.title}.{audio.format}" if audio.title else f"audio_{audio_id}.{audio.format}"
        
        return FileResponse(
            path=str(file_path),
            media_type=self._get_mime_type(audio.format),
            filename=filename
        )
    
    def _get_mime_type(self, file_ext: str) -> str:
        mime_types = {
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'ogg': 'audio/ogg',
            'flac': 'audio/flac',
            'aac': 'audio/aac',
        }
        return mime_types.get(file_ext.lower(), 'application/octet-stream')