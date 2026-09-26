from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel


@dataclass(frozen=True)
class CaseResult:
    case_id: int
    passed: bool
    stdout: str
    stderr: str
    timed_out: bool
    elapsed_ms: int


class CaseResultOut(BaseModel):
    case_id: int
    passed: bool
    stdout: str
    stderr: str
    timed_out: bool
    elapsed_ms: int
