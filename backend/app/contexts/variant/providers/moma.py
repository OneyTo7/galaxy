from __future__ import annotations

import json

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.contexts.ai.providers.moma import llm
from app.contexts.variant.exceptions import VariantError
from app.contexts.variant.schemas import VariantResult
from app.core.config import settings

_SYSTEM = (
    "你是编程命题专家。根据学生误区生成换情境的变式题，"
    "难度分 easy（同型换数）、medium（换情境）、hard（组合考点）三档。"
    "difficulty 必须与传入要求一致。只输出 JSON。"
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
        difficulty: str = "easy",
    ) -> VariantResult:
        if settings.MOCK:
            return self._mock(misconception_type, difficulty)
        return await self._call_moma(
            misconception_type, knowledge_point, original_context, difficulty
        )

    @staticmethod
    def _mock(misconception_type: str, difficulty: str) -> VariantResult:
        # 难度分档：换数 / 换情境 / 组合考点
        if difficulty == "hard":
            return VariantResult(
                title="矩阵螺旋输出",
                description="给定 m×n 矩阵，按螺旋顺序输出所有元素（组合边界与方向控制）",
                cases=[
                    {"input": "3 3\n1 2 3\n4 5 6\n7 8 9", "expected_output": "1 2 3 6 9 8 7 4 5"},
                    {"input": "1 5\n1 2 3 4 5", "expected_output": "1 2 3 4 5"},
                ],
                scoring_points=["边界处理空矩阵", "方向切换正确", "单行/单列退化"],
                lang="python",
                difficulty="hard",
            )
        if difficulty == "medium":
            return VariantResult(
                title="矩阵每行最大值",
                description="给定 m×n 矩阵，输出每行最大值（换情境练边界）",
                cases=[
                    {"input": "2 3\n1 2 3\n4 5 6", "expected_output": "3\n6"},
                    {"input": "1 1\n7", "expected_output": "7"},
                ],
                scoring_points=["边界处理空矩阵", "二维索引正确"],
                lang="python",
                difficulty="medium",
            )
        return VariantResult(
            title="数组求和",
            description="给定 n 个整数，输出它们的和（同型换数练边界）",
            cases=[
                {"input": "3\n1 2 3", "expected_output": "6"},
                {"input": "0", "expected_output": "0"},
            ],
            scoring_points=["空输入处理", "索引终止条件"],
            lang="python",
            difficulty="easy",
        )

    async def _call_moma(
        self, misconception_type, knowledge_point, original_context, difficulty
    ) -> VariantResult:
        user = json.dumps(
            {
                "misconception_type": misconception_type,
                "knowledge_point": knowledge_point,
                "original_context": original_context,
                "difficulty": difficulty,
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
