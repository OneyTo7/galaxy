from __future__ import annotations

from app.core.exceptions import DomainError


class VariantError(DomainError):
    def __init__(self, message: str = "变式生成失败") -> None:
        super().__init__(message, code="variant_error")


class NoDiagnosisError(DomainError):
    def __init__(self, message: str = "无诊断结果，无法生成变式") -> None:
        super().__init__(message, code="no_diagnosis")
