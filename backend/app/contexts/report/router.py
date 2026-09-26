from __future__ import annotations

from fastapi import APIRouter, Depends

from app.contexts.report.deps import get_report_service
from app.contexts.report.schemas import LearningReport
from app.contexts.report.service import ReportService
from app.core.deps import get_current_user_id

router = APIRouter(prefix="/api/assignments", tags=["report"])


@router.get("/{assignment_id}/learning-report", response_model=LearningReport)
async def get_learning_report(
    assignment_id: int,
    user_id: str = Depends(get_current_user_id),
    svc: ReportService = Depends(get_report_service),
) -> LearningReport:
    return svc.get_assignment_report(assignment_id)
