from __future__ import annotations

import json

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.contexts.ai.providers.moma import llm
from app.contexts.diagnose.exceptions import ProviderError
from app.contexts.diagnose.schemas import GenerateResult
from app.core.config import settings

_SYSTEM = (
    "你是编程教学误区诊断专家。读取学生代码、编译/运行报错、用例通过情况，"
    "输出结构化结果。evidence 必须引用真实报错或失败用例，禁止编造。只输出 JSON。"
)

_parser = PydanticOutputParser(pydantic_object=GenerateResult)
_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _SYSTEM + "\n\n{format_instructions}"),
        ("user", "{input}"),
    ]
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
                misconception_type="边界条件遗漏",
                evidence=evidence,
                knowledge_point="数组边界 / 循环终止条件",
                confidence=0.80,
            )
        return GenerateResult(
            misconception_type="无明显误区",
            evidence="全部用例通过",
            knowledge_point="—",
            confidence=0.90,
        )

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
            chain = _PROMPT | llm() | _parser
            return await chain.ainvoke(
                {"input": user, "format_instructions": _parser.get_format_instructions()}
            )
        except Exception as e:
            raise ProviderError(f"诊断失败: {e}", retryable=False)
