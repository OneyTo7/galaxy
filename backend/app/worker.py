from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.contexts.assignment.repository import SQLAlchemyAssignmentRepo
from app.contexts.assignment.service import AssignmentService
from app.contexts.evaluation.repository import SQLEvaluationRepo
from app.contexts.evaluation.service import EvaluationService
from app.contexts.submission.repository import SQLAlchemySubmissionRepo
from app.core.database import SessionLocal
from app.core.queue import consume_submission


def run_worker() -> None:
    db = SessionLocal()
    eval_svc = EvaluationService(SQLEvaluationRepo(db))
    assign_svc = AssignmentService(SQLAlchemyAssignmentRepo(db))
    sub_repo = SQLAlchemySubmissionRepo(db)
    print("evaluation worker started, waiting for submissions...")
    while True:
        submission_id = consume_submission(timeout=5)
        if submission_id is None:
            continue
        sub = sub_repo.get(submission_id)
        if not sub:
            continue
        assignment = assign_svc.get(sub.assignment_id)
        results = eval_svc.run(sub.code, sub.lang, assignment.test_cases, sub.id)
        total = sum(tc.weight for tc in assignment.test_cases) or 1
        passed = sum(
            tc.weight for tc, r in zip(assignment.test_cases, results) if r.passed
        )
        score = round(passed / total * 100)
        sub_repo.update_status_score(sub.id, "done", score)
        print(f"evaluated submission {sub.id} score {score}")


if __name__ == "__main__":
    run_worker()
