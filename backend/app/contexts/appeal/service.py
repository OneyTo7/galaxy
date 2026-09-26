from __future__ import annotations

from app.contexts.appeal.repository import AppealRepoProtocol
from app.contexts.appeal.schemas import AppealDomain
from app.contexts.submission.service import SubmissionService
from app.core.exceptions import ConflictError, NotFoundError


class AppealService:
    def __init__(
        self,
        submission_svc: SubmissionService,
        appeal_repo: AppealRepoProtocol,
    ) -> None:
        self._submission_svc = submission_svc
        self._repo = appeal_repo

    def create(self, submission_id: int, student_id: int, reason: str) -> AppealDomain:
        self._submission_svc.get(submission_id)
        return self._repo.create(submission_id, student_id, reason)

    def list_pending(self) -> list[AppealDomain]:
        return self._repo.list_pending()

    def list_by_student(self, student_id: int) -> list[AppealDomain]:
        return self._repo.list_by_student(student_id)

    def review(
        self,
        appeal_id: int,
        reviewer_id: int,
        approved: bool,
        comment: str,
        new_score: int | None,
    ) -> AppealDomain:
        appeal = self._repo.get(appeal_id)
        if not appeal:
            raise NotFoundError("申诉不存在")
        if appeal.status != "pending":
            raise ConflictError("申诉已处理")
        domain = self._repo.review(appeal_id, reviewer_id, approved, comment, new_score)
        if approved and new_score is not None:
            self._submission_svc.update_score(appeal.submission_id, new_score)
        return domain
