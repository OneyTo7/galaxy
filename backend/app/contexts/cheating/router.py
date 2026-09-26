from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.contexts.cheating.deps import get_cheating_service
from app.contexts.cheating.schemas import CheatingDomain, CheatingReportOut
from app.contexts.cheating.service import CheatingService
from app.core.deps import CurrentUser, require_teacher
from app.core.exceptions import DomainError, NotFoundError

router = APIRouter(prefix="/api/submissions", tags=["cheating"])


def _to_out(d: CheatingDomain) -> CheatingReportOut:
    return CheatingReportOut(
        id=d.id, submission_id=d.submission_id, student_id=d.student_id,
        check_type=d.check_type, score=d.score, detail=d.detail,
        status=d.status, created_at=d.created_at,
    )


@router.post(
    "/{submission_id}/cheating-check",
    response_model=CheatingReportOut,
    status_code=status.HTTP_201_CREATED,
)
async def check_cheating(
    submission_id: int,
    teacher: CurrentUser = Depends(require_teacher),
    svc: CheatingService = Depends(get_cheating_service),
) -> CheatingReportOut:
    try:
        domain = await svc.check_submission(submission_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)
    except DomainError as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail=e.message)
    return _to_out(domain)


@router.get("/{submission_id}/cheating-reports", response_model=list[CheatingReportOut])
async def list_cheating(
    submission_id: int,
    teacher: CurrentUser = Depends(require_teacher),
    svc: CheatingService = Depends(get_cheating_service),
) -> list[CheatingReportOut]:
    return [_to_out(d) for d in svc.list_by_submission(submission_id)]
