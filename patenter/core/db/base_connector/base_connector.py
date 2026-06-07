from abc import ABC, abstractmethod

from patenter.models.patents import PatentModel


class BaseDBConnector(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def get_patents(self) -> list[PatentModel]:
        raise NotImplementedError

    @abstractmethod
    async def get_patent(self, patent_uid: str) -> PatentModel:
        raise NotImplementedError
