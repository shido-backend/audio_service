from dataclasses import dataclass
from environs import Env
from typing import Optional

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
class Config:
    db: DatabaseConfig

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
        )
    )

settings = load_config()