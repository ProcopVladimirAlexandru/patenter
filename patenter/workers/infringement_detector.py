import time
import random

from patenter.models.patents import PatentModel
from patenter.models.infringement_detections import InfringementDetectionModel


def detect_infringement(
    patent: PatentModel, sleep_seconds: int = 5, exception_probability: float = 0.2
) -> list[InfringementDetectionModel]:
    time.sleep(sleep_seconds)
    if random.random() < exception_probability:
        raise Exception(
            f"Infringement detection failed in patent '{patent.publication_number}'"
        )
    models: list[InfringementDetectionModel] = [
        InfringementDetectionModel(link="https://example.com", confidence=0.9),
        InfringementDetectionModel(link="https://chartop.app", confidence=0.8),
    ]
    return [m.model_dump() for m in models]
