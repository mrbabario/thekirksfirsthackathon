from pydantic import BaseModel


class Claim(BaseModel):
    claim: str
    language: str
    entities: list[str]
    subject: str
    predicate: str
    object: str


class Reference(BaseModel):
    pmid: str
    title: str
    abstract: str
    journal: str
    year: str
    language: str
    similarity: float


class Verdict(BaseModel):
    verdict: str
    explanation: str
    references: list[str]
