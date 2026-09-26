from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.contexts.appeal.deps import get_appeal_service
from app.contexts.appeal.schemas import AppealCreate, AppealDomain, AppealOut, AppealReview
from app.contexts.appeal.service import AppealService
from app.core.deps import CurrentUser, get_current_user, require_teacher
from app.core.exceptions import ConflictError, NotFoundError

router = APIRouter(prefix="/api", tags=["appeal"])


def _to_out(d: AppealDomain) -> AppealOut:
    return AppealOut(
        id=d.id, submission_id=d.submission_id, student_id=d.student_id,
        reason=d.reason, status=d.status, approved=d.approved,
        review_comment=d.review_comment, reviewer_id=d.reviewer_id,
        new_score=d.new_score, created_at=d.created_at, reviewed_at=d.reviewed_at,
    )


@router.post(
    "/submissions/{submission_id}/appeals",
    response_model=AppealOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_appeal(
    submission_id: int,
    req: AppealCreate,
    user: CurrentUser = Depends(get_current_user),
    svc: AppealService = Depends(get_appeal_service),
) -> AppealOut:
    try:
        domain = svc.create(submission_id, user.id, req.reason)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)
    return _to_out(domain)


@router.get("/appeals", response_model=list[AppealOut])
async def list_pending_appeals(
    teacher: CurrentUser = Depends(require_teacher),
    svc: AppealService = Depends(get_appeal_service),
) -> list[AppealOut]:
    return [_to_out(d) for d in svc.list_pending()]


@router.get("/appeals/mine", response_model=list[AppealOut])
async def my_appeals(
    user: CurrentUser = Depends(get_current_user),
    svc: AppealService = Depends(get_appeal_service),
) -> list[AppealOut]:
    return [_to_out(d) for d in svc.list_by_student(user.id)]


@router.post("/appeals/{appeal_id}/review", response_model=AppealOut)
async def review_appeal(
    appeal_id: int,
    req: AppealReview,
    teacher: CurrentUser = Depends(require_teacher),
    svc: AppealService = Depends(get_appeal_service),
) -> AppealOut:
    try:
        domain = svc.review(appeal_id, teacher.id, req.approved, req.comment, req.new_score)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)
    except ConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=e.message)
    return _to_out(domain)
