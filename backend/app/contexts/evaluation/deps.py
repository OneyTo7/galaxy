from __future__ import annotations

from app.contexts.evaluation.service import EvaluationService


def get_evaluation_service() -> EvaluationService:
    return EvaluationService()
