import os
import asyncio
from pathlib import Path
from typing import Optional

class StorageService:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self._full_base_path = self._get_full_path(base_path)
    
    @classmethod
    async def create(cls, base_path: str) -> "StorageService":
        instance = cls(base_path)
        await instance.ensure_directory_exists() 
        return instance

    def _get_full_path(self, relative_path: str) -> str:
        return os.path.join(Path.cwd(), relative_path)
    
    async def ensure_directory_exists(self, path: Optional[str] = None) -> str:
        relative_path = os.path.join(self.base_path, path) if path else self.base_path
        full_path = self._get_full_path(relative_path)
        await asyncio.to_thread(Path(full_path).mkdir, parents=True, exist_ok=True)
        return relative_path
    
    async def get_full_path(self, relative_path: str) -> str:
        return self._get_full_path(os.path.join(self.base_path, relative_path))
    
    async def get_storage_path(self, relative_path: str) -> str:
        return os.path.join(self.base_path, relative_path)