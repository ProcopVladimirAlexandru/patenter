from celery import Celery

from patenter.workers.infringement_detector import detect_infringement
from patenter.models.patents import PatentModel

app = Celery("tasks")
app.config_from_object("patenter.celery.celeryconfig")


@app.task
def detect_infringement_task(patent_json: str):
    patent: PatentModel = PatentModel.model_validate_json(patent_json)
    return detect_infringement(patent)
