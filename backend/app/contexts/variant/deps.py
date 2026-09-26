from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.contexts.diagnose.deps import get_diagnose_service
from app.contexts.diagnose.service import DiagnoseService
from app.contexts.variant.providers.moma import MoMAProvider
from app.contexts.variant.repository import SQLAlchemyVariantRepo
from app.contexts.variant.service import VariantService
from app.core.database import get_db


def get_variant_service(
    db: Session = Depends(get_db),
    diagnose_svc: DiagnoseService = Depends(get_diagnose_service),
) -> VariantService:
    return VariantService(
        diagnose_svc=diagnose_svc,
        variant_repo=SQLAlchemyVariantRepo(db),
        moma_provider=MoMAProvider(),
    )
