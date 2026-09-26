from __future__ import annotations

from app.core.exceptions import DomainError


class GenerationError(DomainError):
    def __init__(self, message: str = "命题失败") -> None:
        super().__init__(message, code="generation_error")
