from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.contexts.diagnose.providers.moma import MoMAProvider
from app.contexts.diagnose.repository import SQLAlchemyMisconceptionRepo
from app.contexts.diagnose.service import DiagnoseService
from app.contexts.evaluation.deps import get_evaluation_service
from app.contexts.evaluation.service import EvaluationService
from app.contexts.submission.deps import get_submission_service
from app.contexts.submission.service import SubmissionService
from app.core.database import get_db


def get_diagnose_service(
    db: Session = Depends(get_db),
    submission_svc: SubmissionService = Depends(get_submission_service),
    evaluation_svc: EvaluationService = Depends(get_evaluation_service),
) -> DiagnoseService:
    return DiagnoseService(
        submission_svc=submission_svc,
        evaluation_svc=evaluation_svc,
        misconception_repo=SQLAlchemyMisconceptionRepo(db),
        moma_provider=MoMAProvider(),
    )
