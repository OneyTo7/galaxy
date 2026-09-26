from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class VariantOut(BaseModel):
    id: int
    submission_id: int
    title: str
    description: str
    cases: list = []
    scoring_points: list = []
    lang: str


class VariantResult(BaseModel):
    title: str
    description: str
    cases: list
    scoring_points: list
    lang: str


@dataclass(frozen=True)
class VariantDomain:
    id: int
    submission_id: int
    title: str
    description: str
    cases: Optional[list]
    scoring_points: Optional[list]
    lang: str
    created_at: datetime
