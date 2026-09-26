from __future__ import annotations

from fastapi import APIRouter, Depends

from app.contexts.grade.deps import get_grade_service
from app.contexts.grade.schemas import GradeDomain, GradeOut
from app.contexts.grade.service import GradeService
from app.core.deps import CurrentUser, require_teacher

router = APIRouter(prefix="/api/assignments", tags=["grade"])


def _to_out(d: GradeDomain) -> GradeOut:
    return GradeOut(
        id=d.id, assignment_id=d.assignment_id, student_id=d.student_id,
        final_score=d.final_score, status=d.status, note=d.note,
        created_at=d.created_at, updated_at=d.updated_at,
    )


@router.post("/{assignment_id}/gradebook", response_model=list[GradeOut])
async def generate_gradebook(
    assignment_id: int,
    teacher: CurrentUser = Depends(require_teacher),
    svc: GradeService = Depends(get_grade_service),
) -> list[GradeOut]:
    return [_to_out(d) for d in svc.generate_gradebook(assignment_id)]


@router.get("/{assignment_id}/gradebook", response_model=list[GradeOut])
async def get_gradebook(
    assignment_id: int,
    teacher: CurrentUser = Depends(require_teacher),
    svc: GradeService = Depends(get_grade_service),
) -> list[GradeOut]:
    return [_to_out(d) for d in svc.list_by_assignment(assignment_id)]
