from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from datetime import date


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    POLLING_DATE: date

    model_config = ConfigDict(env_file=".env")


settings = Settings()