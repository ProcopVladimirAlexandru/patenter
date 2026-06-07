import json

from aiofile import async_open

from patenter.core.db.base_connector.base_connector import BaseDBConnector
from patenter.models.patents import PatentModel


class LocalFileDBConnector(BaseDBConnector):
    def __init__(self, db_file_path: str):
        super().__init__()
        self._db_file_path = db_file_path

    async def get_patents(self) -> list[PatentModel]:
        async with async_open(self._db_file_path, "rt") as f:
            content = await f.read()
            return [PatentModel(**patent) for patent in json.loads(content)["patents"]]

    @property
    def db_file_path(self):
        return self._db_file_path
