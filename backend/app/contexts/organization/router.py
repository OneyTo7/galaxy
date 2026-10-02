from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.contexts.assignment.deps import get_assignment_service
from app.contexts.assignment.service import AssignmentService
from app.contexts.organization.deps import get_organization_service
from app.contexts.organization.schemas import ClassCreate, ClassOut, CourseCreate, CourseDomain, CourseOut, EnrollmentOut
from app.contexts.organization.service import OrganizationService
from app.core.deps import CurrentUser, get_current_user, require_teacher
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/api", tags=["organization"])


def _course_out(d: CourseDomain) -> CourseOut:
    return CourseOut(id=d.id, teacher_id=d.teacher_id, name=d.name, code=d.code, created_at=d.created_at)


def _assign_out(d) -> dict:
    return {
        "id": d.id, "teacher_id": d.teacher_id, "course_id": d.course_id,
        "title": d.title, "description": d.description[:120] + "..." if len(d.description) > 120 else d.description,
        "lang": d.lang, "status": d.status, "created_at": d.created_at.isoformat(),
        "test_cases": [],
    }


@router.get("/courses/mine", tags=["organization"])
async def my_courses(
    user: CurrentUser = Depends(get_current_user),
    svc: OrganizationService = Depends(get_organization_service),
):
    if user.role == "teacher":
        return [_course_out(c) for c in svc.list_my_courses(user.id)]
    return [_course_out(c) for c in svc.list_student_courses(user.id)]


@router.get("/courses/{course_id}/assignments", tags=["organization"])
async def course_assignments(
    course_id: int,
    user: CurrentUser = Depends(get_current_user),
    org_svc: OrganizationService = Depends(get_organization_service),
    assign_svc: AssignmentService = Depends(get_assignment_service),
):
    domains = assign_svc.list_by_course(course_id)
    if user.role == "student":
        domains = [d for d in domains if d.status == "published"]
    return [_assign_out(d) for d in domains]


@router.get("/courses/{course_id}/students", tags=["organization"])
async def course_students(
    course_id: int,
    teacher: CurrentUser = Depends(require_teacher),
    svc: OrganizationService = Depends(get_organization_service),
):
    return svc.list_course_students(course_id)


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
