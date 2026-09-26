from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.contexts.organization.repository import SQLOrganizationRepo
from app.contexts.organization.service import OrganizationService
from app.core.database import get_db


def get_organization_service(db: Session = Depends(get_db)) -> OrganizationService:
    return OrganizationService(repo=SQLOrganizationRepo(db))
