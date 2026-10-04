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
    difficulty: str = "easy"
    practice_assignment_id: Optional[int] = None


class VariantResult(BaseModel):
    title: str
    description: str
    cases: list
    scoring_points: list
    lang: str
    difficulty: str = "easy"


@dataclass(frozen=True)
class VariantDomain:
    id: int
    submission_id: int
    title: str
    description: str
    cases: Optional[list]
    scoring_points: Optional[list]
    lang: str
    difficulty: str
    origin_misconception_id: Optional[int]
    practice_assignment_id: Optional[int]
    created_at: datetime
