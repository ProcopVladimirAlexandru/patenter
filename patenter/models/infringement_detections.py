from pydantic import BaseModel
from patenter.models.patents import PatentModel


class InfringementDetectionPerClaimModel(BaseModel):
    claim_number: int
    claim_text: str
    infringing_text: str


class InfringementDetectionModel(BaseModel):
    infringing_enterprise: str
    infringing_product: str
    url: str
    model_uid: str
    per_claim_analysis: list[InfringementDetectionPerClaimModel]


class InfringementDetectionsModel(BaseModel):
    patent: PatentModel
    detections: list[InfringementDetectionModel]
