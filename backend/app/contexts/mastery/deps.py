from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.contexts.assignment.deps import get_assignment_service
from app.contexts.assignment.service import AssignmentService
from app.contexts.diagnose.repository import SQLAlchemyMisconceptionRepo
from app.contexts.evaluation.deps import get_evaluation_service
from app.contexts.evaluation.service import EvaluationService
from app.contexts.mastery.repository import SQLAlchemyMasteryRepo
from app.contexts.mastery.service import MasteryService, OvercomeMarkerProtocol
from app.contexts.organization.deps import get_organization_service
from app.contexts.organization.service import OrganizationService
from app.contexts.submission.deps import get_submission_service
from app.contexts.submission.service import SubmissionService
from app.core.database import get_db


class MisconceptionOvercomeMarker(OvercomeMarkerProtocol):
    """组合根适配器：掌握度事件驱动 diagnose 上下文的误区克服标记。"""

    def __init__(self, db: Session) -> None:
        self._repo = SQLAlchemyMisconceptionRepo(db)

    def mark_overcome(self, user_id: int, knowledge_point_id: int) -> int:
        return self._repo.mark_open_overcome(user_id, knowledge_point_id)


def get_mastery_service(
    db: Session = Depends(get_db),
    evaluation_svc: EvaluationService = Depends(get_evaluation_service),
    submission_svc: SubmissionService = Depends(get_submission_service),
    assignment_svc: AssignmentService = Depends(get_assignment_service),
    org_svc: OrganizationService = Depends(get_organization_service),
) -> MasteryService:
    return MasteryService(
        repo=SQLAlchemyMasteryRepo(db),
        evaluation_svc=evaluation_svc,
        submission_svc=submission_svc,
        assignment_svc=assignment_svc,
        org_svc=org_svc,
        overcome_marker=MisconceptionOvercomeMarker(db),
    )
