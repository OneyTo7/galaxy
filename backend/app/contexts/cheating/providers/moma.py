from __future__ import annotations

import json

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.contexts.ai.providers.moma import llm
from app.contexts.cheating.exceptions import CheatingError
from app.contexts.cheating.schemas import AIDetectionResult
from app.core.config import settings

_SYSTEM = (
    "你是代码 AI 代写检测专家。判断代码是否疑似 AI 生成"
    "（过于规范、注释模板化、命名过于完美、缺乏人类常见瑕疵等）。只输出 JSON。"
)

_parser = PydanticOutputParser(pydantic_object=AIDetectionResult)
_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _SYSTEM + "\n\n{format_instructions}"),
        ("user", "{input}"),
    ]
)


class CheatingProvider:
    async def detect_ai(self, code: str, lang: str) -> AIDetectionResult:
        if settings.MOCK:
            return self._mock()
        user = json.dumps({"code": code, "lang": lang}, ensure_ascii=False)
        try:
            chain = _PROMPT | llm() | _parser
            return await chain.ainvoke(
                {"input": user, "format_instructions": _parser.get_format_instructions()}
            )
        except Exception as e:
            raise CheatingError(f"AI 代写检测失败: {e}")

    @staticmethod
    def _mock() -> AIDetectionResult:
        return AIDetectionResult(
            is_ai_generated=False, confidence=0.10, reasoning="mock 不判定"
        )
