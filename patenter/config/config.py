from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    OPENAI_API_KEY: str = Field(..., alias="OPENAI_API_KEY")
    MODEL_UID: str = Field("gpt-4o", alias="MODEL_UID")
    OPENAI_REQUEST_TIMEOUT_S: int = Field(300, alias="OPENAI_REQUEST_TIMEOUT_S")
    OPENAI_MAX_RETRIES: int = Field(5, alias="OPENAI_MAX_RETRIES")
    OPENAI_TEMPERATURE: float = Field(0.0, alias="OPENAI_TEMPERATURE")

    TAVILY_API_KEY: str | None = Field(None, alias="TAVILY_API_KEY")

    DB_FILE_PATH: str = Field("data/PatentData.json", alias="DB_FILE_PATH")


config = Config()
