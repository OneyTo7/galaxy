from __future__ import annotations

from app.contexts.ai.providers.moma import MOMA_HTTP
from app.contexts.diagnose.exceptions import ProviderError
from app.contexts.diagnose.schemas import GenerateResult
from app.core.config import settings


class MoMAProvider:
    async def diagnose(
        self,
        code: str,
        lang: str,
        compile_error: str,
        run_errors: str,
        test_results: list,
    ) -> GenerateResult:
        if settings.MOCK:
            return self._mock(test_results)
        return await self._call_moma(code, lang, compile_error, run_errors, test_results)

    @staticmethod
    def _mock(test_results: list) -> GenerateResult:
        failed = [r for r in test_results if not r.get("passed")]
        if failed:
            case = failed[0]
            evidence = case.get("stderr") or f"用例 {case.get('case_id')} 未通过"
            return GenerateResult(
                "边界条件遗漏", evidence, "数组边界 / 循环终止条件", 0.80
            )
        return GenerateResult("无明显误区", "全部用例通过", "—", 0.90)

    async def _call_moma(
        self, code, lang, compile_error, run_errors, test_results
    ) -> GenerateResult:
        raise ProviderError("MoMA 真实调用未实现（W3 切真）", retryable=False)
