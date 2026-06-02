from datetime import timedelta, timezone

from pydantic_settings import BaseSettings

TZ = timezone(timedelta(hours=8))  # Beijing time (UTC+8)


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:////home/suhongzhou/dbSysWUT/data/scheduler.db"
    SECRET_KEY: str = "change-me-in-production-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"


settings = Settings()
