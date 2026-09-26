from __future__ import annotations

from app.core.exceptions import DomainError


class MoMAUnavailableError(DomainError):
    def __init__(self, message: str = "MoMA 不可用") -> None:
        super().__init__(message, code="moma_unavailable")


class MisconceptionParseError(DomainError):
    def __init__(self, message: str = "诊断结果解析失败") -> None:
        super().__init__(message, code="diagnose_parse_error")


class ProviderError(DomainError):
    def __init__(self, message: str, *, retryable: bool = False, code: str | None = None) -> None:
        super().__init__(message, code=code or "provider_error")
        self.retryable = retryable
