from __future__ import annotations

from sqlalchemy.orm import Session

from app.contexts.evaluation.models import Evaluation
from app.contexts.evaluation.schemas import CaseResult


class EvaluationRepoProtocol:
    def create_many(self, submission_id: int, results: list[CaseResult]) -> None: ...
    def list_by_submission(self, submission_id: int) -> list[CaseResult]: ...


class SQLEvaluationRepo(EvaluationRepoProtocol):
    def __init__(self, db: Session) -> None:
        self._db = db

    def create_many(self, submission_id, results):
        for r in results:
            self._db.add(
                Evaluation(
                    submission_id=submission_id,
                    case_id=r.case_id,
                    passed=r.passed,
                    stdout=r.stdout,
                    stderr=r.stderr,
                    timed_out=r.timed_out,
                    elapsed_ms=r.elapsed_ms,
                )
            )
        self._db.commit()

    def list_by_submission(self, submission_id):
        rows = (
            self._db.query(Evaluation)
            .filter(Evaluation.submission_id == submission_id)
            .order_by(Evaluation.id.asc())
            .all()
        )
        return [
            CaseResult(
                case_id=r.case_id, passed=r.passed, stdout=r.stdout,
                stderr=r.stderr, timed_out=r.timed_out, elapsed_ms=r.elapsed_ms,
            )
            for r in rows
        ]
