from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.contexts.assignment.deps import get_assignment_service
from app.contexts.assignment.schemas import (
    AssignmentCreate,
    AssignmentDomain,
    AssignmentOut,
    AssignmentUpdate,
    TestCaseOut,
)
from app.contexts.assignment.service import AssignmentService
from app.core.deps import CurrentUser, require_teacher
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/api/assignments", tags=["assignment"])


def _to_out(d: AssignmentDomain) -> AssignmentOut:
    return AssignmentOut(
        id=d.id,
        teacher_id=d.teacher_id,
        course_id=d.course_id,
        title=d.title,
        description=d.description,
        lang=d.lang,
        scoring_rubric=d.scoring_rubric,
        reference_code=d.reference_code,
        status=d.status,
        created_at=d.created_at,
        test_cases=[
            TestCaseOut(
                id=tc.id,
                assignment_id=tc.assignment_id,
                name=tc.name,
                input=tc.input,
                expected_output=tc.expected_output,
                is_hidden=tc.is_hidden,
                weight=tc.weight,
                order=tc.order,
            )
            for tc in d.test_cases
        ],
    )


@router.post("", response_model=AssignmentOut, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    req: AssignmentCreate,
    teacher: CurrentUser = Depends(require_teacher),
    svc: AssignmentService = Depends(get_assignment_service),
) -> AssignmentOut:
    domain = svc.create(teacher.id, req)
    return _to_out(domain)


@router.get("", response_model=list[AssignmentOut])
async def list_assignments(
    teacher: CurrentUser = Depends(require_teacher),
    svc: AssignmentService = Depends(get_assignment_service),
) -> list[AssignmentOut]:
    return [_to_out(d) for d in svc.list_mine(teacher.id)]


@router.get("/{assignment_id}", response_model=AssignmentOut)
async def get_assignment(
    assignment_id: int,
    teacher: CurrentUser = Depends(require_teacher),
    svc: AssignmentService = Depends(get_assignment_service),
) -> AssignmentOut:
    try:
        return _to_out(svc.get(assignment_id))
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)


@router.put("/{assignment_id}", response_model=AssignmentOut)
async def update_assignment(
    assignment_id: int,
    req: AssignmentUpdate,
    teacher: CurrentUser = Depends(require_teacher),
    svc: AssignmentService = Depends(get_assignment_service),
) -> AssignmentOut:
    try:
        return _to_out(svc.update(assignment_id, req))
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
    assignment_id: int,
    teacher: CurrentUser = Depends(require_teacher),
    svc: AssignmentService = Depends(get_assignment_service),
) -> None:
    try:
        svc.delete(assignment_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)
