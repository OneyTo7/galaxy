from __future__ import annotations

from fastapi import APIRouter, Depends

from app.contexts.report.deps import get_report_service
from app.contexts.report.schemas import LearningReport
from app.contexts.report.service import ReportService
from app.core.deps import CurrentUser, require_teacher

router = APIRouter(prefix="/api/assignments", tags=["report"])


@router.get("/{assignment_id}/learning-report", response_model=LearningReport)
async def get_learning_report(
    assignment_id: int,
    user: CurrentUser = Depends(require_teacher),
    svc: ReportService = Depends(get_report_service),
) -> LearningReport:
    return svc.get_assignment_report(assignment_id)
