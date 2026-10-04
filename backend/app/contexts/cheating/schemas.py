from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AIDetectionResult(BaseModel):
    is_ai_generated: bool
    confidence: float
    reasoning: str


class CheatingReportOut(BaseModel):
    id: int
    submission_id: int
    student_id: int
    check_type: str
    score: float
    detail: str
    meta: Optional[dict] = None
    status: str
    created_at: datetime


@dataclass(frozen=True)
class CheatingDomain:
    id: int
    submission_id: int
    student_id: int
    check_type: str
    score: float
    detail: str
    meta: Optional[dict]
    status: str
    created_at: datetime
