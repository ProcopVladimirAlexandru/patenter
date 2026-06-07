import logging
from celery.result import AsyncResult

from fastapi import APIRouter, HTTPException
from patenter.celery.tasks import detect_infringement_task
from patenter.core.exceptions.exceptions import ResourceNotFoundException
from patenter.routers.v1.patents.request_models import PatentRequestModel
from patenter.routers.v1.patents.response_models import (
    DataResponse,
    PatentResponseModel,
    PatentsDataResponse,
    PatentsResponseModel,
    PatentDataResponse,
    NewInfringementDetectionDataResponse,
    InfringementDetectionsResponseModel,
    InfringementDetectionTaskResultDataResponse,
    NewInfringementDetectionResponseModel,
)
from patenter.core.db.local_file_connector.connector import LocalFileDBConnector
from patenter.config.config import config
from patenter.models.infringement_detections import InfringementDetectionsModel
from patenter.core.db.base_connector.base_connector import BaseDBConnector


router = APIRouter(prefix="/api/v1/patents", tags=["patents"])
db_connector: BaseDBConnector = LocalFileDBConnector(db_file_path=config.DB_FILE_PATH)
logger = logging.getLogger(__name__)


@router.get("/", response_model=PatentsDataResponse)
async def get_patents() -> PatentsDataResponse:
    patents = await db_connector.get_patents()
    return PatentsDataResponse(
        success=True,
        message="Patents retrieved successfully",
        data=PatentsResponseModel(
            patents=[
                PatentResponseModel.from_internal_model(patent) for patent in patents
            ]
        ),
    )


@router.get("/{patent_uid}", response_model=PatentDataResponse)
async def get_patent(patent_uid: str) -> PatentDataResponse:
    try:
        patent = await db_connector.get_patent(patent_uid)
    except ResourceNotFoundException:
        raise HTTPException(
            status_code=404, detail=f"Patent with uid {patent_uid} not found"
        )

    return PatentDataResponse(
        success=True,
        message="Patent retrieved successfully",
        data=PatentResponseModel.from_internal_model(patent),
    )


@router.post(
    "/infringement_detection_task", response_model=NewInfringementDetectionDataResponse
)
async def detect_infringement(
    patent: PatentRequestModel,
) -> NewInfringementDetectionDataResponse:
    try:
        task: AsyncResult = detect_infringement_task.delay(
            patent.to_internal_model().model_dump()
        )
    except Exception as ex:
        logger.exception(
            f"Cannot start task for patent {patent.publication_number}", exc_info=ex
        )
        raise HTTPException(status_code=500, detail="Unknown error, co")

    return NewInfringementDetectionDataResponse(
        success=True,
        message="Patent received successfully. Will attempt to detect infringement...",
        data=NewInfringementDetectionResponseModel(
            uid=task.id,
        ),
    )


@router.get(
    "/infringement_detection_task/{task_id}",
    response_model=InfringementDetectionTaskResultDataResponse,
)
async def get_infringement_detection_task(task_id: str) -> DataResponse:
    task: AsyncResult = AsyncResult(task_id)
    if task.failed():
        return DataResponse(
            success=False,
            message="Task failed",
            data={
                "task_id": task_id,
                "status": task.status,
                "result": str(task.result),
            },
        )

    if not task.ready():
        return DataResponse(
            success=False,
            message="Task is still running",
            data={
                "task_id": task_id,
                "status": task.status,
            },
        )

    return InfringementDetectionTaskResultDataResponse(
        success=True,
        message="Task result",
        data=InfringementDetectionsResponseModel.from_internal_model(
            InfringementDetectionsModel(**task.result)
        ),
    )
