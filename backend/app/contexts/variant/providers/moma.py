from __future__ import annotations

import json

from app.contexts.ai.providers.moma import chat
from app.contexts.variant.exceptions import VariantError
from app.contexts.variant.schemas import VariantResult
from app.core.config import settings

_SYSTEM = (
    "你是编程命题专家。根据学生误区生成换情境的变式题，"
    "输出 JSON：{\"title\": str, \"description\": str, "
    "\"cases\": [{\"input\": str, \"expected_output\": str}], "
    "\"scoring_points\": [str], \"lang\": str}。只输出 JSON，不要其他文字。"
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
            content = await chat(_SYSTEM, user)
            data = json.loads(content)
            return VariantResult(
                data["title"],
                data["description"],
                data["cases"],
                data["scoring_points"],
                data.get("lang", "python"),
            )
        except RuntimeError as e:
            raise VariantError(str(e))
        except (ValueError, KeyError) as e:
            raise VariantError(f"变式解析失败: {e}")
