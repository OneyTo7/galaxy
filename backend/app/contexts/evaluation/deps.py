from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.contexts.evaluation.repository import SQLEvaluationRepo
from app.contexts.evaluation.service import EvaluationService
from app.core.database import get_db


def get_evaluation_service(db: Session = Depends(get_db)) -> EvaluationService:
    return EvaluationService(repo=SQLEvaluationRepo(db))
