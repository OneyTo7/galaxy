from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.contexts.assignment.repository import SQLAlchemyAssignmentRepo
from app.contexts.assignment.service import AssignmentService
from app.contexts.evaluation.repository import SQLEvaluationRepo
from app.contexts.evaluation.service import EvaluationService
from app.contexts.submission.repository import SQLAlchemySubmissionRepo
from app.contexts.submission.service import SubmissionService
from app.core.database import SessionLocal
from app.core.exceptions import NotFoundError
from app.core.queue import consume_submission


def run_worker() -> None:
    print("evaluation worker started, waiting for submissions...")
    while True:
        submission_id = consume_submission(timeout=5)
        if submission_id is None:
            continue
        db = SessionLocal()
        try:
            eval_svc = EvaluationService(SQLEvaluationRepo(db))
            assign_svc = AssignmentService(SQLAlchemyAssignmentRepo(db))
            sub_repo = SQLAlchemySubmissionRepo(db)
            submission_svc = SubmissionService(sub_repo, assign_svc, eval_svc)
            try:
                sub = submission_svc.get(submission_id)
                assignment = assign_svc.get(sub.assignment_id)
                results = eval_svc.run(sub.code, sub.lang, assignment.test_cases, sub.id)
                score = eval_svc.score(results, assignment.test_cases)
                submission_svc.update_score(sub.id, score)
                print(f"evaluated submission {sub.id} score {score}")
            except NotFoundError:
                continue
        finally:
            db.close()


if __name__ == "__main__":
    run_worker()
