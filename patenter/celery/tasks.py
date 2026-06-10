from celery import Celery

from patenter.models.infringement_detections import InfringementDetectionsModel
from patenter.workers.infringement_detector import InfringementDetector
from patenter.models.patents import PatentModel

app = Celery("tasks")
app.config_from_object("patenter.celery.celeryconfig")


@app.task(pydantic=True)
def detect_infringement_task(
    patent: PatentModel,
    model_uid: str,
    external_web_access: bool,
    reasoning_effort: str,
    search_context_size: str,
) -> InfringementDetectionsModel:
    return InfringementDetector(
        patent,
        model_uid=model_uid,
        external_web_access=external_web_access,
        reasoning_effort=reasoning_effort,
        search_context_size=search_context_size,
    ).run()


@app.task()
def divide(x: float, y: float) -> float:
    return x / y
