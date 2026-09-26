from __future__ import annotations

from app.core.exceptions import DomainError


class CheatingError(DomainError):
    def __init__(self, message: str = "反作弊检测失败") -> None:
        super().__init__(message, code="cheating_error")
