from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class KnowledgeTagIn(BaseModel):
    code: str = Field(min_length=1, max_length=32)
    weight: float = Field(default=1.0, ge=0.1, le=2.0)


class KnowledgeTagOut(BaseModel):
    knowledge_point_id: int
    code: str
    name: str
    category: str
    weight: float


class KnowledgeTagUpdate(BaseModel):
    items: list[KnowledgeTagIn] = []


class KnowledgePointOut(BaseModel):
    id: int
    code: str
    name: str
    category: str
    sort_order: int


class MasteryCellOut(BaseModel):
    user_id: int
    knowledge_point_id: int
    code: str
    name: str
    category: str
    mastery: Optional[float] = None
    attempts: int = 0
    correct: int = 0
    status: str = "untracked"


class MatrixStudentOut(BaseModel):
    user_id: int
    display_name: str


class MasteryMatrixOut(BaseModel):
    course_id: int
    students: list[MatrixStudentOut] = []
    cells: list[MasteryCellOut] = []


class MasteryEventOut(BaseModel):
    id: int
    knowledge_point_id: int
    code: str
    name: str
    source: str
    observed: bool
    mastery_before: float
    mastery_after: float
    submission_id: int
    created_at: datetime


class StudentMasteryOut(BaseModel):
    course_id: int
    user_id: int
    points: list[MasteryCellOut] = []


class MasterySummaryItem(BaseModel):
    knowledge_point_id: int
    code: str
    name: str
    category: str
    avg_mastery: float
    student_count: int
    at_risk_count: int


@dataclass(frozen=True)
class KnowledgePointDomain:
    id: int
    code: str
    name: str
    category: str
    sort_order: int
    p_init: float
    p_transit: float
    p_slip: float
    p_guess: float


@dataclass(frozen=True)
class AssignmentKnowledgePointDomain:
    assignment_id: int
    knowledge_point_id: int
    weight: float


@dataclass(frozen=True)
class StudentMasteryDomain:
    id: int
    user_id: int
    knowledge_point_id: int
    mastery: float
    attempts: int
    correct: int
    status: str
    first_seen_at: datetime
    last_updated_at: datetime


@dataclass(frozen=True)
class MasteryEventDomain:
    id: int
    user_id: int
    knowledge_point_id: int
    submission_id: int
    source: str
    observed: bool
    mastery_before: float
    mastery_after: float
    created_at: datetime
