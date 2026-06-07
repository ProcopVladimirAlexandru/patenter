from celery import Celery

from patenter.models.infringement_detections import InfringementDetectionsModel
from patenter.workers.infringement_detector import InfringementDetector
from patenter.models.patents import PatentModel

app = Celery("tasks")
app.config_from_object("patenter.celery.celeryconfig")


@app.task(pydantic=True)
def detect_infringement_task(patent: PatentModel) -> InfringementDetectionsModel:
    return InfringementDetector(patent).run()
