from patenter.models.patents import PatentModel
from patenter.models.infringement_detections import (
    InfringementDetectionsModel,
    InfringementDetectionModel,
)
from pydantic import BaseModel
from typing import Any


class BaseResponse(BaseModel):
    success: bool
    message: str


class DataResponse(BaseResponse):
    data: Any


class PatentDatesResponseModel(BaseModel):
    application: str
    filing: str
    publication: str


class PatentResponseModel(PatentModel):
    dates: PatentDatesResponseModel

    @staticmethod
    def from_internal_model(patent: PatentModel) -> "PatentResponseModel":
        return PatentResponseModel(
            publication_number=patent.publication_number,
            title=patent.title,
            abstract=patent.abstract,
            claims=patent.claims,
            dates=PatentDatesResponseModel(
                application=patent.dates.application.isoformat(),
                filing=patent.dates.filing.isoformat(),
                publication=patent.dates.publication.isoformat(),
            ),
            status=patent.status,
        )


class PatentsResponseModel(BaseModel):
    patents: list[PatentResponseModel]


class PatentsDataResponse(DataResponse):
    data: PatentsResponseModel


class NewInfringementDetectionResponseModel(BaseModel):
    uid: str


class NewInfringementDetectionDataResponse(DataResponse):
    data: NewInfringementDetectionResponseModel


class InfringementDetectionPatentDetailsResponseModel(BaseModel):
    publication_number: str
    title: str
    dates: PatentDatesResponseModel

    @staticmethod
    def from_internal_model(
        patent: PatentModel,
    ) -> "InfringementDetectionPatentDetailsResponseModel":
        return InfringementDetectionPatentDetailsResponseModel(
            publication_number=patent.publication_number,
            title=patent.title,
            dates=PatentDatesResponseModel(
                application=patent.dates.application.isoformat(),
                filing=patent.dates.filing.isoformat(),
                publication=patent.dates.publication.isoformat(),
            ),
        )


class InfringementDetectionPerClaimResponseModel(BaseModel):
    claim_number: int
    claim_text: str
    infringing_text: str


class InfringementDetectionResponseModel(BaseModel):
    infringing_enterprise: str
    infringing_product: str
    link: str
    per_claim_analysis: list[InfringementDetectionPerClaimResponseModel] | None = None

    @staticmethod
    def from_internal_model(
        detection: InfringementDetectionModel,
    ) -> "InfringementDetectionResponseModel":
        return InfringementDetectionResponseModel(**detection.model_dump())


class InfringementDetectionsResponseModel(BaseModel):
    patent: InfringementDetectionPatentDetailsResponseModel
    detections: list[InfringementDetectionResponseModel]

    @staticmethod
    def from_internal_model(
        detections: InfringementDetectionsModel,
    ) -> "InfringementDetectionsResponseModel":
        return InfringementDetectionsResponseModel(
            patent=InfringementDetectionPatentDetailsResponseModel.from_internal_model(
                detections.patent
            ),
            detections=[
                InfringementDetectionResponseModel.from_internal_model(detection)
                for detection in detections.detections
            ],
        )


class InfringementDetectionTaskResultDataResponse(DataResponse):
    data: InfringementDetectionsResponseModel
