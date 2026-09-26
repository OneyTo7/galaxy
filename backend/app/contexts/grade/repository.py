from __future__ import annotations

from sqlalchemy.orm import Session

from app.contexts.grade.models import Grade
from app.contexts.grade.schemas import GradeDomain


class GradeRepoProtocol:
    def upsert(self, assignment_id: int, student_id: int, final_score: int) -> GradeDomain: ...
    def list_by_assignment(self, assignment_id: int) -> list[GradeDomain]: ...


class SQLAlchemyGradeRepo(GradeRepoProtocol):
    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _to_domain(g: Grade) -> GradeDomain:
        return GradeDomain(
            g.id, g.assignment_id, g.student_id, g.final_score,
            g.status, g.note, g.created_at, g.updated_at,
        )

    def upsert(self, assignment_id, student_id, final_score):
        existing = (
            self._db.query(Grade)
            .filter(Grade.assignment_id == assignment_id, Grade.student_id == student_id)
            .first()
        )
        if existing:
            existing.final_score = final_score
            existing.status = "graded"
            self._db.commit()
            self._db.refresh(existing)
            return self._to_domain(existing)
        g = Grade(
            assignment_id=assignment_id,
            student_id=student_id,
            final_score=final_score,
            status="graded",
        )
        self._db.add(g)
        self._db.commit()
        self._db.refresh(g)
        return self._to_domain(g)

    def list_by_assignment(self, assignment_id):
        rows = (
            self._db.query(Grade)
            .filter(Grade.assignment_id == assignment_id)
            .order_by(Grade.final_score.desc())
            .all()
        )
        return [self._to_domain(g) for g in rows]
