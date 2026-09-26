from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.contexts.evaluation.schemas import CaseResultOut
from app.contexts.submission.deps import get_submission_service
from app.contexts.submission.schemas import EvaluationOut, SubmissionCreate
from app.contexts.submission.service import SubmissionService
from app.core.deps import get_current_user_id
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/api/submissions", tags=["submission"])


@router.post("", response_model=EvaluationOut, status_code=status.HTTP_201_CREATED)
async def submit(
    req: SubmissionCreate,
    user_id: str = Depends(get_current_user_id),
    svc: SubmissionService = Depends(get_submission_service),
) -> EvaluationOut:
    try:
        domain, results = svc.submit(int(user_id), req.assignment_id, req.code, req.lang)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)
    return EvaluationOut(
        submission_id=domain.id,
        assignment_id=domain.assignment_id,
        score=domain.score,
        status=domain.status,
        results=[
            CaseResultOut(
                case_id=r.case_id, passed=r.passed, stdout=r.stdout,
                stderr=r.stderr, timed_out=r.timed_out, elapsed_ms=r.elapsed_ms,
            )
            for r in results
        ],
    )


@router.get("/{submission_id}/evaluation", response_model=EvaluationOut)
async def get_evaluation(
    submission_id: int,
    user_id: str = Depends(get_current_user_id),
    svc: SubmissionService = Depends(get_submission_service),
) -> EvaluationOut:
    try:
        d = svc.get(submission_id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)
    return EvaluationOut(
        submission_id=d.id,
        assignment_id=d.assignment_id,
        score=d.score,
        status=d.status,
        results=[CaseResultOut(**r) for r in (d.last_result or [])],
    )
