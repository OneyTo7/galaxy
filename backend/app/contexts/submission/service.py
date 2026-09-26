from __future__ import annotations

from app.contexts.assignment.service import AssignmentService
from app.contexts.evaluation.schemas import CaseResult
from app.contexts.evaluation.service import EvaluationService
from app.contexts.submission.repository import SubmissionRepoProtocol
from app.contexts.submission.schemas import SubmissionDomain
from app.core.exceptions import NotFoundError


class SubmissionService:
    def __init__(
        self,
        sub_repo: SubmissionRepoProtocol,
        assignment_svc: AssignmentService,
        evaluation_svc: EvaluationService,
    ) -> None:
        self._sub_repo = sub_repo
        self._assignment_svc = assignment_svc
        self._evaluation_svc = evaluation_svc

    def submit(self, user_id: int, assignment_id: int, code: str, lang: str):
        assignment = self._assignment_svc.get(assignment_id)
        domain = self._sub_repo.create(user_id, assignment_id, code, lang, "pending", 0)
        results: list[CaseResult] = self._evaluation_svc.run(
            code, lang, assignment.test_cases, domain.id
        )

        total = sum(tc.weight for tc in assignment.test_cases) or 1
        passed_weight = sum(
            tc.weight for tc, r in zip(assignment.test_cases, results) if r.passed
        )
        score = round(passed_weight / total * 100)
        domain = self._sub_repo.update_status_score(domain.id, "done", score)
        return domain, results

    def get(self, submission_id: int) -> SubmissionDomain:
        domain = self._sub_repo.get(submission_id)
        if not domain:
            raise NotFoundError("提交不存在")
        return domain

    def get_evaluation(self, submission_id: int) -> list[CaseResult]:
        return self._evaluation_svc.list_by_submission(submission_id)

    def list_by_assignment(self, assignment_id: int) -> list[SubmissionDomain]:
        return self._sub_repo.list_by_assignment(assignment_id)
