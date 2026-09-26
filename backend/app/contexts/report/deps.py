from __future__ import annotations

from fastapi import Depends

from app.contexts.assignment.deps import get_assignment_service
from app.contexts.assignment.service import AssignmentService
from app.contexts.diagnose.deps import get_diagnose_service
from app.contexts.diagnose.service import DiagnoseService
from app.contexts.organization.deps import get_organization_service
from app.contexts.organization.service import OrganizationService
from app.contexts.report.service import ReportService
from app.contexts.submission.deps import get_submission_service
from app.contexts.submission.service import SubmissionService


def get_report_service(
    org_svc: OrganizationService = Depends(get_organization_service),
    assignment_svc: AssignmentService = Depends(get_assignment_service),
    submission_svc: SubmissionService = Depends(get_submission_service),
    diagnose_svc: DiagnoseService = Depends(get_diagnose_service),
) -> ReportService:
    return ReportService(
        org_svc=org_svc,
        assignment_svc=assignment_svc,
        submission_svc=submission_svc,
        diagnose_svc=diagnose_svc,
    )
