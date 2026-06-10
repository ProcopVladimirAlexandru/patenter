from patenter.models.patents import PatentModel
from patenter.models.infringement_detections import (
    InfringementDetectionsModel,
    InfringementDetectionModel,
)
from pydantic import BaseModel, ConfigDict
from typing import Any
from pydantic.alias_generators import to_camel


class ApiResponseModel(BaseModel):
    """
    Base class for all API response models. Inheriting from this class will
    cause all descendants to be serialized with JSON property names in camelCase
    """

    model_config = ConfigDict(
        alias_generator=to_camel, validate_by_name=True, validate_by_alias=True
    )

    def model_dump(
        self,
        by_alias: bool | None = True,  # Default to perform model_dump() as camel case
        **kwargs: Any,
    ) -> dict[str, Any]:
        return super().model_dump(by_alias=by_alias, **kwargs)


class BaseResponse(ApiResponseModel):
    success: bool
    message: str


class DataResponse(BaseResponse):
    data: Any


class PatentDatesResponseModel(ApiResponseModel):
    application: str
    filing: str
    publication: str


class PatentResponseModel(PatentModel, ApiResponseModel):
    dates: PatentDatesResponseModel

    @staticmethod
    def from_internal_model(patent: PatentModel) -> "PatentResponseModel":
        return PatentResponseModel(
            publication_number=patent.publication_number,
            title=patent.title,
            assignees=patent.assignees,
            abstract=patent.abstract,
            claims=patent.claims,
            dates=PatentDatesResponseModel(
                application=patent.dates.application.isoformat(),
                filing=patent.dates.filing.isoformat(),
                publication=patent.dates.publication.isoformat(),
            ),
            status=patent.status,
        )


class PatentsResponseModel(ApiResponseModel):
    patents: list[PatentResponseModel]


class PatentsDataResponse(DataResponse):
    data: PatentsResponseModel


class PatentDataResponse(DataResponse):
    data: PatentResponseModel


class NewInfringementDetectionResponseModel(ApiResponseModel):
    uid: str


class NewInfringementDetectionDataResponse(DataResponse):
    data: NewInfringementDetectionResponseModel


class InfringementDetectionPatentDetailsResponseModel(ApiResponseModel):
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


class InfringementDetectionPerClaimResponseModel(ApiResponseModel):
    claim_number: int
    claim_text: str
    infringing_text: str


class InfringementDetectionResponseModel(ApiResponseModel):
    infringing_enterprise: str
    infringing_product: str
    url: str
    model_uid: str
    per_claim_analysis: list[InfringementDetectionPerClaimResponseModel]

    @staticmethod
    def from_internal_model(
        detection: InfringementDetectionModel,
    ) -> "InfringementDetectionResponseModel":
        return InfringementDetectionResponseModel(**detection.model_dump())


class InfringementDetectionsResponseModel(ApiResponseModel):
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
    task_status: str
    data: InfringementDetectionsResponseModel | None
