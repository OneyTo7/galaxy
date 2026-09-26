from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.contexts.assignment.deps import get_assignment_service
from app.contexts.assignment.service import AssignmentService
from app.contexts.grade.repository import SQLAlchemyGradeRepo
from app.contexts.grade.service import GradeService
from app.contexts.submission.deps import get_submission_service
from app.contexts.submission.service import SubmissionService
from app.core.database import get_db


def get_grade_service(
    db: Session = Depends(get_db),
    submission_svc: SubmissionService = Depends(get_submission_service),
    assignment_svc: AssignmentService = Depends(get_assignment_service),
) -> GradeService:
    return GradeService(submission_svc=submission_svc, assignment_svc=assignment_svc, grade_repo=SQLAlchemyGradeRepo(db))
