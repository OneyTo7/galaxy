from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.contexts.diagnose.deps import get_diagnose_service
from app.contexts.diagnose.schemas import DiagnoseOut, MisconceptionOut
from app.contexts.diagnose.service import DiagnoseService
from app.core.deps import CurrentUser, get_current_user
from app.core.exceptions import DomainError, ForbiddenError, NotFoundError

router = APIRouter(prefix="/api/submissions", tags=["diagnose"])


@router.post(
    "/{submission_id}/diagnose",
    response_model=DiagnoseOut,
    status_code=status.HTTP_201_CREATED,
)
async def diagnose(
    submission_id: int,
    user: CurrentUser = Depends(get_current_user),
    svc: DiagnoseService = Depends(get_diagnose_service),
) -> DiagnoseOut:
    try:
        domain = await svc.diagnose(submission_id, user)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)
    except ForbiddenError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=e.message)
    except DomainError as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail=e.message)
    return DiagnoseOut(
        submission_id=domain.submission_id,
        misconception_type=domain.misconception_type,
        evidence=domain.evidence,
        knowledge_point=domain.knowledge_point,
        knowledge_point_id=domain.knowledge_point_id,
        confidence=domain.confidence,
        evidence_validated=domain.evidence_validated,
        status=domain.status,
    )


@router.get("/{submission_id}/diagnosis", response_model=list[MisconceptionOut])
async def list_diagnosis(
    submission_id: int,
    user: CurrentUser = Depends(get_current_user),
    svc: DiagnoseService = Depends(get_diagnose_service),
) -> list[MisconceptionOut]:
    return [
        MisconceptionOut(
            id=d.id,
            submission_id=d.submission_id,
            misconception_type=d.misconception_type,
            evidence=d.evidence,
            knowledge_point=d.knowledge_point,
            knowledge_point_id=d.knowledge_point_id,
            confidence=d.confidence,
            evidence_validated=d.evidence_validated,
            status=d.status,
            created_at=d.created_at,
        )
        for d in svc.list_by_submission(submission_id)
    ]
