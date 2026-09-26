from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.contexts.organization.deps import get_organization_service
from app.contexts.organization.schemas import (
    ClassCreate,
    ClassOut,
    CourseCreate,
    CourseOut,
    EnrollmentOut,
)
from app.contexts.organization.service import OrganizationService
from app.core.deps import CurrentUser, get_current_user, require_teacher
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/api", tags=["organization"])


@router.post("/courses", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
async def create_course(
    req: CourseCreate,
    teacher: CurrentUser = Depends(require_teacher),
    svc: OrganizationService = Depends(get_organization_service),
) -> CourseOut:
    d = svc.create_course(teacher.id, req.name, req.code)
    return CourseOut(
        id=d.id, teacher_id=d.teacher_id, name=d.name, code=d.code, created_at=d.created_at
    )


@router.get("/courses", response_model=list[CourseOut])
async def list_courses(
    teacher: CurrentUser = Depends(require_teacher),
    svc: OrganizationService = Depends(get_organization_service),
) -> list[CourseOut]:
    return [
        CourseOut(
            id=c.id, teacher_id=c.teacher_id, name=c.name, code=c.code, created_at=c.created_at
        )
        for c in svc.list_my_courses(teacher.id)
    ]


@router.get("/courses/{course_id}", response_model=CourseOut)
async def get_course(
    course_id: int,
    teacher: CurrentUser = Depends(require_teacher),
    svc: OrganizationService = Depends(get_organization_service),
) -> CourseOut:
    try:
        d = svc.get_course(course_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)
    return CourseOut(
        id=d.id, teacher_id=d.teacher_id, name=d.name, code=d.code, created_at=d.created_at
    )


@router.post(
    "/courses/{course_id}/classes",
    response_model=ClassOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_class(
    course_id: int,
    req: ClassCreate,
    teacher: CurrentUser = Depends(require_teacher),
    svc: OrganizationService = Depends(get_organization_service),
) -> ClassOut:
    try:
        d = svc.create_class(course_id, req.name)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)
    return ClassOut(id=d.id, course_id=d.course_id, name=d.name, created_at=d.created_at)


@router.get("/courses/{course_id}/classes", response_model=list[ClassOut])
async def list_classes(
    course_id: int,
    teacher: CurrentUser = Depends(require_teacher),
    svc: OrganizationService = Depends(get_organization_service),
) -> list[ClassOut]:
    try:
        domains = svc.list_classes(course_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)
    return [
        ClassOut(id=d.id, course_id=d.course_id, name=d.name, created_at=d.created_at)
        for d in domains
    ]


@router.post(
    "/classes/{class_id}/enrollments",
    response_model=EnrollmentOut,
    status_code=status.HTTP_201_CREATED,
)
async def enroll(
    class_id: int,
    user: CurrentUser = Depends(get_current_user),
    svc: OrganizationService = Depends(get_organization_service),
) -> EnrollmentOut:
    d = svc.enroll(class_id, user.id)
    return EnrollmentOut(
        id=d.id, class_id=d.class_id, student_id=d.student_id, created_at=d.created_at
    )


@router.get("/classes/{class_id}/enrollments", response_model=list[EnrollmentOut])
async def list_enrollments(
    class_id: int,
    teacher: CurrentUser = Depends(require_teacher),
    svc: OrganizationService = Depends(get_organization_service),
) -> list[EnrollmentOut]:
    return [
        EnrollmentOut(
            id=e.id, class_id=e.class_id, student_id=e.student_id, created_at=e.created_at
        )
        for e in svc.list_enrollments(class_id)
    ]
