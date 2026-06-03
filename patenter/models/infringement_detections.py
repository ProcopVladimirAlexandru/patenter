from pydantic import BaseModel


class InfringementDetectionModel(BaseModel):
    link: str
    confidence: float
