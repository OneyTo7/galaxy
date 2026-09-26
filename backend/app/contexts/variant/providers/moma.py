from __future__ import annotations

import httpx

from app.contexts.variant.exceptions import VariantError
from app.contexts.variant.schemas import VariantResult
from app.core.config import settings

if not settings.MOCK:
    MOMA_HTTP = httpx.AsyncClient(
        base_url=settings.MOMA_ENDPOINT,
        timeout=httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=5.0),
        limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
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
        raise VariantError("MoMA 真实调用未实现（W3 切真）")
