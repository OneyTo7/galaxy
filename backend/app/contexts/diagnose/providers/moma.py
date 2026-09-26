from __future__ import annotations

import json

from app.contexts.ai.providers.moma import chat
from app.contexts.diagnose.exceptions import ProviderError
from app.contexts.diagnose.schemas import GenerateResult
from app.core.config import settings

_SYSTEM = (
    "你是编程教学误区诊断专家。读取学生代码、编译/运行报错、用例通过情况，"
    "输出 JSON：{\"misconception_type\": str, \"evidence\": str, \"knowledge_point\": str, \"confidence\": float}。"
    "evidence 必须引用真实报错或失败用例，禁止编造。只输出 JSON，不要其他文字。"
)


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
        user = json.dumps(
            {
                "code": code,
                "lang": lang,
                "compile_error": compile_error,
                "run_errors": run_errors,
                "test_results": test_results,
            },
            ensure_ascii=False,
        )
        try:
            content = await chat(_SYSTEM, user)
            data = json.loads(content)
            return GenerateResult(
                data["misconception_type"],
                data["evidence"],
                data["knowledge_point"],
                float(data["confidence"]),
            )
        except RuntimeError as e:
            raise ProviderError(str(e), retryable=False)
        except (ValueError, KeyError) as e:
            raise ProviderError(f"诊断结果解析失败: {e}", retryable=False)
