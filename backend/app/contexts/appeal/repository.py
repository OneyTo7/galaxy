from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.contexts.appeal.models import Appeal
from app.contexts.appeal.schemas import AppealDomain


class AppealRepoProtocol:
    def create(self, submission_id: int, student_id: int, reason: str) -> AppealDomain: ...
    def get(self, appeal_id: int) -> AppealDomain | None: ...
    def list_pending(self) -> list[AppealDomain]: ...
    def list_by_student(self, student_id: int) -> list[AppealDomain]: ...
    def review(
        self, appeal_id: int, reviewer_id: int, approved: bool, comment: str, new_score: int | None
    ) -> AppealDomain | None: ...


class SQLAlchemyAppealRepo(AppealRepoProtocol):
    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _to_domain(a: Appeal) -> AppealDomain:
        return AppealDomain(
            a.id, a.submission_id, a.student_id, a.reason, a.status,
            a.approved, a.review_comment, a.reviewer_id, a.new_score,
            a.created_at, a.reviewed_at,
        )

    def create(self, submission_id, student_id, reason):
        a = Appeal(submission_id=submission_id, student_id=student_id, reason=reason)
        self._db.add(a)
        self._db.commit()
        self._db.refresh(a)
        return self._to_domain(a)

    def get(self, appeal_id):
        a = self._db.get(Appeal, appeal_id)
        return self._to_domain(a) if a else None

    def list_pending(self):
        rows = (
            self._db.query(Appeal)
            .filter(Appeal.status == "pending")
            .order_by(Appeal.created_at.asc())
            .all()
        )
        return [self._to_domain(a) for a in rows]

    def list_by_student(self, student_id):
        rows = (
            self._db.query(Appeal)
            .filter(Appeal.student_id == student_id)
            .order_by(Appeal.created_at.desc())
            .all()
        )
        return [self._to_domain(a) for a in rows]

    def review(self, appeal_id, reviewer_id, approved, comment, new_score):
        a = self._db.get(Appeal, appeal_id)
        if not a:
            return None
        a.status = "resolved"
        a.approved = approved
        a.review_comment = comment
        a.reviewer_id = reviewer_id
        a.new_score = new_score
        a.reviewed_at = datetime.now(timezone.utc)
        self._db.commit()
        self._db.refresh(a)
        return self._to_domain(a)
