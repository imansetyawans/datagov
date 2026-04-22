import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./datagov.db")

    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

    debug: bool = True
    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env.local"


settings = Settings()