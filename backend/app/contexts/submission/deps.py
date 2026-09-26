from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.contexts.assignment.providers.moma import AssignmentGenerator
from app.contexts.assignment.repository import SQLAlchemyAssignmentRepo
from app.contexts.assignment.service import AssignmentService
from app.contexts.evaluation.deps import get_evaluation_service
from app.contexts.evaluation.service import EvaluationService
from app.contexts.organization.deps import get_organization_service
from app.contexts.organization.service import OrganizationService
from app.contexts.submission.repository import SQLAlchemySubmissionRepo
from app.contexts.submission.service import SubmissionService
from app.core.database import get_db


def get_submission_service(
    db: Session = Depends(get_db),
    evaluation_svc: EvaluationService = Depends(get_evaluation_service),
    org_svc: OrganizationService = Depends(get_organization_service),
) -> SubmissionService:
    return SubmissionService(
        sub_repo=SQLAlchemySubmissionRepo(db),
        assignment_svc=AssignmentService(SQLAlchemyAssignmentRepo(db), AssignmentGenerator(), org_svc),
        evaluation_svc=evaluation_svc,
        org_svc=org_svc,
    )
