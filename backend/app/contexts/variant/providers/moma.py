from __future__ import annotations

import json

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.contexts.ai.providers.moma import llm
from app.contexts.variant.exceptions import VariantError
from app.contexts.variant.schemas import VariantResult
from app.core.config import settings

_SYSTEM = (
    "你是编程命题专家。根据学生误区生成换情境的变式题。只输出 JSON。"
)

_parser = PydanticOutputParser(pydantic_object=VariantResult)
_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _SYSTEM + "\n\n{format_instructions}"),
        ("user", "{input}"),
    ]
)


class MoMAProvider:
    async def generate(
        self,
        misconception_type: str,
        knowledge_point: str,
        original_context: str,
    ) -> VariantResult:
        if settings.MOCK:
            return self._mock(misconception_type)
        return await self._call_moma(misconception_type, knowledge_point, original_context)

    @staticmethod
    def _mock(misconception_type: str) -> VariantResult:
        return VariantResult(
            title="矩阵每行最大值",
            description="给定 m×n 矩阵，输出每行最大值（换情境练边界）",
            cases=[{"input": "2 3\n1 2 3\n4 5 6", "expected_output": "3\n6"}],
            scoring_points=["边界处理空矩阵", "二维索引正确"],
            lang="python",
        )

    async def _call_moma(
        self, misconception_type, knowledge_point, original_context
    ) -> VariantResult:
        user = json.dumps(
            {
                "misconception_type": misconception_type,
                "knowledge_point": knowledge_point,
                "original_context": original_context,
            },
            ensure_ascii=False,
        )
        try:
            chain = _PROMPT | llm() | _parser
            return await chain.ainvoke(
                {"input": user, "format_instructions": _parser.get_format_instructions()}
            )
        except Exception as e:
            raise VariantError(f"变式生成失败: {e}")
