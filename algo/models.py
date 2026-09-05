from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Verdict = Literal[
    "SUPPORTED",
    "CONTRADICTED",
    "MIXED",
    "INSUFFICIENT",
]


@dataclass
class Claim:
    text: str
    subject: str
    predicate: str
    object: str
    entities: list[str]
    language: str


@dataclass
class Paper:
    pmid: str
    title: str
    abstract: str
    journal: str
    year: int | None
    language: str


@dataclass
class Reference:
    number: int
    pmid: str
    title: str
    abstract: str
    journal: str
    year: int | None


@dataclass
class ExplanationPart:
    text: str
    references: list[int]


@dataclass
class ClaimResult:
    claim: Claim
    verdict: Verdict
    explanation: list[ExplanationPart]
    references: list[Reference]


@dataclass
class ArticleResult:
    article_hash: str
    language: str
    claims: list[ClaimResult]
