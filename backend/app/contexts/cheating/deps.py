from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.contexts.cheating.providers.moma import CheatingProvider
from app.contexts.cheating.repository import SQLAlchemyCheatingRepo
from app.contexts.cheating.service import CheatingService
from app.contexts.submission.deps import get_submission_service
from app.contexts.submission.service import SubmissionService
from app.core.database import get_db


def get_cheating_service(
    db: Session = Depends(get_db),
    submission_svc: SubmissionService = Depends(get_submission_service),
) -> CheatingService:
    return CheatingService(
        submission_svc=submission_svc,
        cheating_repo=SQLAlchemyCheatingRepo(db),
        cheating_provider=CheatingProvider(),
    )
