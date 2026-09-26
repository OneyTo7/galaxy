from __future__ import annotations

from app.contexts.diagnose.service import DiagnoseService
from app.contexts.variant.exceptions import NoDiagnosisError
from app.contexts.variant.providers.moma import MoMAProvider
from app.contexts.variant.repository import VariantRepoProtocol
from app.contexts.variant.schemas import VariantDomain
from app.core.deps import CurrentUser


class VariantService:
    def __init__(
        self,
        diagnose_svc: DiagnoseService,
        variant_repo: VariantRepoProtocol,
        moma_provider: MoMAProvider,
    ) -> None:
        self._diagnose_svc = diagnose_svc
        self._repo = variant_repo
        self._moma = moma_provider

    async def generate(self, submission_id: int, user: CurrentUser) -> VariantDomain:
        self._diagnose_svc._submission_svc.get_with_permission(submission_id, user)
        diagnoses = self._diagnose_svc.list_by_submission(submission_id)
        if not diagnoses:
            raise NoDiagnosisError()
        latest = diagnoses[0]
        result = await self._moma.generate(
            latest.misconception_type, latest.knowledge_point, ""
        )
        return self._repo.create(submission_id, result)

    def list_by_submission(self, submission_id: int) -> list[VariantDomain]:
        return self._repo.list_by_submission(submission_id)
