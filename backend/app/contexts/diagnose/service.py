from __future__ import annotations

from app.contexts.diagnose.providers.moma import MoMAProvider
from app.contexts.diagnose.repository import MisconceptionRepoProtocol
from app.contexts.diagnose.schemas import MisconceptionDomain
from app.contexts.evaluation.service import EvaluationService
from app.contexts.submission.service import SubmissionService
from app.core.deps import CurrentUser


class DiagnoseService:
    def __init__(
        self,
        submission_svc: SubmissionService,
        evaluation_svc: EvaluationService,
        misconception_repo: MisconceptionRepoProtocol,
        moma_provider: MoMAProvider,
    ) -> None:
        self._submission_svc = submission_svc
        self._evaluation_svc = evaluation_svc
        self._repo = misconception_repo
        self._moma = moma_provider

    async def diagnose(self, submission_id: int, user: CurrentUser) -> MisconceptionDomain:
        submission = self._submission_svc.get_with_permission(submission_id, user)
        results = self._evaluation_svc.list_by_submission(submission_id)
        test_results = [
            {"case_id": r.case_id, "passed": r.passed, "stderr": r.stderr}
            for r in results
        ]
        result = await self._moma.diagnose(
            submission.code, submission.lang, "", "", test_results
        )
        return self._repo.create(submission_id, result)

    def list_by_submission(self, submission_id: int) -> list[MisconceptionDomain]:
        return self._repo.list_by_submission(submission_id)
