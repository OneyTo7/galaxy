from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    code: str = Field(min_length=1, max_length=32)


class CourseOut(BaseModel):
    id: int
    teacher_id: int
    name: str
    code: str
    created_at: datetime


class ClassCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)


class ClassOut(BaseModel):
    id: int
    course_id: int
    name: str
    created_at: datetime


class EnrollmentOut(BaseModel):
    id: int
    class_id: int
    student_id: int
    created_at: datetime


@dataclass(frozen=True)
class CourseDomain:
    id: int
    teacher_id: int
    name: str
    code: str
    created_at: datetime


@dataclass(frozen=True)
class ClassDomain:
    id: int
    course_id: int
    name: str
    created_at: datetime


@dataclass(frozen=True)
class EnrollmentDomain:
    id: int
    class_id: int
    student_id: int
    created_at: datetime
