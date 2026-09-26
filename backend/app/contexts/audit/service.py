from __future__ import annotations

from app.contexts.audit.repository import AuditRepoProtocol
from app.contexts.audit.schemas import AuditDomain


class AuditService:
    def __init__(self, repo: AuditRepoProtocol) -> None:
        self._repo = repo

    def log(self, actor_id, method, path, status_code) -> AuditDomain:
        return self._repo.log(actor_id, method, path, status_code)

    def list_recent(self, limit: int = 100) -> list[AuditDomain]:
        return self._repo.list_recent(limit)
