from dataclasses import dataclass
from environs import Env
from typing import Optional
from pathlib import Path

@dataclass
class StorageConfig:
    audio_upload_dir: str

@dataclass
class DatabaseConfig:
    host: str
    port: int
    user: str
    password: str
    name: str
    url: str = ''
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10

    def __post_init__(self):
        self.url = (
            f"postgresql+asyncpg://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.name}"
        )

@dataclass
class AuthConfig:
    yandex_redirect_url: str
    yandex_client_id: str
    yandex_client_secret: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

@dataclass
class Config:
    db: DatabaseConfig
    auth: AuthConfig
    storage: StorageConfig

def load_config(env_path: Optional[str] = None) -> Config:
    env = Env()
    env.read_env(env_path)

    return Config(
        db=DatabaseConfig(
            host=env.str("POSTGRES_HOST"),
            port=env.int("POSTGRES_PORT"),
            user=env.str("POSTGRES_USER"),
            password=env.str("POSTGRES_PASSWORD"),
            name=env.str("POSTGRES_DB"),
        ),
        auth=AuthConfig(
            yandex_redirect_url=env.str("YANDEX_REDIRECT_URI"),
            yandex_client_id=env.str("YANDEX_CLIENT_ID"),
            yandex_client_secret=env.str("YANDEX_CLIENT_SECRET"),
            jwt_secret=env.str("JWT_SECRET"),
            jwt_algorithm=env.str("JWT_ALGORITHM", "HS256"),
            jwt_expire_minutes=env.int("JWT_EXPIRE_MINUTES", 30),
        ),
        storage=StorageConfig(
            audio_upload_dir=env.str("AUDIO_UPLOAD_DIR", "uploads/audio")
        )
    )

settings = load_config()