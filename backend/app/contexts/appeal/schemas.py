from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AppealCreate(BaseModel):
    reason: str = Field(min_length=1)


class AppealReview(BaseModel):
    approved: bool
    comment: str = ""
    new_score: Optional[int] = None


class AppealOut(BaseModel):
    id: int
    submission_id: int
    student_id: int
    reason: str
    status: str
    approved: Optional[bool] = None
    review_comment: str
    reviewer_id: Optional[int] = None
    new_score: Optional[int] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None


@dataclass(frozen=True)
class AppealDomain:
    id: int
    submission_id: int
    student_id: int
    reason: str
    status: str
    approved: Optional[bool]
    review_comment: str
    reviewer_id: Optional[int]
    new_score: Optional[int]
    created_at: datetime
    reviewed_at: Optional[datetime]
