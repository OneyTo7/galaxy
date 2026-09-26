from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.contexts.appeal.router import router as appeal_router
from app.contexts.assignment.router import router as assignment_router
from app.contexts.diagnose.router import router as diagnose_router
from app.contexts.organization.router import router as organization_router
from app.contexts.report.router import router as report_router
from app.contexts.submission.router import router as submission_router
from app.contexts.user.router import router as user_router
from app.contexts.variant.router import router as variant_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="智学 · AI 认知诊断实验教学平台",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(user_router)
app.include_router(assignment_router)
app.include_router(submission_router)
app.include_router(diagnose_router)
app.include_router(variant_router)
app.include_router(report_router)
app.include_router(organization_router)
app.include_router(appeal_router)


@app.get("/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok"}
