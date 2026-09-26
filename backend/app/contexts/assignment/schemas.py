from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TestCaseIn(BaseModel):
    name: str = ""
    input: str = ""
    expected_output: str = ""
    is_hidden: bool = False
    weight: int = 1
    order: int = 0


class TestCaseOut(TestCaseIn):
    id: int
    assignment_id: int


class AssignmentCreate(BaseModel):
    course_id: Optional[int] = None
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    lang: str = Field(default="python", pattern="^(java|python)$")
    scoring_rubric: str = ""
    reference_code: str = ""
    test_cases: list[TestCaseIn] = []


class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    scoring_rubric: Optional[str] = None
    reference_code: Optional[str] = None
    status: Optional[str] = None


class AssignmentOut(BaseModel):
    id: int
    teacher_id: int
    course_id: Optional[int] = None
    title: str
    description: str
    lang: str
    scoring_rubric: str
    reference_code: str
    status: str
    created_at: datetime
    test_cases: list[TestCaseOut] = []


@dataclass(frozen=True)
class TestCaseDomain:
    id: int
    assignment_id: int
    name: str
    input: str
    expected_output: str
    is_hidden: bool
    weight: int
    order: int


@dataclass(frozen=True)
class AssignmentDomain:
    id: int
    teacher_id: int
    course_id: Optional[int]
    title: str
    description: str
    lang: str
    scoring_rubric: str
    reference_code: str
    status: str
    created_at: datetime
    test_cases: list[TestCaseDomain] = field(default_factory=list)
