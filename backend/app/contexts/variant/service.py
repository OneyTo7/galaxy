from __future__ import annotations

from app.contexts.assignment.service import AssignmentService
from app.contexts.diagnose.service import DiagnoseService
from app.contexts.mastery.service import MasteryService
from app.contexts.submission.service import SubmissionService
from app.contexts.variant.exceptions import NoDiagnosisError
from app.contexts.variant.providers.moma import MoMAProvider
from app.contexts.variant.repository import VariantRepoProtocol
from app.contexts.variant.schemas import VariantDomain
from app.core.deps import CurrentUser


class VariantService:
    def __init__(
        self,
        diagnose_svc: DiagnoseService,
        submission_svc: SubmissionService,
        assignment_svc: AssignmentService,
        mastery_svc: MasteryService,
        variant_repo: VariantRepoProtocol,
        moma_provider: MoMAProvider,
    ) -> None:
        self._diagnose_svc = diagnose_svc
        self._submission_svc = submission_svc
        self._assignment_svc = assignment_svc
        self._mastery_svc = mastery_svc
        self._repo = variant_repo
        self._moma = moma_provider

    async def generate(self, submission_id: int, user: CurrentUser) -> VariantDomain:
        submission = self._submission_svc.get_with_permission(submission_id, user)
        diagnoses = self._diagnose_svc.list_by_submission(submission_id)
        if not diagnoses:
            raise NoDiagnosisError()
        latest = diagnoses[0]
        # D3: 幂等——同一诊断已有变式则直接返回（重复请求不重复建练习作业）
        existing = self._repo.latest_for_misconception(latest.id)
        if existing:
            return existing
        # D3: 按掌握度选难度（最近发展区）
        difficulty = self._mastery_svc.difficulty_for(
            latest.knowledge_point_id, submission.user_id
        )
        result = await self._moma.generate(
            latest.misconception_type, latest.knowledge_point, "", difficulty
        )
        # 防御：模型可能不遵守 difficulty 字段，强制对齐
        result = result.model_copy(update={"difficulty": difficulty})
        # D3: 建可提交的 practice 作业（复用整条提交→评测→掌握度管线）
        teacher_id = None  # 系统生成，无教师属主
        cases = [c if isinstance(c, dict) else c.model_dump() for c in result.cases]
        practice = self._assignment_svc.create_practice(
            teacher_id=teacher_id,
            title=result.title,
            description=result.description,
            lang=result.lang,
            cases=cases,
            assigned_user_id=submission.user_id,
        )
        # D3: 给练习作业打知识点标签，使提交后掌握度可追踪（靶向观测）
        if latest.knowledge_point_id is not None:
            self._mastery_svc.tag_practice(practice.id, latest.knowledge_point_id)
        return self._repo.create(
            submission_id, result, latest.id, practice.id
        )

    def list_by_submission(self, submission_id: int) -> list[VariantDomain]:
        return self._repo.list_by_submission(submission_id)
