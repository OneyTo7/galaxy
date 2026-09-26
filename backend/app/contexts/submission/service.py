from __future__ import annotations

from app.contexts.assignment.service import AssignmentService
from app.contexts.evaluation.schemas import CaseResult
from app.contexts.evaluation.service import EvaluationService
from app.contexts.organization.service import OrganizationService
from app.contexts.submission.repository import SubmissionRepoProtocol
from app.contexts.submission.schemas import SubmissionDomain
from app.core.deps import CurrentUser
from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.queue import enqueue_submission


class SubmissionService:
    def __init__(
        self,
        sub_repo: SubmissionRepoProtocol,
        assignment_svc: AssignmentService,
        evaluation_svc: EvaluationService,
        org_svc: OrganizationService,
    ) -> None:
        self._sub_repo = sub_repo
        self._assignment_svc = assignment_svc
        self._evaluation_svc = evaluation_svc
        self._org_svc = org_svc

    def submit(self, user_id: int, assignment_id: int, code: str, lang: str):
        assignment = self._assignment_svc.get(assignment_id)
        if assignment.course_id and not self._org_svc.is_enrolled(user_id, assignment.course_id):
            raise ForbiddenError("未选该课程，无法提交")
        domain = self._sub_repo.create(user_id, assignment_id, code, lang, "pending", 0)
        enqueue_submission(domain.id)
        return domain, []

    def get(self, submission_id: int) -> SubmissionDomain:
        domain = self._sub_repo.get(submission_id)
        if not domain:
            raise NotFoundError("提交不存在")
        return domain

    def get_evaluation(self, submission_id: int, user: CurrentUser) -> tuple[SubmissionDomain, list[CaseResult]]:
        submission = self.get_with_permission(submission_id, user)
        results = self._evaluation_svc.list_by_submission(submission_id)
        return submission, results

    def _check_access(self, submission: SubmissionDomain, user: CurrentUser) -> None:
        if user.role == "student" and submission.user_id != user.id:
            raise ForbiddenError()
        if user.role == "teacher":
            assignment = self._assignment_svc.get(submission.assignment_id)
            if assignment.course_id:
                course = self._org_svc.get_course(assignment.course_id)
                if course.teacher_id != user.id:
                    raise ForbiddenError()

    def get_with_permission(self, submission_id: int, user: CurrentUser) -> SubmissionDomain:
        submission = self._sub_repo.get(submission_id)
        if not submission:
            raise NotFoundError("提交不存在")
        self._check_access(submission, user)
        return submission

    def update_score(self, submission_id: int, score: int) -> None:
        self._sub_repo.update_status_score(submission_id, "done", score)

    def list_by_assignment(self, assignment_id: int) -> list[SubmissionDomain]:
        return self._sub_repo.list_by_assignment(assignment_id)
