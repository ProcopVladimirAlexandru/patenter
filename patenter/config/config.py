import os
from functools import cached_property

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    OPENAI_API_KEY: str = Field(..., alias="OPENAI_API_KEY")
    MODEL_UID: str = Field("gpt-4o", alias="MODEL_UID")
    OPENAI_REQUEST_TIMEOUT_S: int = Field(600, alias="OPENAI_REQUEST_TIMEOUT_S")
    OPENAI_MAX_RETRIES: int = Field(5, alias="OPENAI_MAX_RETRIES")
    OPENAI_TEMPERATURE: float = Field(0.0, alias="OPENAI_TEMPERATURE")

    LOG_LEVEL: str = Field("INFO", alias="LOG_LEVEL")
    DB_FILE_PATH: str = Field("data/PatentData.json", alias="DB_FILE_PATH")

    KEYDB_CACHE_URL: str = Field("redis://localhost:6379/1", alias="KEYDB_CACHE_URL")
    KEYDB_CELERY_BROKER_URL: str = Field(
        "redis://localhost:6379/0", alias="KEYDB_CELERY_BROKER_URL"
    )

    @computed_field()  # type: ignore[misc]
    @cached_property
    def ALLOW_ORIGINS(self) -> list[str]:
        return (
            os.getenv("ALLOW_ORIGINS", "").split(",")
            if os.getenv("ALLOW_ORIGINS", None)
            else []
        )


config = Config()
