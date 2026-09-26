from __future__ import annotations

import httpx

from app.core.config import settings

if not settings.MOCK:
    MOMA_HTTP = httpx.AsyncClient(
        base_url=settings.MOMA_ENDPOINT,
        timeout=httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=5.0),
        limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
    )
else:
    MOMA_HTTP = None


async def close_moma() -> None:
    if MOMA_HTTP is not None:
        await MOMA_HTTP.aclose()
