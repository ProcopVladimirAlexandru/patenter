from datetime import date
from pydantic import BaseModel


class PatentDatesModel(BaseModel):
    application: date
    filing: date
    publication: date


class PatentClaimModel(BaseModel):
    number: int
    preamble: str | None
    text: str | None
    elements: list[str]


class PatentModel(BaseModel):
    publication_number: str
    assignees: list[str]
    title: str
    abstract: str
    claims: list[PatentClaimModel]
    dates: PatentDatesModel
    status: str
