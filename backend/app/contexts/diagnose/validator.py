"""D4: evidence 事实校验。

LLM 输出的 evidence 必须命中真实信号（报错/失败用例/代码片段），
不命中则视为编造、降级置信、可重试一次。
纯函数，无 IO，便于单测。
"""

from __future__ import annotations

from difflib import SequenceMatcher


def _longest_common_substring_ratio(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).find_longest_match(0, len(a), 0, len(b)).size / max(
        len(a), len(b)
    )


def _token_overlap(a: str, b: str) -> float:
    ta = set(a.lower().split())
    tb = set(b.lower().split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / min(len(ta), len(tb))


def validate_evidence(evidence: str, signals: dict) -> bool:
    """命中任一规则即通过。

    signals = {
        "compile_stderr": str,            # 编译报错
        "case_stderrs": list[str],       # 各用例 stderr
        "failed_case_ids": list[int|str],# 失败用例 id/序号
        "code": str,                     # 学生提交代码
    }
    """
    ev = (evidence or "").strip()
    if not ev:
        return False
    # 1) 与任一 stderr 有 ≥10% 最长公共子串占比（或 token 重叠率 ≥0.3）
    stderrs = [signals.get("compile_stderr") or ""]
    stderrs.extend(signals.get("case_stderrs") or [])
    for s in stderrs:
        if not s:
            continue
        if _longest_common_substring_ratio(ev, s) >= 0.10 or _token_overlap(ev, s) >= 0.30:
            return True
    # 2) evidence 包含失败用例的 case_id / 序号
    for cid in signals.get("failed_case_ids") or []:
        if str(cid) in ev:
            return True
    # 3) evidence 引用的代码片段（≥10 字符）确实出现在提交代码中
    code = signals.get("code") or ""
    if len(code) >= 10 and len(ev) >= 10:
        for win in range(len(ev) - 9):
            frag = ev[win : win + 10]
            if frag in code:
                return True
    return False
