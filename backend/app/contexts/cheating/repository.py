from __future__ import annotations

from sqlalchemy.orm import Session

from app.contexts.cheating.models import CheatingReport
from app.contexts.cheating.schemas import CheatingDomain


class CheatingRepoProtocol:
    def create(
        self, submission_id: int, student_id: int, check_type: str, score: float, detail: str, status: str
    ) -> CheatingDomain: ...
    def list_by_submission(self, submission_id: int) -> list[CheatingDomain]: ...


class SQLAlchemyCheatingRepo(CheatingRepoProtocol):
    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _to_domain(r: CheatingReport) -> CheatingDomain:
        return CheatingDomain(
            r.id, r.submission_id, r.student_id, r.check_type,
            r.score, r.detail, r.status, r.created_at,
        )

    def create(self, submission_id, student_id, check_type, score, detail, status):
        r = CheatingReport(
            submission_id=submission_id,
            student_id=student_id,
            check_type=check_type,
            score=score,
            detail=detail,
            status=status,
        )
        self._db.add(r)
        self._db.commit()
        self._db.refresh(r)
        return self._to_domain(r)

    def list_by_submission(self, submission_id):
        rows = (
            self._db.query(CheatingReport)
            .filter(CheatingReport.submission_id == submission_id)
            .order_by(CheatingReport.created_at.desc())
            .all()
        )
        return [self._to_domain(r) for r in rows]
