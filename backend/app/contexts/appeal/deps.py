from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.contexts.appeal.repository import SQLAlchemyAppealRepo
from app.contexts.appeal.service import AppealService
from app.contexts.submission.deps import get_submission_service
from app.contexts.submission.service import SubmissionService
from app.core.database import get_db


def get_appeal_service(
    db: Session = Depends(get_db),
    submission_svc: SubmissionService = Depends(get_submission_service),
) -> AppealService:
    return AppealService(submission_svc=submission_svc, appeal_repo=SQLAlchemyAppealRepo(db))
