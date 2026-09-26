from __future__ import annotations

from app.contexts.evaluation import runner
from app.contexts.evaluation.schemas import CaseResult


class EvaluationService:
    def run(self, code: str, lang: str, test_cases: list) -> list[CaseResult]:
        return runner.run(code, lang, test_cases)
