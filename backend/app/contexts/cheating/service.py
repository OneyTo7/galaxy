from __future__ import annotations

from app.contexts.cheating.providers.moma import CheatingProvider
from app.contexts.cheating.repository import CheatingRepoProtocol
from app.contexts.cheating.schemas import CheatingDomain
from app.contexts.submission.service import SubmissionService
from app.core.deps import CurrentUser


class CheatingService:
    def __init__(
        self,
        submission_svc: SubmissionService,
        cheating_repo: CheatingRepoProtocol,
        cheating_provider: CheatingProvider,
    ) -> None:
        self._submission_svc = submission_svc
        self._repo = cheating_repo
        self._provider = cheating_provider

    async def check_submission(self, submission_id: int, user: CurrentUser) -> CheatingDomain:
        submission = self._submission_svc.get_with_permission(submission_id, user)
        result = await self._provider.detect_ai(submission.code, submission.lang)
        score = result.confidence if result.is_ai_generated else 0.0
        status = "flagged" if result.is_ai_generated else "cleared"
        return self._repo.create(
            submission_id, submission.user_id, "ai_generated", score, result.reasoning, status
        )

    def list_by_submission(self, submission_id: int, user: CurrentUser) -> list[CheatingDomain]:
        self._submission_svc.get_with_permission(submission_id, user)
        return self._repo.list_by_submission(submission_id)
