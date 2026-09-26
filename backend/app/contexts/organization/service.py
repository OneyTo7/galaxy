from __future__ import annotations

from app.contexts.organization.repository import OrganizationRepoProtocol
from app.contexts.organization.schemas import (
    ClassDomain,
    CourseDomain,
    EnrollmentDomain,
)
from app.core.exceptions import NotFoundError


class OrganizationService:
    def __init__(self, repo: OrganizationRepoProtocol) -> None:
        self._repo = repo

    def create_course(self, teacher_id: int, name: str, code: str) -> CourseDomain:
        return self._repo.create_course(teacher_id, name, code)

    def list_my_courses(self, teacher_id: int) -> list[CourseDomain]:
        return self._repo.list_courses_by_teacher(teacher_id)

    def get_course(self, course_id: int) -> CourseDomain:
        c = self._repo.get_course(course_id)
        if not c:
            raise NotFoundError("课程不存在")
        return c

    def create_class(self, course_id: int, name: str) -> ClassDomain:
        self.get_course(course_id)
        return self._repo.create_class(course_id, name)

    def list_classes(self, course_id: int) -> list[ClassDomain]:
        self.get_course(course_id)
        return self._repo.list_classes_by_course(course_id)

    def get_class(self, class_id: int) -> ClassDomain:
        cl = self._repo.get_class(class_id)
        if not cl:
            raise NotFoundError("班级不存在")
        return cl

    def enroll(self, class_id: int, student_id: int) -> EnrollmentDomain:
        return self._repo.create_enrollment(class_id, student_id)

    def list_enrollments(self, class_id: int) -> list[EnrollmentDomain]:
        return self._repo.list_enrollments_by_class(class_id)
