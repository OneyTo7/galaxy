"""受控知识点解析：将 LLM 输出的字符串收敛到 taxonomy。"""

from __future__ import annotations

from app.contexts.mastery.schemas import KnowledgePointDomain


def resolve(
    raw_code: str,
    raw_name: str,
    taxonomy: list[KnowledgePointDomain],
) -> KnowledgePointDomain | None:
    """code 精确匹配 → name 精确匹配 → name 模糊包含 → 最近的 category 兜底（不命中则 None）。"""
    if not taxonomy:
        return None
    code = (raw_code or "").strip().lower()
    name = (raw_name or "").strip()
    if code:
        for k in taxonomy:
            if k.code.lower() == code:
                return k
    if name:
        for k in taxonomy:
            if k.name == name:
                return k
        # 模糊包含：双向往返包含
        for k in taxonomy:
            if name in k.name or k.name in name:
                return k
    return None
