from __future__ import annotations

from app.contexts.assignment.providers.moma import AssignmentGenerator
from app.contexts.assignment.repository import AssignmentRepoProtocol
from app.contexts.assignment.schemas import AssignmentDomain
from app.contexts.organization.service import OrganizationService
from app.core.exceptions import ForbiddenError, NotFoundError


class AssignmentService:
    def __init__(self, repo: AssignmentRepoProtocol, generator: AssignmentGenerator, org_svc: OrganizationService) -> None:
        self._repo = repo
        self._generator = generator
        self._org_svc = org_svc

    def create(self, teacher_id: int, payload) -> AssignmentDomain:
        if payload.course_id:
            course = self._org_svc.get_course(payload.course_id)
            if course.teacher_id != teacher_id:
                raise ForbiddenError("无权操作该课程下的作业")
        data = {
            "course_id": payload.course_id,
            "title": payload.title,
            "description": payload.description,
            "lang": payload.lang,
            "scoring_rubric": payload.scoring_rubric,
            "reference_code": payload.reference_code,
            "status": "draft",
        }
        test_cases = [tc.model_dump() for tc in payload.test_cases]
        return self._repo.create(teacher_id, data, test_cases)

    def get(self, assignment_id: int) -> AssignmentDomain:
        domain = self._repo.get(assignment_id)
        if not domain:
            raise NotFoundError("作业不存在")
        return domain

    def list_mine(self, teacher_id: int) -> list[AssignmentDomain]:
        return self._repo.list_by_teacher(teacher_id)

    def list_by_course(self, course_id: int) -> list[AssignmentDomain]:
        return self._repo.list_by_course(course_id)

    async def generate(self, teacher_id: int, course_id: int | None, prompt: str) -> AssignmentDomain:
        if course_id:
            course = self._org_svc.get_course(course_id)
            if course.teacher_id != teacher_id:
                raise ForbiddenError("无权操作该课程下的作业")
        result = await self._generator.generate(prompt)
        data = {
            "course_id": course_id,
            "title": result.title,
            "description": result.description,
            "lang": result.lang,
            "scoring_rubric": result.scoring_rubric,
            "reference_code": result.reference_code,
            "status": "draft",
        }
        test_cases = [tc.model_dump() for tc in result.test_cases]
        return self._repo.create(teacher_id, data, test_cases)

    def update(self, assignment_id: int, payload, teacher_id: int) -> AssignmentDomain:
        domain = self._repo.get(assignment_id)
        if not domain:
            raise NotFoundError("作业不存在")
        if domain.teacher_id != teacher_id:
            raise ForbiddenError()
        data = {
            k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None
        }
        domain = self._repo.update(assignment_id, data)
        return domain

    def delete(self, assignment_id: int, teacher_id: int) -> None:
        domain = self._repo.get(assignment_id)
        if not domain:
            raise NotFoundError("作业不存在")
        if domain.teacher_id != teacher_id:
            raise ForbiddenError()
        self._repo.delete(assignment_id)
