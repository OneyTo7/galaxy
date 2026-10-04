from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("galaxy.worker")

from app.contexts.assignment.providers.moma import AssignmentGenerator
from app.contexts.assignment.repository import SQLAlchemyAssignmentRepo
from app.contexts.assignment.service import AssignmentService
from app.contexts.evaluation.repository import SQLEvaluationRepo
from app.contexts.evaluation.service import EvaluationService
from app.contexts.mastery.repository import SQLAlchemyMasteryRepo
from app.contexts.mastery.service import MasteryService, OvercomeMarkerProtocol
from app.contexts.organization.repository import SQLOrganizationRepo
from app.contexts.organization.service import OrganizationService
from app.contexts.submission.repository import SQLAlchemySubmissionRepo
from app.contexts.submission.service import SubmissionService
from app.contexts.diagnose.repository import SQLAlchemyMisconceptionRepo
from app.core.database import SessionLocal
from app.core.exceptions import NotFoundError
from app.core.queue import consume_submission


class _OvercomeMarker(OvercomeMarkerProtocol):
    def __init__(self, db) -> None:
        self._repo = SQLAlchemyMisconceptionRepo(db)

    def mark_overcome(self, user_id, knowledge_point_id):
        return self._repo.mark_open_overcome(user_id, knowledge_point_id)


def run_worker() -> None:
    logger.info("evaluation worker started, waiting for submissions...")
    while True:
        submission_id = consume_submission(timeout=5)
        if submission_id is None:
            continue
        db = SessionLocal()
        try:
            eval_svc = EvaluationService(SQLEvaluationRepo(db))
            org_svc = OrganizationService(SQLOrganizationRepo(db))
            assign_svc = AssignmentService(SQLAlchemyAssignmentRepo(db), AssignmentGenerator(), org_svc)
            sub_repo = SQLAlchemySubmissionRepo(db)
            submission_svc = SubmissionService(sub_repo, assign_svc, eval_svc, org_svc)
            mastery_svc = MasteryService(
                repo=SQLAlchemyMasteryRepo(db),
                evaluation_svc=eval_svc,
                submission_svc=submission_svc,
                assignment_svc=assign_svc,
                org_svc=org_svc,
                overcome_marker=_OvercomeMarker(db),
            )
            try:
                sub = submission_svc.get(submission_id)
                assignment = assign_svc.get(sub.assignment_id)
                results = eval_svc.run(sub.code, sub.lang, assignment.test_cases, sub.id)
                score = eval_svc.score(results, assignment.test_cases)
                submission_svc.update_score(sub.id, score)
                logger.info("evaluated submission %s score %s", sub.id, score)
                # D2: 评分后记录掌握度观测（失败不回滚评分）
                try:
                    mastery_svc.record_submission(sub.id)
                except Exception:
                    logger.exception("mastery record failed for submission %s", sub.id)
            except NotFoundError:
                continue
        finally:
            db.close()


if __name__ == "__main__":
    run_worker()
