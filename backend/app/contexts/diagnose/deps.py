from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.contexts.diagnose.providers.moma import MoMAProvider
from app.contexts.diagnose.repository import SQLAlchemyMisconceptionRepo
from app.contexts.diagnose.service import DiagnoseService, MasteryHookProtocol
from app.contexts.evaluation.deps import get_evaluation_service
from app.contexts.evaluation.service import EvaluationService
from app.contexts.mastery.deps import get_mastery_service
from app.contexts.mastery.service import MasteryService
from app.contexts.submission.deps import get_submission_service
from app.contexts.submission.service import SubmissionService
from app.core.database import get_db


class MasteryHook(MasteryHookProtocol):
    """组合根适配器：诊断入库后调用 mastery 记录负观测。"""

    def __init__(self, svc: MasteryService) -> None:
        self._svc = svc

    def record_diagnosis(
        self, submission_id: int, user_id: int, knowledge_point_id: int | None, confidence: float
    ) -> None:
        self._svc.record_diagnosis(submission_id, user_id, knowledge_point_id, confidence)


def get_diagnose_service(
    db: Session = Depends(get_db),
    submission_svc: SubmissionService = Depends(get_submission_service),
    evaluation_svc: EvaluationService = Depends(get_evaluation_service),
    mastery_svc: MasteryService = Depends(get_mastery_service),
) -> DiagnoseService:
    return DiagnoseService(
        submission_svc=submission_svc,
        evaluation_svc=evaluation_svc,
        misconception_repo=SQLAlchemyMisconceptionRepo(db),
        moma_provider=MoMAProvider(taxonomy_provider=mastery_svc.list_codes),
        mastery_hook=MasteryHook(mastery_svc),
        taxonomy_provider=mastery_svc.list_taxonomy,
    )
