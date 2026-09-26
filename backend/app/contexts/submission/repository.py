from __future__ import annotations

from sqlalchemy.orm import Session

from app.contexts.submission.models import Submission
from app.contexts.submission.schemas import SubmissionDomain


class SubmissionRepoProtocol:
    def create(
        self,
        user_id: int,
        assignment_id: int,
        code: str,
        lang: str,
        status: str,
        score: int,
    ) -> SubmissionDomain: ...
    def get(self, submission_id: int) -> SubmissionDomain | None: ...
    def update_status_score(self, submission_id: int, status: str, score: int) -> SubmissionDomain | None: ...
    def list_by_assignment(self, assignment_id: int) -> list[SubmissionDomain]: ...


class SQLAlchemySubmissionRepo(SubmissionRepoProtocol):
    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _to_domain(s: Submission) -> SubmissionDomain:
        return SubmissionDomain(
            s.id, s.user_id, s.assignment_id, s.code, s.lang,
            s.status, s.score, s.last_result, s.created_at,
        )

    def create(self, user_id, assignment_id, code, lang, status, score):
        s = Submission(
            user_id=user_id,
            assignment_id=assignment_id,
            code=code,
            lang=lang,
            status=status,
            score=score,
        )
        self._db.add(s)
        self._db.commit()
        self._db.refresh(s)
        return self._to_domain(s)

    def update_status_score(self, submission_id, status, score):
        s = self._db.get(Submission, submission_id)
        if not s:
            return None
        s.status = status
        s.score = score
        self._db.commit()
        self._db.refresh(s)
        return self._to_domain(s)

    def get(self, submission_id):
        s = self._db.get(Submission, submission_id)
        return self._to_domain(s) if s else None

    def list_by_assignment(self, assignment_id):
        rows = (
            self._db.query(Submission)
            .filter(Submission.assignment_id == assignment_id)
            .order_by(Submission.created_at.desc())
            .all()
        )
        return [self._to_domain(s) for s in rows]
