from __future__ import annotations

from app.contexts.lesson.repository import LessonRepoProtocol
from app.contexts.organization.service import OrganizationService
from app.core.exceptions import ForbiddenError, NotFoundError


class LessonService:
    def __init__(self, repo: LessonRepoProtocol, org_svc: OrganizationService) -> None:
        self._repo = repo
        self._org_svc = org_svc

    def list_by_course(self, course_id: int) -> list:
        self._org_svc.get_course(course_id)  # 确认课程存在
        return self._repo.list_by_course(course_id)

    def get(self, lesson_id: int):
        l = self._repo.get(lesson_id)
        if not l:
            raise NotFoundError("章节不存在")
        return l

    def create(self, teacher_id: int, course_id: int, title: str, content: str, sort_order: int, assignment_id: int | None) -> object:
        course = self._org_svc.get_course(course_id)
        if course.teacher_id != teacher_id:
            raise ForbiddenError()
        return self._repo.create(course_id, title, content, sort_order, assignment_id)

    def update(self, teacher_id: int, lesson_id: int, data: dict) -> object:
        l = self._repo.get(lesson_id)
        if not l:
            raise NotFoundError("章节不存在")
        course = self._org_svc.get_course(l.course_id)
        if course.teacher_id != teacher_id:
            raise ForbiddenError()
        return self._repo.update(lesson_id, data)

    def delete(self, teacher_id: int, lesson_id: int) -> None:
        l = self._repo.get(lesson_id)
        if not l:
            raise NotFoundError("章节不存在")
        course = self._org_svc.get_course(l.course_id)
        if course.teacher_id != teacher_id:
            raise ForbiddenError()
        self._repo.delete(lesson_id)
