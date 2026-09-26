from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel


class DiagnoseOut(BaseModel):
    submission_id: int
    misconception_type: str
    evidence: str
    knowledge_point: str
    confidence: float


class MisconceptionOut(DiagnoseOut):
    id: int
    created_at: datetime


class GenerateResult(BaseModel):
    misconception_type: str
    evidence: str
    knowledge_point: str
    confidence: float


@dataclass(frozen=True)
class MisconceptionDomain:
    id: int
    submission_id: int
    misconception_type: str
    evidence: str
    knowledge_point: str
    confidence: float
    created_at: datetime
