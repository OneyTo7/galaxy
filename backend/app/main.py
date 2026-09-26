from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.contexts.ai.providers.moma import close_moma
from app.core.config import settings
from app.core.exceptions import DomainError
from app.contexts.appeal.router import router as appeal_router
from app.contexts.assignment.router import router as assignment_router
from app.contexts.audit.middleware import AuditMiddleware
from app.contexts.audit.router import router as audit_router
from app.contexts.cheating.router import router as cheating_router
from app.contexts.diagnose.router import router as diagnose_router
from app.contexts.grade.router import router as grade_router
from app.contexts.organization.router import router as organization_router
from app.contexts.report.router import router as report_router
from app.contexts.submission.router import router as submission_router
from app.contexts.user.router import router as user_router
from app.contexts.variant.router import router as variant_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_moma()


app = FastAPI(
    title="智学 · AI 认知诊断实验教学平台",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
app.add_middleware(AuditMiddleware)


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    status_map = {
        "not_found": 404, "forbidden": 403, "conflict": 409,
        "unauthorized": 401, "moma_unavailable": 503,
        "provider_error": 503, "variant_error": 503,
        "generation_error": 503, "cheating_error": 503,
    }
    return JSONResponse(
        status_code=status_map.get(exc.code, 400),
        content={"detail": exc.message},
    )


@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

app.include_router(user_router)
app.include_router(assignment_router)
app.include_router(submission_router)
app.include_router(diagnose_router)
app.include_router(variant_router)
app.include_router(report_router)
app.include_router(organization_router)
app.include_router(appeal_router)
app.include_router(cheating_router)
app.include_router(grade_router)
app.include_router(audit_router)


@app.get("/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok"}
