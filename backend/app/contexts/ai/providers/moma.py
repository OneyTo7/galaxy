from __future__ import annotations

from typing import Optional

from langchain_openai import ChatOpenAI

from app.core.config import settings

_LLM: Optional[ChatOpenAI] = None


def llm() -> ChatOpenAI:
    """获取 MoMA ChatOpenAI 单例（bulkhead 隔离，统一 client）。"""
    global _LLM
    if _LLM is None:
        _LLM = ChatOpenAI(
            model=settings.MOMA_MODEL,
            base_url=settings.MOMA_ENDPOINT,
            api_key=settings.MOMA_API_KEY,
            timeout=settings.MOMA_TIMEOUT,
            max_tokens=4096,
            temperature=0.2,
            max_retries=settings.MOMA_MAX_RETRIES,
        )
    return _LLM


async def close_moma() -> None:
    global _LLM
    if _LLM is not None:
        await _LLM.aclose()
        _LLM = None
