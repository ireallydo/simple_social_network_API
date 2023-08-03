from pydantic import BaseSettings, Field
from pathlib import Path
from datetime import timedelta


class Settings(BaseSettings):

    HOST: str = Field(..., env="HOST")
    PORT: str = Field(..., env="PORT")

    DB_NAME: str = Field(..., env="DB_NAME")
    DB_USER: str = Field(..., env="DB_USER")
    DB_PASSWORD: str = Field(..., env="DB_PASSWORD")
    DB_HOST: str = Field(..., env="DB_HOST")

    ACCESS_TOKEN_EXPIRE_MINUTES: timedelta = Field(timedelta(minutes=5), env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_MINUTES: timedelta = Field(timedelta(days=1), env="REFRESH_TOKEN_EXPIRE_MINUTES")
    TOKEN_ALGO: str = Field('HS256', env="TOKEN_ALGO")
    JWT_KEY: str = Field(..., env="JWT_KEY")
    JWT_REFRESH_KEY: str = Field(..., env="JWT_REFRESH_KEY")

    HUNTER_IO_API_KEY: str = Field(..., env="HUNTER_IO_API_KEY")
    HUNTER_IO_API_HOST: str = Field(..., env="HUNTER_IO_API_HOST")
    HUNTER_IO_API_VERIFIER: str = Field(..., env="HUNTER_IO_API_VERIFIER")
    HUNTER_IO_API_RETRY: int = Field(3, env="HUNTER_IO_API_RETRY")
    HUNTER_IO_API_SLEEP: int = Field(5, env="")

    LOG_FILEPATH: str = Field("logs/app_log.log", env="LOG_FILEPATH")
    LOG_ROTATION: int = Field(1, env="LOG_ROTATION")
    LOG_RETENTION: int = Field(30, env="LOG_RETENTION")

    class Config:
        env_file = Path(__file__).parents[1].joinpath(".env")
        env_file_encoding = "utf-8"
