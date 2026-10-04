"""D5: 同班同作业代码相似度检测。

归一化 → 词法 token 化 → 标识符/字面量映射 → k-gram 滚动哈希 → winnowing
指纹 → Jaccard 相似度 → 取证片段。纯函数，无 IO，便于单测。
"""

from __future__ import annotations

import re

# 注释与空行过滤
_COMMENT_RE = re.compile(
    r"//[^\n]*|/\*.*?\*/|#[^\n]*|\"\"\"[\s\S]*?\"\"\"|'''[\s\S]*?'''", re.MULTILINE
)
_TOKEN_RE = re.compile(r"[A-Za-z_]\w*|\d+(\.\d+)?|[^\sA-Za-z0-9_]")
_K = 8
_WINDOW = 5


def normalize(code: str) -> str:
    code = _COMMENT_RE.sub(" ", code or "")
    return code


def tokenize(code: str) -> list[str]:
    """词法 token 流；标识符统一为 ID，数字统一为 LIT（挫败改名/换常量）。"""
    tokens = []
    for m in _TOKEN_RE.finditer(code):
        t = m.group(0)
        if t[0].isalpha() or t[0] == "_":
            tokens.append("ID")
        elif t[0].isdigit():
            tokens.append("LIT")
        else:
            tokens.append(t)  # 算子/括号等原文保留
    return tokens


def _hash(seq: list[str]) -> int:
    return hash(tuple(seq))


def fingerprints(tokens: list[str]) -> set[int]:
    """k-gram 滚动窗口 → winnowing 取每窗口最小哈希，返回指纹集合。"""
    if len(tokens) < _K:
        return set()
    hashes = [_hash(tokens[i : i + _K]) for i in range(len(tokens) - _K + 1)]
    if not hashes:
        return set()
    selected: set[int] = set()
    for i in range(0, len(hashes), _WINDOW):
        window = hashes[i : i + _WINDOW]
        if window:
            selected.add(min(window))
    return selected


def similarity(code_a: str, code_b: str) -> float:
    fa = fingerprints(tokenize(normalize(code_a)))
    fb = fingerprints(tokenize(normalize(code_b)))
    if not fa or not fb:
        return 0.0
    inter = len(fa & fb)
    return round(inter / len(fa | fb) * 100, 1)


def classify(sim: float) -> str | None:
    """≥80 flagged；60–79 suspected；<60 不产生报告。"""
    if sim >= 80.0:
        return "flagged"
    if sim >= 60.0:
        return "suspected"
    return None
