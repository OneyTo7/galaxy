from __future__ import annotations

from app.contexts.assignment.providers.moma import AssignmentGenerator
from app.contexts.assignment.repository import AssignmentRepoProtocol
from app.contexts.assignment.schemas import AssignmentDomain
from app.core.exceptions import NotFoundError


class AssignmentService:
    def __init__(self, repo: AssignmentRepoProtocol, generator: AssignmentGenerator) -> None:
        self._repo = repo
        self._generator = generator

    def create(self, teacher_id: int, payload) -> AssignmentDomain:
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

    def update(self, assignment_id: int, payload) -> AssignmentDomain:
        data = {
            k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None
        }
        domain = self._repo.update(assignment_id, data)
        if not domain:
            raise NotFoundError("作业不存在")
        return domain

    def delete(self, assignment_id: int) -> None:
        if not self._repo.delete(assignment_id):
            raise NotFoundError("作业不存在")
