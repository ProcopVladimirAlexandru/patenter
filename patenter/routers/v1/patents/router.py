from celery.result import AsyncResult

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from patenter.celery.tasks import detect_infringement_task
from patenter.routers.v1.patents.request_models import PatentRequestModel


router = APIRouter(prefix="/api/v1/patents", tags=["patents"])


@router.post("/infringement_detection_task")
async def detect_infringement(patent: PatentRequestModel) -> JSONResponse:
    task: AsyncResult = detect_infringement_task.delay(
        patent.to_internal_model().model_dump_json()
    )
    return JSONResponse(
        {
            "message": "Patent received successfully. Will attempt to detect infringement...",
            "data": {
                "task_id": task.id,
            },
        }
    )


@router.get("/infringement_detection_task/{task_id}")
async def get_infringement_detection_task(task_id: str) -> JSONResponse:
    task: AsyncResult = AsyncResult(task_id)
    if not task.ready():
        return JSONResponse(
            {
                "message": "Task is still running",
                "data": {
                    "task_id": task_id,
                    "status": task.status,
                },
            }
        )
    if task.failed():
        return JSONResponse(
            {
                "message": "Task failed",
                "data": {
                    "task_id": task_id,
                    "status": task.status,
                    "result": str(task.result),
                },
            }
        )
    return JSONResponse(
        {
            "message": "Task result",
            "data": {
                "task_id": task_id,
                "status": task.status,
                "result": task.result,
            },
        }
    )
