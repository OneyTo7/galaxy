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

    def list_published(self) -> list[AssignmentDomain]:
        return self._repo.list_published()

    def list_practice_for_user(self, user_id: int) -> list[AssignmentDomain]:
        return self._repo.list_practice_for_user(user_id)

    def create_practice(
        self,
        teacher_id: int | None,
        title: str,
        description: str,
        lang: str,
        cases: list[dict],
        assigned_user_id: int,
        knowledge_point_id: int | None = None,
    ) -> AssignmentDomain:
        """D3: 创建变式练习作业（不挂课程，自动 published）。
        若提供 knowledge_point_id，则同步打 Q 矩阵标签，使提交后掌握度可追踪。"""
        data = {
            "course_id": None,
            "title": title,
            "description": description,
            "lang": lang,
            "scoring_rubric": "",
            "reference_code": "",
            "status": "published",
            "kind": "practice",
            "assigned_user_id": assigned_user_id,
        }
        test_cases = [
            {
                "name": tc.get("name", ""),
                "input": tc.get("input", ""),
                "expected_output": tc.get("expected_output", ""),
                "is_hidden": tc.get("is_hidden", False),
                "weight": tc.get("weight", 1),
                "order": idx,
            }
            for idx, tc in enumerate(cases)
        ]
        domain = self._repo.create(teacher_id, data, test_cases)
        if knowledge_point_id is not None:
            self._repo.replace_assignment_tags(domain.id, [(knowledge_point_id, 1.0)])
        return domain

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
