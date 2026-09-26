from __future__ import annotations

from app.contexts.ai.providers.moma import MOMA_HTTP
from app.contexts.variant.exceptions import VariantError
from app.contexts.variant.schemas import VariantResult
from app.core.config import settings


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
        raise VariantError("MoMA 真实调用未实现（W3 切真）")
