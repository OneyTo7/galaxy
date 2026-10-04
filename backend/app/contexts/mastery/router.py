from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.contexts.mastery.deps import get_mastery_service
from app.contexts.mastery.schemas import (
    KnowledgePointOut,
    KnowledgeTagOut,
    KnowledgeTagUpdate,
    MasteryCellOut,
    MasteryEventOut,
    MasteryMatrixOut,
    MatrixStudentOut,
    StudentMasteryOut,
)
from app.contexts.mastery.service import MasteryService
from app.core.deps import CurrentUser, get_current_user, require_teacher
from app.core.exceptions import DomainError, ForbiddenError, NotFoundError

router = APIRouter(tags=["mastery"])


def _cell(points: dict) -> MasteryCellOut:
    return MasteryCellOut(**points)


def _event_out(e, kp_map: dict) -> MasteryEventOut:
    kp = kp_map.get(e.knowledge_point_id)
    return MasteryEventOut(
        id=e.id,
        knowledge_point_id=e.knowledge_point_id,
        code=kp.code if kp else "",
        name=kp.name if kp else "",
        source=e.source,
        observed=e.observed,
        mastery_before=e.mastery_before,
        mastery_after=e.mastery_after,
        submission_id=e.submission_id,
        created_at=e.created_at,
    )


@router.get("/api/knowledge-points", response_model=list[KnowledgePointOut])
async def list_knowledge_points(
    teacher: CurrentUser = Depends(require_teacher),
    svc: MasteryService = Depends(get_mastery_service),
) -> list[KnowledgePointOut]:
    return [
        KnowledgePointOut(
            id=k.id, code=k.code, name=k.name, category=k.category, sort_order=k.sort_order
        )
        for k in svc.list_taxonomy()
    ]


@router.get(
    "/api/assignments/{assignment_id}/knowledge-points",
    response_model=list[KnowledgeTagOut],
)
async def get_assignment_tags(
    assignment_id: int,
    teacher: CurrentUser = Depends(require_teacher),
    svc: MasteryService = Depends(get_mastery_service),
) -> list[KnowledgeTagOut]:
    try:
        tags = svc.get_tags(assignment_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)
    taxonomy = {k.id: k for k in svc.list_taxonomy()}
    return [
        KnowledgeTagOut(
            knowledge_point_id=t.knowledge_point_id,
            code=taxonomy[t.knowledge_point_id].code,
            name=taxonomy[t.knowledge_point_id].name,
            category=taxonomy[t.knowledge_point_id].category,
            weight=t.weight,
        )
        for t in tags
        if t.knowledge_point_id in taxonomy
    ]


@router.put(
    "/api/assignments/{assignment_id}/knowledge-points",
    response_model=list[KnowledgeTagOut],
)
async def update_assignment_tags(
    assignment_id: int,
    req: KnowledgeTagUpdate,
    teacher: CurrentUser = Depends(require_teacher),
    svc: MasteryService = Depends(get_mastery_service),
) -> list[KnowledgeTagOut]:
    try:
        svc.tag_assignment(teacher.id, assignment_id, req.items)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)
    except ForbiddenError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=e.message)
    except DomainError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=e.message)
    return await get_assignment_tags(assignment_id, teacher, svc)


@router.get("/api/courses/{course_id}/mastery-matrix", response_model=MasteryMatrixOut)
async def mastery_matrix(
    course_id: int,
    teacher: CurrentUser = Depends(require_teacher),
    svc: MasteryService = Depends(get_mastery_service),
) -> MasteryMatrixOut:
    try:
        data = svc.matrix(course_id, teacher)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)
    except ForbiddenError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=e.message)
    return MasteryMatrixOut(
        course_id=data["course_id"],
        students=[MatrixStudentOut(**s) for s in data["students"]],
        cells=[_cell(c) for c in data["cells"]],
    )


@router.get("/api/students/{student_id}/mastery", response_model=StudentMasteryOut)
async def student_mastery(
    student_id: int,
    course_id: int = Query(...),
    teacher: CurrentUser = Depends(require_teacher),
    svc: MasteryService = Depends(get_mastery_service),
) -> StudentMasteryOut:
    try:
        data = svc.student_mastery(course_id, student_id, teacher)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)
    except ForbiddenError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=e.message)
    return StudentMasteryOut(
        course_id=data["course_id"],
        user_id=data["user_id"],
        points=[_cell(p) for p in data["points"]],
    )


@router.get(
    "/api/students/{student_id}/mastery/events", response_model=list[MasteryEventOut]
)
async def student_mastery_events(
    student_id: int,
    course_id: int = Query(...),
    teacher: CurrentUser = Depends(require_teacher),
    svc: MasteryService = Depends(get_mastery_service),
) -> list[MasteryEventOut]:
    try:
        events = svc.events(course_id, student_id, teacher)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)
    except ForbiddenError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=e.message)
    kp_map = {k.id: k for k in svc.list_taxonomy()}
    return [_event_out(e, kp_map) for e in events]


@router.get("/api/mastery/me", response_model=StudentMasteryOut)
async def my_mastery(
    course_id: int = Query(...),
    user: CurrentUser = Depends(get_current_user),
    svc: MasteryService = Depends(get_mastery_service),
) -> StudentMasteryOut:
    try:
        data = svc.my_mastery(course_id, user.id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)
    return StudentMasteryOut(
        course_id=data["course_id"],
        user_id=data["user_id"],
        points=[_cell(p) for p in data["points"]],
    )
