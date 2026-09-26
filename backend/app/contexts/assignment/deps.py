from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.contexts.assignment.providers.moma import AssignmentGenerator
from app.contexts.assignment.repository import SQLAlchemyAssignmentRepo
from app.contexts.assignment.service import AssignmentService
from app.core.database import get_db


def get_assignment_service(db: Session = Depends(get_db)) -> AssignmentService:
    return AssignmentService(repo=SQLAlchemyAssignmentRepo(db), generator=AssignmentGenerator())
