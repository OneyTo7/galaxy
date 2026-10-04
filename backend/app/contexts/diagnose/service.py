from __future__ import annotations

from app.contexts.diagnose.providers.moma import MoMAProvider
from app.contexts.diagnose.repository import MisconceptionRepoProtocol
from app.contexts.diagnose.resolver import resolve as resolve_kp
from app.contexts.diagnose.schemas import GenerateResult, MisconceptionDomain
from app.contexts.diagnose.validator import validate_evidence
from app.contexts.evaluation.service import EvaluationService
from app.contexts.submission.service import SubmissionService
from app.core.deps import CurrentUser


class MasteryHookProtocol:
    """诊断入库后触发掌握度记录（由 mastery 上下文在组合根接线）。"""

    def record_diagnosis(
        self, submission_id: int, user_id: int, knowledge_point_id: int | None, confidence: float
    ) -> None: ...


class DiagnoseService:
    def __init__(
        self,
        submission_svc: SubmissionService,
        evaluation_svc: EvaluationService,
        misconception_repo: MisconceptionRepoProtocol,
        moma_provider: MoMAProvider,
        mastery_hook: MasteryHookProtocol | None = None,
        taxonomy_provider=None,
    ) -> None:
        self._submission_svc = submission_svc
        self._evaluation_svc = evaluation_svc
        self._repo = misconception_repo
        self._moma = moma_provider
        self._mastery_hook = mastery_hook
        # taxonomy_provider: callable() -> list[KnowledgePointDomain]，惰性取最新 taxonomy
        self._taxonomy_provider = taxonomy_provider

    def _signals(self, code: str, results: list) -> dict:
        stderrs = [r.stderr for r in results if r.stderr]
        failed = [r.case_id for r in results if not r.passed]
        compile_err = next((r.stderr for r in results if r.stderr), "")
        return {
            "compile_stderr": compile_err,
            "case_stderrs": stderrs,
            "failed_case_ids": failed,
            "code": code,
        }

    async def diagnose(self, submission_id: int, user: CurrentUser) -> MisconceptionDomain:
        submission = self._submission_svc.get_with_permission(submission_id, user)
        results = self._evaluation_svc.list_by_submission(submission_id)
        test_results = [
            {"case_id": r.case_id, "passed": r.passed, "stderr": r.stderr}
            for r in results
        ]
        signals = self._signals(submission.code, results)
        result = await self._moma.diagnose(
            submission.code, submission.lang, "", "", test_results
        )
        # D4: evidence 事实校验，不通过则带提示重试一次
        validated = validate_evidence(result.evidence, signals)
        if not validated:
            retry = await self._moma.diagnose(
                submission.code, submission.lang, "", "", test_results
            )
            if validate_evidence(retry.evidence, signals):
                result, validated = retry, True
        # 仍不通过：降级为规则标签，置信度减半
        if not validated:
            result = self._degrade(result, signals)
        # D1: 收敛到受控知识点体系
        taxonomy = self._taxonomy_provider() if self._taxonomy_provider else []
        kp = resolve_kp(result.knowledge_point_code, result.knowledge_point, taxonomy)
        knowledge_point_id = kp.id if kp else None
        domain = self._repo.create(
            submission_id=submission_id,
            user_id=submission.user_id,
            result=result,
            knowledge_point_id=knowledge_point_id,
            evidence_validated=validated,
        )
        # D2: 触发掌握度记录（诊断是负证据）
        if self._mastery_hook:
            self._mastery_hook.record_diagnosis(
                submission_id, submission.user_id, knowledge_point_id, result.confidence
            )
        return domain

    def _degrade(self, result: GenerateResult, signals: dict) -> GenerateResult:
        """证据未命中真实信号：降级为规则标签，置信度减半。"""
        stderrs = [signals.get("compile_stderr") or ""] + (signals.get("case_stderrs") or [])
        if any(s for s in stderrs):
            mtype = "编译错误"
            ev = stderrs[0] if stderrs[0] else "运行时报错"
        elif signals.get("failed_case_ids"):
            mtype = "用例未通过"
            ev = f"失败用例 {signals['failed_case_ids'][0]}"
        else:
            mtype = "逻辑偏差"
            ev = "输出与预期不符"
        return GenerateResult(
            misconception_type=mtype,
            evidence=ev,
            knowledge_point=result.knowledge_point,
            knowledge_point_code=result.knowledge_point_code,
            confidence=result.confidence / 2,
        )

    def list_by_submission(self, submission_id: int) -> list[MisconceptionDomain]:
        return self._repo.list_by_submission(submission_id)
