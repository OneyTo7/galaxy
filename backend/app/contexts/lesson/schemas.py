from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LessonOut(BaseModel):
    id: int
    course_id: int
    title: str
    sort_order: int
    content: str
    assignment_id: Optional[int] = None
    created_at: datetime


class LessonListItem(BaseModel):
    id: int
    course_id: int
    title: str
    sort_order: int
    assignment_id: Optional[int] = None


class LessonCreate(BaseModel):
    course_id: int
    title: str
    content: str = ""
    sort_order: int = 0
    assignment_id: Optional[int] = None


@dataclass(frozen=True)
class LessonDomain:
    id: int
    course_id: int
    title: str
    sort_order: int
    content: str
    assignment_id: Optional[int]
    created_at: datetime
