from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.contexts.evaluation.schemas import CaseResultOut
from app.contexts.submission.deps import get_submission_service
from app.contexts.submission.schemas import EvaluationOut, SubmissionCreate, SubmissionDomain, SubmissionOut
from app.contexts.submission.service import SubmissionService
from app.core.deps import CurrentUser, get_current_user
from app.core.exceptions import ForbiddenError, NotFoundError

router = APIRouter(prefix="/api/submissions", tags=["submission"])


@router.post("", response_model=EvaluationOut, status_code=status.HTTP_201_CREATED)
async def submit(
    req: SubmissionCreate,
    user: CurrentUser = Depends(get_current_user),
    svc: SubmissionService = Depends(get_submission_service),
) -> EvaluationOut:
    try:
        domain, results = svc.submit(user.id, req.assignment_id, req.code, req.lang)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)
    except ForbiddenError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=e.message)
    return EvaluationOut(
        submission_id=domain.id,
        assignment_id=domain.assignment_id,
        score=domain.score,
        status=domain.status,
        results=[],
    )


def _to_out(d: SubmissionDomain) -> SubmissionOut:
    return SubmissionOut(
        id=d.id, user_id=d.user_id, assignment_id=d.assignment_id,
        lang=d.lang, status=d.status, score=d.score, created_at=d.created_at,
    )


@router.get("/mine", response_model=list[SubmissionOut])
async def my_submissions(
    user: CurrentUser = Depends(get_current_user),
    svc: SubmissionService = Depends(get_submission_service),
) -> list[SubmissionOut]:
    return [_to_out(d) for d in svc.list_mine(user.id)]


@router.get("/{submission_id}/evaluation", response_model=EvaluationOut)
async def get_evaluation(
    submission_id: int,
    user: CurrentUser = Depends(get_current_user),
    svc: SubmissionService = Depends(get_submission_service),
) -> EvaluationOut:
    try:
        d, results = svc.get_evaluation(submission_id, user)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.message)
    except ForbiddenError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=e.message)
    return EvaluationOut(
        submission_id=d.id,
        assignment_id=d.assignment_id,
        score=d.score,
        status=d.status,
        results=[
            CaseResultOut(
                case_id=r.case_id, passed=r.passed, stdout=r.stdout,
                stderr=r.stderr, timed_out=r.timed_out, elapsed_ms=r.elapsed_ms,
            )
            for r in results
        ],
    )
