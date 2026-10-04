from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.contexts.lesson.deps import get_lesson_service
from app.contexts.lesson.schemas import LessonCreate, LessonListItem, LessonOut
from app.contexts.lesson.service import LessonService
from app.core.deps import CurrentUser, get_current_user, require_teacher
from app.core.exceptions import ForbiddenError, NotFoundError

router = APIRouter(prefix="/api", tags=["lesson"])


def _to_out(d) -> LessonOut:
    return LessonOut(
        id=d.id, course_id=d.course_id, title=d.title,
        sort_order=d.sort_order, content=d.content,
        assignment_id=d.assignment_id, created_at=d.created_at,
    )


def _to_list_item(d) -> LessonListItem:
    return LessonListItem(
        id=d.id, course_id=d.course_id, title=d.title,
        sort_order=d.sort_order, assignment_id=d.assignment_id,
    )


@router.get("/courses/{course_id}/lessons", response_model=list[LessonListItem])
async def list_lessons(
    course_id: int,
    user: CurrentUser = Depends(get_current_user),
    svc: LessonService = Depends(get_lesson_service),
) -> list[LessonListItem]:
    return [_to_list_item(d) for d in svc.list_by_course(course_id)]


@router.get("/lessons/{lesson_id}", response_model=LessonOut)
async def get_lesson(
    lesson_id: int,
    user: CurrentUser = Depends(get_current_user),
    svc: LessonService = Depends(get_lesson_service),
) -> LessonOut:
    try:
        return _to_out(svc.get(lesson_id))
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post("/courses/{course_id}/lessons", response_model=LessonOut, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    course_id: int,
    req: LessonCreate,
    teacher: CurrentUser = Depends(require_teacher),
    svc: LessonService = Depends(get_lesson_service),
) -> LessonOut:
    try:
        d = svc.create(
            teacher_id=teacher.id, course_id=course_id,
            title=req.title, content=req.content,
            sort_order=req.sort_order, assignment_id=req.assignment_id,
        )
        return _to_out(d)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)
    except ForbiddenError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=e.message)


@router.put("/lessons/{lesson_id}", response_model=LessonOut)
async def update_lesson(
    lesson_id: int,
    req: dict,
    teacher: CurrentUser = Depends(require_teacher),
    svc: LessonService = Depends(get_lesson_service),
) -> LessonOut:
    try:
        return _to_out(svc.update(teacher.id, lesson_id, req))
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)
    except ForbiddenError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=e.message)


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    lesson_id: int,
    teacher: CurrentUser = Depends(require_teacher),
    svc: LessonService = Depends(get_lesson_service),
) -> None:
    try:
        svc.delete(teacher.id, lesson_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)
    except ForbiddenError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=e.message)
