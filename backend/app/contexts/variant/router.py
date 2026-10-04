from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.contexts.variant.deps import get_variant_service
from app.contexts.variant.schemas import VariantOut
from app.contexts.variant.service import VariantService
from app.core.deps import CurrentUser, get_current_user
from app.core.exceptions import DomainError, ForbiddenError

router = APIRouter(prefix="/api/submissions", tags=["variant"])


def _to_out(domain) -> VariantOut:
    return VariantOut(
        id=domain.id,
        submission_id=domain.submission_id,
        title=domain.title,
        description=domain.description,
        cases=domain.cases or [],
        scoring_points=domain.scoring_points or [],
        lang=domain.lang,
        difficulty=domain.difficulty,
        practice_assignment_id=domain.practice_assignment_id,
    )


@router.post(
    "/{submission_id}/variant",
    response_model=VariantOut,
    status_code=status.HTTP_201_CREATED,
)
async def generate_variant(
    submission_id: int,
    user: CurrentUser = Depends(get_current_user),
    svc: VariantService = Depends(get_variant_service),
) -> VariantOut:
    try:
        domain = await svc.generate(submission_id, user)
    except DomainError as e:
        code = 403 if e.code == "forbidden" else (409 if e.code == "no_diagnosis" else 503)
        raise HTTPException(code, detail=e.message)
    return _to_out(domain)


@router.get("/{submission_id}/variants", response_model=list[VariantOut])
async def list_variants(
    submission_id: int,
    user: CurrentUser = Depends(get_current_user),
    svc: VariantService = Depends(get_variant_service),
) -> list[VariantOut]:
    return [_to_out(d) for d in svc.list_by_submission(submission_id)]
