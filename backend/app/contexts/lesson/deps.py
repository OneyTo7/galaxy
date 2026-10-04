from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.contexts.lesson.repository import SQLAlchemyLessonRepo
from app.contexts.lesson.service import LessonService
from app.contexts.organization.deps import get_organization_service
from app.contexts.organization.service import OrganizationService
from app.core.database import get_db


def get_lesson_service(
    db: Session = Depends(get_db),
    org_svc: OrganizationService = Depends(get_organization_service),
) -> LessonService:
    return LessonService(repo=SQLAlchemyLessonRepo(db), org_svc=org_svc)
