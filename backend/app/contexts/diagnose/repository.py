from __future__ import annotations

from sqlalchemy.orm import Session

from app.contexts.diagnose.models import Misconception
from app.contexts.diagnose.schemas import GenerateResult, MisconceptionDomain


class MisconceptionRepoProtocol:
    def create(self, submission_id: int, result: GenerateResult) -> MisconceptionDomain: ...
    def list_by_submission(self, submission_id: int) -> list[MisconceptionDomain]: ...


class SQLAlchemyMisconceptionRepo(MisconceptionRepoProtocol):
    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _to_domain(m: Misconception) -> MisconceptionDomain:
        return MisconceptionDomain(
            m.id, m.submission_id, m.misconception_type, m.evidence,
            m.knowledge_point, m.confidence, m.created_at,
        )

    def create(self, submission_id, result):
        m = Misconception(
            submission_id=submission_id,
            misconception_type=result.misconception_type,
            evidence=result.evidence,
            knowledge_point=result.knowledge_point,
            confidence=result.confidence,
        )
        self._db.add(m)
        self._db.commit()
        self._db.refresh(m)
        return self._to_domain(m)

    def list_by_submission(self, submission_id):
        rows = (
            self._db.query(Misconception)
            .filter(Misconception.submission_id == submission_id)
            .order_by(Misconception.created_at.desc())
            .all()
        )
        return [self._to_domain(m) for m in rows]
