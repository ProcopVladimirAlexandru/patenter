from pydantic import BaseModel
from patenter.models.patents import PatentModel


class InfringementDetectionModel(BaseModel):
    infringing_enterprise: str
    infringing_product: str
    link: str
    per_claim_analysis: None = None


class InfringementDetectionsModel(BaseModel):
    patent: PatentModel
    detections: list[InfringementDetectionModel]
