from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.contexts.audit.deps import get_audit_service
from app.contexts.audit.schemas import AuditDomain, AuditLogOut
from app.contexts.audit.service import AuditService
from app.core.deps import CurrentUser, require_teacher

router = APIRouter(prefix="/api/audit-logs", tags=["audit"])


def _to_out(d: AuditDomain) -> AuditLogOut:
    return AuditLogOut(
        id=d.id, actor_id=d.actor_id, method=d.method, path=d.path,
        status_code=d.status_code, created_at=d.created_at,
    )


@router.get("", response_model=list[AuditLogOut])
async def list_audit(
    limit: int = Query(100, ge=1, le=500),
    teacher: CurrentUser = Depends(require_teacher),
    svc: AuditService = Depends(get_audit_service),
) -> list[AuditLogOut]:
    return [_to_out(d) for d in svc.list_recent(limit)]
