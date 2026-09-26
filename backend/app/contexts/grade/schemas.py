from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel


class GradeOut(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    final_score: int
    status: str
    note: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class GradeDomain:
    id: int
    assignment_id: int
    student_id: int
    final_score: int
    status: str
    note: str
    created_at: datetime
    updated_at: datetime
