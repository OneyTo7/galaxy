from __future__ import annotations

from app.contexts.assignment.service import AssignmentService
from app.contexts.grade.repository import GradeRepoProtocol
from app.contexts.grade.schemas import GradeDomain
from app.contexts.submission.service import SubmissionService
from app.core.deps import CurrentUser
from app.core.exceptions import ForbiddenError


class GradeService:
    def __init__(
        self,
        submission_svc: SubmissionService,
        assignment_svc: AssignmentService,
        grade_repo: GradeRepoProtocol,
    ) -> None:
        self._submission_svc = submission_svc
        self._assignment_svc = assignment_svc
        self._repo = grade_repo

    def generate_gradebook(self, assignment_id: int, user: CurrentUser) -> list[GradeDomain]:
        assignment = self._assignment_svc.get(assignment_id)
        if assignment.teacher_id != user.id:
            raise ForbiddenError()
        submissions = self._submission_svc.list_by_assignment(assignment_id)
        best: dict[int, int] = {}
        for s in submissions:
            if s.status != "done":
                continue
            if s.user_id not in best or s.score > best[s.user_id]:
                best[s.user_id] = s.score
        domains: list[GradeDomain] = []
        for student_id, score in best.items():
            domains.append(self._repo.upsert(assignment_id, student_id, score))
        return domains

    def list_by_assignment(self, assignment_id: int, user: CurrentUser) -> list[GradeDomain]:
        assignment = self._assignment_svc.get(assignment_id)
        if assignment.teacher_id != user.id:
            raise ForbiddenError()
        return self._repo.list_by_assignment(assignment_id)
