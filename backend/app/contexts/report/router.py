from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.contexts.report.deps import get_report_service
from app.contexts.report.schemas import ClassReport, CourseReport, LearningReport
from app.contexts.report.service import ReportService
from app.core.deps import CurrentUser, require_teacher
from app.core.exceptions import ForbiddenError

router = APIRouter(tags=["report"])


@router.get("/api/assignments/{assignment_id}/learning-report", response_model=LearningReport)
async def get_learning_report(
    assignment_id: int,
    user: CurrentUser = Depends(require_teacher),
    svc: ReportService = Depends(get_report_service),
) -> LearningReport:
    try:
        return svc.get_assignment_report(assignment_id, user)
    except ForbiddenError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=e.message)


@router.get("/api/courses/{course_id}/learning-report", response_model=CourseReport)
async def get_course_report(
    course_id: int,
    user: CurrentUser = Depends(require_teacher),
    svc: ReportService = Depends(get_report_service),
) -> CourseReport:
    try:
        return svc.get_course_report(course_id, user)
    except ForbiddenError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=e.message)


@router.get("/api/classes/{class_id}/learning-report", response_model=ClassReport)
async def get_class_report(
    class_id: int,
    user: CurrentUser = Depends(require_teacher),
    svc: ReportService = Depends(get_report_service),
) -> ClassReport:
    try:
        return svc.get_class_report(class_id, user)
    except ForbiddenError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=e.message)
