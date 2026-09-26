from __future__ import annotations

from sqlalchemy.orm import Session

from app.contexts.audit.models import AuditLog
from app.contexts.audit.schemas import AuditDomain


class AuditRepoProtocol:
    def log(self, actor_id: int | None, method: str, path: str, status_code: int) -> AuditDomain: ...
    def list_recent(self, limit: int = 100) -> list[AuditDomain]: ...


class SQLAlchemyAuditRepo(AuditRepoProtocol):
    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _to_domain(a: AuditLog) -> AuditDomain:
        return AuditDomain(a.id, a.actor_id, a.method, a.path, a.status_code, a.created_at)

    def log(self, actor_id, method, path, status_code):
        a = AuditLog(
            actor_id=actor_id, method=method, path=path, status_code=status_code
        )
        self._db.add(a)
        self._db.commit()
        self._db.refresh(a)
        return self._to_domain(a)

    def list_recent(self, limit=100):
        rows = (
            self._db.query(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )
        return [self._to_domain(a) for a in rows]
