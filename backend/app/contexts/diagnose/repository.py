from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.contexts.diagnose.models import Misconception
from app.contexts.diagnose.schemas import GenerateResult, MisconceptionDomain


class MisconceptionRepoProtocol:
    def create(
        self,
        submission_id: int,
        user_id: int | None,
        result: GenerateResult,
        knowledge_point_id: int | None,
        evidence_validated: bool,
    ) -> MisconceptionDomain: ...
    def list_by_submission(self, submission_id: int) -> list[MisconceptionDomain]: ...
    def mark_open_overcome(self, user_id: int, knowledge_point_id: int) -> int: ...


class SQLAlchemyMisconceptionRepo(MisconceptionRepoProtocol):
    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _to_domain(m: Misconception) -> MisconceptionDomain:
        return MisconceptionDomain(
            m.id, m.submission_id, m.user_id, m.misconception_type,
            m.evidence, m.knowledge_point, m.knowledge_point_id, m.confidence,
            m.evidence_validated, m.status, m.overcome_at, m.created_at,
        )

    def create(
        self, submission_id, user_id, result, knowledge_point_id, evidence_validated
    ):
        m = Misconception(
            submission_id=submission_id,
            user_id=user_id,
            misconception_type=result.misconception_type,
            evidence=result.evidence,
            knowledge_point=result.knowledge_point,
            knowledge_point_id=knowledge_point_id,
            confidence=result.confidence,
            evidence_validated=evidence_validated,
            status="open",
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

    def mark_open_overcome(self, user_id, knowledge_point_id):
        rows = (
            self._db.query(Misconception)
            .filter(
                Misconception.user_id == user_id,
                Misconception.knowledge_point_id == knowledge_point_id,
                Misconception.status == "open",
            )
            .all()
        )
        now = datetime.now()
        for r in rows:
            r.status = "overcome"
            r.overcome_at = now
        if rows:
            self._db.commit()
        return len(rows)
