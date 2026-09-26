from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.contexts.audit.repository import SQLAlchemyAuditRepo
from app.core.database import SessionLocal
from app.core.security import decode_token


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        path = request.url.path
        if not path.startswith("/api/"):
            return response
        try:
            actor_id = None
            auth = request.headers.get("authorization", "")
            if auth.startswith("Bearer "):
                payload = decode_token(auth[7:])
                if payload and payload.get("sub"):
                    actor_id = int(payload["sub"])
            db = SessionLocal()
            try:
                SQLAlchemyAuditRepo(db).log(
                    actor_id, request.method, path, response.status_code
                )
            finally:
                db.close()
        except Exception:
            pass
        return response
