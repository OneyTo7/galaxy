from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel


class DiagnoseOut(BaseModel):
    submission_id: int
    misconception_type: str
    evidence: str
    knowledge_point: str
    knowledge_point_code: str = ""
    knowledge_point_id: int | None = None
    confidence: float
    evidence_validated: bool = True
    status: str = "open"


class MisconceptionOut(DiagnoseOut):
    id: int
    created_at: datetime


class GenerateResult(BaseModel):
    misconception_type: str
    evidence: str
    knowledge_point: str
    # 受控知识点编码：要求模型从给定列表中选；缺失时由 service 兜底解析
    knowledge_point_code: str = ""
    confidence: float


@dataclass(frozen=True)
class MisconceptionDomain:
    id: int
    submission_id: int
    user_id: int | None
    misconception_type: str
    evidence: str
    knowledge_point: str
    knowledge_point_id: int | None
    confidence: float
    evidence_validated: bool
    status: str
    overcome_at: datetime | None
    created_at: datetime
