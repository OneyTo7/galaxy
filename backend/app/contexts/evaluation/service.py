from __future__ import annotations

from app.contexts.evaluation import runner
from app.contexts.evaluation.repository import EvaluationRepoProtocol
from app.contexts.evaluation.schemas import CaseResult


class EvaluationService:
    def __init__(self, repo: EvaluationRepoProtocol) -> None:
        self._repo = repo

    def run(
        self, code: str, lang: str, test_cases: list, submission_id: int
    ) -> list[CaseResult]:
        results = runner.run(code, lang, test_cases)
        self._repo.create_many(submission_id, results)
        return results

    @staticmethod
    def score(results: list[CaseResult], test_cases: list) -> int:
        total = sum(tc.weight for tc in test_cases) or 1
        passed = sum(tc.weight for tc, r in zip(test_cases, results) if r.passed)
        return round(passed / total * 100)

    def list_by_submission(self, submission_id: int) -> list[CaseResult]:
        return self._repo.list_by_submission(submission_id)
