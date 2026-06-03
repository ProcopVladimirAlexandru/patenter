from datetime import date
from pydantic import BaseModel


class PatentDatesModel(BaseModel):
    application: date
    filing: date
    publication: date


class PatentClaimModel(BaseModel):
    number: int
    preamble: str
    text: str


class PatentModel(BaseModel):
    publication_number: str
    title: str
    abstract: str
    claims: list[PatentClaimModel]
    dates: PatentDatesModel
    status: str
