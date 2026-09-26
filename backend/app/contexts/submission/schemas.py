from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.contexts.evaluation.schemas import CaseResultOut


class SubmissionCreate(BaseModel):
    assignment_id: int
    code: str = Field(min_length=1)
    lang: str = Field(default="python", pattern="^(java|python)$")


class SubmissionOut(BaseModel):
    id: int
    user_id: int
    assignment_id: int
    lang: str
    status: str
    score: int
    created_at: datetime


class EvaluationOut(BaseModel):
    submission_id: int
    assignment_id: int
    score: int
    status: str
    results: list[CaseResultOut] = []


@dataclass(frozen=True)
class SubmissionDomain:
    id: int
    user_id: int
    assignment_id: int
    code: str
    lang: str
    status: str
    score: int
    last_result: Optional[list]
    created_at: datetime
