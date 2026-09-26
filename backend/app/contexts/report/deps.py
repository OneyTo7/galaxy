from __future__ import annotations

from fastapi import Depends

from app.contexts.diagnose.deps import get_diagnose_service
from app.contexts.diagnose.service import DiagnoseService
from app.contexts.report.service import ReportService
from app.contexts.submission.deps import get_submission_service
from app.contexts.submission.service import SubmissionService


def get_report_service(
    submission_svc: SubmissionService = Depends(get_submission_service),
    diagnose_svc: DiagnoseService = Depends(get_diagnose_service),
) -> ReportService:
    return ReportService(submission_svc=submission_svc, diagnose_svc=diagnose_svc)
