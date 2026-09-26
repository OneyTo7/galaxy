from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.contexts.variant.deps import get_variant_service
from app.contexts.variant.schemas import VariantOut
from app.contexts.variant.service import VariantService
from app.core.deps import get_current_user_id
from app.core.exceptions import DomainError

router = APIRouter(prefix="/api/submissions", tags=["variant"])


@router.post(
    "/{submission_id}/variant",
    response_model=VariantOut,
    status_code=status.HTTP_201_CREATED,
)
async def generate_variant(
    submission_id: int,
    user_id: str = Depends(get_current_user_id),
    svc: VariantService = Depends(get_variant_service),
) -> VariantOut:
    try:
        domain = await svc.generate(submission_id)
    except DomainError as e:
        code = 409 if e.code == "no_diagnosis" else 503
        raise HTTPException(code, detail=e.message)
    return VariantOut(
        id=domain.id,
        submission_id=domain.submission_id,
        title=domain.title,
        description=domain.description,
        cases=domain.cases or [],
        scoring_points=domain.scoring_points or [],
        lang=domain.lang,
    )


@router.get("/{submission_id}/variants", response_model=list[VariantOut])
async def list_variants(
    submission_id: int,
    user_id: str = Depends(get_current_user_id),
    svc: VariantService = Depends(get_variant_service),
) -> list[VariantOut]:
    return [
        VariantOut(
            id=d.id,
            submission_id=d.submission_id,
            title=d.title,
            description=d.description,
            cases=d.cases or [],
            scoring_points=d.scoring_points or [],
            lang=d.lang,
        )
        for d in svc.list_by_submission(submission_id)
    ]
