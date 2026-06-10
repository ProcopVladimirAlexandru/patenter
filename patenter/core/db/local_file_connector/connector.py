import json

from aiofile import async_open

from patenter.core.db.base_connector.base_connector import BaseDBConnector
from patenter.models.patents import PatentModel
from patenter.core.exceptions.exceptions import ResourceNotFoundException


class LocalFileDBConnector(BaseDBConnector):
    def __init__(self, db_file_path: str):
        super().__init__()
        self._db_file_path = db_file_path

    async def get_patents(self) -> list[PatentModel]:
        async with async_open(self._db_file_path, "rt") as f:
            content = await f.read()
            return [PatentModel(**patent) for patent in json.loads(content)["patents"]]

    async def get_patent(self, patent_uid: str) -> PatentModel:
        async with async_open(self._db_file_path, "rt") as f:
            content = await f.read()
        patents = [PatentModel(**patent) for patent in json.loads(content)["patents"]]
        for patent in patents:
            if patent.publication_number == patent_uid:
                return patent
        raise ResourceNotFoundException(
            f"Patent with publication number {patent_uid} not found"
        )

    @property
    def db_file_path(self):
        return self._db_file_path
