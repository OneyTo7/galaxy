from __future__ import annotations

from pydantic import BaseModel


class MisconceptionStat(BaseModel):
    misconception_type: str
    count: int


class KnowledgeStat(BaseModel):
    knowledge_point: str
    count: int


class StudentStat(BaseModel):
    user_id: int
    score: int
    misconception_type: str = ""


class LearningReport(BaseModel):
    assignment_id: int
    submission_count: int
    avg_score: float
    misconception_stats: list[MisconceptionStat] = []
    knowledge_stats: list[KnowledgeStat] = []
    students: list[StudentStat] = []


class CourseReport(BaseModel):
    course_id: int
    assignment_count: int
    submission_count: int
    avg_score: float
    misconception_stats: list[MisconceptionStat] = []
    knowledge_stats: list[KnowledgeStat] = []
    students: list[StudentStat] = []
