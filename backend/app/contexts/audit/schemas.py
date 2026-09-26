from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: int
    actor_id: Optional[int] = None
    method: str
    path: str
    status_code: int
    created_at: datetime


@dataclass(frozen=True)
class AuditDomain:
    id: int
    actor_id: Optional[int]
    method: str
    path: str
    status_code: int
    created_at: datetime
