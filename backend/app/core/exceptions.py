class DomainError(Exception):
    def __init__(self, message: str, code: str = "domain_error") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class NotFoundError(DomainError):
    def __init__(self, message: str = "not found") -> None:
        super().__init__(message, code="not_found")


class AuthError(DomainError):
    def __init__(self, message: str = "unauthorized") -> None:
        super().__init__(message, code="unauthorized")


class ConflictError(DomainError):
    def __init__(self, message: str = "conflict") -> None:
        super().__init__(message, code="conflict")


class ForbiddenError(DomainError):
    def __init__(self, message: str = "无权操作该资源") -> None:
        super().__init__(message, code="forbidden")
