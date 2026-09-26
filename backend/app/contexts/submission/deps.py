from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.contexts.assignment.repository import SQLAlchemyAssignmentRepo
from app.contexts.assignment.service import AssignmentService
from app.contexts.evaluation.deps import get_evaluation_service
from app.contexts.submission.repository import SQLAlchemySubmissionRepo
from app.contexts.submission.service import SubmissionService
from app.core.database import get_db


def get_submission_service(db: Session = Depends(get_db)) -> SubmissionService:
    return SubmissionService(
        sub_repo=SQLAlchemySubmissionRepo(db),
        assignment_svc=AssignmentService(SQLAlchemyAssignmentRepo(db)),
        evaluation_svc=get_evaluation_service(),
    )
