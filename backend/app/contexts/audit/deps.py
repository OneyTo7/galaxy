from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.contexts.audit.repository import SQLAlchemyAuditRepo
from app.contexts.audit.service import AuditService
from app.core.database import get_db


def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    return AuditService(repo=SQLAlchemyAuditRepo(db))
