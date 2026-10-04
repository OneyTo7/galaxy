from __future__ import annotations

from sqlalchemy.orm import Session

from app.contexts.variant.models import VariantExercise
from app.contexts.variant.schemas import VariantDomain, VariantResult


class VariantRepoProtocol:
    def create(
        self,
        submission_id: int,
        result: VariantResult,
        origin_misconception_id: int | None,
        practice_assignment_id: int | None,
    ) -> VariantDomain: ...
    def list_by_submission(self, submission_id: int) -> list[VariantDomain]: ...
    def latest_for_misconception(self, misconception_id: int) -> VariantDomain | None: ...


class SQLAlchemyVariantRepo(VariantRepoProtocol):
    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _to_domain(v: VariantExercise) -> VariantDomain:
        return VariantDomain(
            v.id, v.submission_id, v.title, v.description,
            v.cases, v.scoring_points, v.lang,
            v.difficulty, v.origin_misconception_id, v.practice_assignment_id,
            v.created_at,
        )

    def create(self, submission_id, result, origin_misconception_id, practice_assignment_id):
        v = VariantExercise(
            submission_id=submission_id,
            title=result.title,
            description=result.description,
            cases=result.cases,
            scoring_points=result.scoring_points,
            lang=result.lang,
            difficulty=result.difficulty,
            origin_misconception_id=origin_misconception_id,
            practice_assignment_id=practice_assignment_id,
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

    def latest_for_misconception(self, misconception_id):
        v = (
            self._db.query(VariantExercise)
            .filter(VariantExercise.origin_misconception_id == misconception_id)
            .order_by(VariantExercise.created_at.desc())
            .first()
        )
        return self._to_domain(v) if v else None
