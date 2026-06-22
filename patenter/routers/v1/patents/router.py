import logging
from typing import Annotated
import atexit
import asyncio

from fastapi import APIRouter, HTTPException, Query
from celery import group
from celery.result import GroupResult
from celery import states as celery_states

from patenter.celery.tasks import detect_infringement_task
from patenter.core.exceptions.exceptions import ResourceNotFoundException
from patenter.routers.v1.patents.response_models import (
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
from patenter.models.patents import PatentModel
from patenter.core.db.base_connector.base_connector import BaseDBConnector
from patenter.core.cache.keydb_connector.connector import KeyDBConnector
from patenter.core.cache.base_connector.base_connector import BaseCacheConnector


router = APIRouter(prefix="/api/v1/patents", tags=["patents"])
db_connector: BaseDBConnector = LocalFileDBConnector(db_file_path=config.DB_FILE_PATH)
cache_connector: BaseCacheConnector = KeyDBConnector(url=config.KEYDB_CACHE_URL)
logger = logging.getLogger(__name__)


@router.get("/", response_model=PatentsDataResponse)
async def get_patents():
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
async def get_patent(patent_uid: str):
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
    "/{patent_uid}/infringement_detection_task",
    response_model=NewInfringementDetectionDataResponse,
)
async def detect_infringement(
    patent_uid: str,
    use_cache: Annotated[bool, Query(...)] = True
):
    if use_cache:
        cached_result: str | None = None
        try:
            cached_result = await cache_connector.get(patent_uid)
        except Exception as e:
            logger.error(f"Failed to get cached result for patent {patent_uid}: {e}")
        if cached_result:
            logger.info(f"Returning cached result for patent {patent_uid}")
            return NewInfringementDetectionDataResponse(
                success=True,
                message="Patent received successfully. Will attempt to detect infringement...",
                data=NewInfringementDetectionResponseModel(uid=cached_result,),
            )
        logger.info(f"No cached result found for patent {patent_uid}. Will create task...")

    try:
        patent: PatentModel = await db_connector.get_patent(patent_uid)
    except ResourceNotFoundException:
        raise HTTPException(
            status_code=404, detail=f"Patent with uid {patent_uid} not found"
        )

    try:
        # TODO type this
        task_params_combos: list[dict] = [
            {
                "model_uid": "gpt-5.5",
                "external_web_access": True,
                "reasoning_effort": "high",
                "search_context_size": "high",
            },
            {
                "model_uid": "o3",
                "external_web_access": True,
                "reasoning_effort": "high",
                "search_context_size": "high",
            },
        ]
        task_group = group(
            [
                detect_infringement_task.s(patent.model_dump(), **task_params)
                for task_params in task_params_combos
            ]
        )
        task_group_result: GroupResult = task_group.delay()
        # save so that it can be restored later from id
        task_group_result.save()
    except Exception as ex:
        logger.exception(
            f"Cannot start task for patent {patent.publication_number}", exc_info=ex
        )
        raise HTTPException(status_code=500, detail="Unknown error, co")

    return NewInfringementDetectionDataResponse(
        success=True,
        message="Patent received successfully. Will attempt to detect infringement...",
        data=NewInfringementDetectionResponseModel(
            uid=task_group_result.id,
        ),
    )


@router.get(
    "/{patent_uid}/infringement_detection_task/{task_uid}",
    response_model=InfringementDetectionTaskResultDataResponse,
)
async def get_infringement_detection_task(
    patent_uid: str,
    task_uid: str,
    use_cache: Annotated[bool, Query(...)] = True,
):
    restored_group_result: GroupResult | None = GroupResult.restore(id=task_uid)
    if not restored_group_result:
        raise HTTPException(status_code=404, detail="Task not found")

    if not restored_group_result.ready():
        return InfringementDetectionTaskResultDataResponse(
            success=False,
            message="Task is not ready",
            task_status=celery_states.PENDING,
            data=None,
        )

    all_detections: list[dict] = []
    all_failed: bool = True
    patent: PatentModel | None = None
    for subtask_result in restored_group_result.results:
        if not subtask_result.failed():
            all_failed = False
            if subtask_result.ready():
                all_detections.extend(subtask_result.result["detections"])
                patent = PatentModel(**subtask_result.result["patent"])

    if all_failed or not patent:
        return InfringementDetectionTaskResultDataResponse(
            success=False,
            message="Task failed",
            task_status=celery_states.FAILURE,
            data=None,
        )

    response = InfringementDetectionTaskResultDataResponse(
        success=True,
        message="Task result",
        task_status=celery_states.SUCCESS,
        data=InfringementDetectionsResponseModel.from_internal_model(
            InfringementDetectionsModel(patent=patent, detections=all_detections)
        ),
    )
    if use_cache:
        try:
            await cache_connector.set(patent_uid, task_uid)
            logger.info(f"Cached result for patent {patent_uid}")
        except Exception as e:
            logger.error(f"Failed to cache result for patent {patent_uid}: {e}")
    return response
