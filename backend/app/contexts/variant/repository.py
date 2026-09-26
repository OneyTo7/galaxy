from __future__ import annotations

from sqlalchemy.orm import Session

from app.contexts.variant.models import VariantExercise
from app.contexts.variant.schemas import VariantDomain, VariantResult


class VariantRepoProtocol:
    def create(self, submission_id: int, result: VariantResult) -> VariantDomain: ...
    def list_by_submission(self, submission_id: int) -> list[VariantDomain]: ...


class SQLAlchemyVariantRepo(VariantRepoProtocol):
    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _to_domain(v: VariantExercise) -> VariantDomain:
        return VariantDomain(
            v.id, v.submission_id, v.title, v.description,
            v.cases, v.scoring_points, v.lang, v.created_at,
        )

    def create(self, submission_id, result):
        v = VariantExercise(
            submission_id=submission_id,
            title=result.title,
            description=result.description,
            cases=result.cases,
            scoring_points=result.scoring_points,
            lang=result.lang,
        )
        self._db.add(v)
        self._db.commit()
        self._db.refresh(v)
        return self._to_domain(v)

    def list_by_submission(self, submission_id):
        rows = (
            self._db.query(VariantExercise)
            .filter(VariantExercise.submission_id == submission_id)
            .order_by(VariantExercise.created_at.desc())
            .all()
        )
        return [self._to_domain(v) for v in rows]
