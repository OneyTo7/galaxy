from __future__ import annotations

import httpx

from app.core.config import settings

if not settings.MOCK:
    MOMA_HTTP = httpx.AsyncClient(
        base_url=settings.MOMA_ENDPOINT,
        timeout=httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=5.0),
        limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        headers={"Authorization": f"Bearer {settings.MOMA_API_KEY}"},
    )
else:
    MOMA_HTTP = None


async def close_moma() -> None:
    if MOMA_HTTP is not None:
        await MOMA_HTTP.aclose()


async def chat(system: str, user: str) -> str:
    if MOMA_HTTP is None:
        raise RuntimeError("MoMA 未配置（MOCK=1 或 endpoint 未设）")
    r = await MOMA_HTTP.post(
        "chat/completions",
        json={
            "model": settings.MOMA_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": 4096,
            "temperature": 0.2,
            "top_p": 0.9,
            "stream": False,
        },
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]
