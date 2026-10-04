from __future__ import annotations

from dataclasses import dataclass

from app.contexts.cheating.providers.moma import CheatingProvider
from app.contexts.cheating.repository import CheatingRepoProtocol
from app.contexts.cheating.schemas import CheatingDomain
from app.contexts.cheating.similarity import classify, similarity
from app.contexts.submission.service import SubmissionService
from app.core.deps import CurrentUser


@dataclass(frozen=True)
class _PeerSubmission:
    submission_id: int
    user_id: int
    code: str


class SubmissionPeerRepoProtocol:
    """同班同作业提交数据源（由作弊上下文定义，组合根注入实现）。"""

    def list_peers(self, assignment_id: int, exclude_user_id: int) -> list[_PeerSubmission]: ...


class CheatingService:
    def __init__(
        self,
        submission_svc: SubmissionService,
        cheating_repo: CheatingRepoProtocol,
        cheating_provider: CheatingProvider,
        peer_repo: SubmissionPeerRepoProtocol | None = None,
    ) -> None:
        self._submission_svc = submission_svc
        self._repo = cheating_repo
        self._provider = cheating_provider
        self._peer_repo = peer_repo

    async def check_submission(self, submission_id: int, user: CurrentUser) -> CheatingDomain:
        submission = self._submission_svc.get_with_permission(submission_id, user)
        # D5: 相似度为主——同班同作业两两比对
        if self._peer_repo is not None:
            sim_reports = self._check_similarity(submission_id, submission.user_id, submission.assignment_id)
            if sim_reports:
                # 取最高相似度对作为主报告
                top = max(sim_reports, key=lambda r: r["meta"]["similarity"])
                return self._repo.create(
                    submission_id=submission_id,
                    student_id=submission.user_id,
                    check_type="similarity",
                    score=top["meta"]["similarity"],
                    detail=top["detail"],
                    status=top["status"],
                    meta=top["meta"],
                )
        # 无相似度命中或无同班比对：AI 代写检测为辅，单独命中只产生 suspected
        return await self._check_ai(submission_id, submission.user_id, submission.code, submission.lang)

    def _check_similarity(
        self, submission_id: int, user_id: int, assignment_id: int
    ) -> list[dict]:
        # 通过 SubmissionService 拿当前提交代码
        current = self._submission_svc.get(submission_id)
        peers = self._peer_repo.list_peers(assignment_id, exclude_user_id=user_id) if self._peer_repo else []
        reports: list[dict] = []
        for peer in peers:
            sim = similarity(current.code, peer.code)
            status = classify(sim)
            if status is None:
                continue
            reports.append(
                {
                    "status": status,
                    "detail": f"与用户 {peer.user_id} 代码相似度 {sim}%",
                    "meta": {
                        "partner_id": peer.user_id,
                        "partner_submission_id": peer.submission_id,
                        "similarity": sim,
                    },
                }
            )
        return reports

    async def _check_ai(
        self, submission_id: int, user_id: int, code: str, lang: str
    ) -> CheatingDomain:
        result = await self._provider.detect_ai(code, lang)
        # D5: LLM 判 AI 代写降级为辅助信号——单独命中只 suspected，不再直接 flagged
        if result.is_ai_generated:
            status = "suspected"
        else:
            status = "cleared"
        score = result.confidence if result.is_ai_generated else 0.0
        return self._repo.create(
            submission_id=submission_id,
            student_id=user_id,
            check_type="ai_generated",
            score=score,
            detail=result.reasoning,
            status=status,
        )

    def list_by_submission(self, submission_id: int, user: CurrentUser) -> list[CheatingDomain]:
        self._submission_svc.get_with_permission(submission_id, user)
        return self._repo.list_by_submission(submission_id)
