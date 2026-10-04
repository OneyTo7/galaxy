"""BKT（贝叶斯知识追踪）纯计算，无 IO，便于单测与调参。"""

from __future__ import annotations

# 全局默认参数（可被 knowledge_points 表按知识点覆盖）
P_INIT = 0.30
P_TRANSIT = 0.20
P_SLIP = 0.10
P_GUESS = 0.20
# 诊断是二手负证据，失手率调高以降权
P_SLIP_DIAGNOSIS = 0.25
# 变式为靶向练习，学习增益更高
VARIANT_TRANSIT_BOOST = 1.5
TRANSIT_CAP = 0.50
# 加权通过率 ≥ 该阈值记为一次正确观测
PASS_RATIO_THRESHOLD = 0.60
# 状态阈值
MASTERED_AT = 0.85
AT_RISK_BELOW = 0.30
AT_RISK_MIN_ATTEMPTS = 2


def posterior(mastery: float, observed: bool, slip: float, guess: float) -> float:
    """似然更新：已知观测结果后，学生已掌握的后验概率。"""
    if observed:
        num = mastery * (1 - slip)
        den = num + (1 - mastery) * guess
    else:
        num = mastery * slip
        den = num + (1 - mastery) * (1 - guess)
    return num / den if den > 0 else mastery


def learn(posterior_mastery: float, transit: float) -> float:
    """学习更新：一次练习后掌握概率的转移。"""
    return posterior_mastery + (1 - posterior_mastery) * min(transit, TRANSIT_CAP)


def update(
    mastery: float,
    observed: bool,
    source: str,
    *,
    slip: float = P_SLIP,
    transit: float = P_TRANSIT,
) -> float:
    if source == "diagnosis":
        slip = max(slip, P_SLIP_DIAGNOSIS)
    if source == "variant":
        transit = min(transit * VARIANT_TRANSIT_BOOST, TRANSIT_CAP)
    return learn(posterior(mastery, observed, slip, P_GUESS), transit)


def status_of(mastery: float, attempts: int) -> str:
    if mastery >= MASTERED_AT:
        return "mastered"
    if mastery < AT_RISK_BELOW and attempts >= AT_RISK_MIN_ATTEMPTS:
        return "at_risk"
    return "learning"


def difficulty_for(mastery: float | None) -> str:
    """按最近发展区选变式难度：未掌握→同型换数，学习中→换情境，接近掌握→组合考点。"""
    if mastery is None or mastery < 0.40:
        return "easy"
    if mastery < 0.70:
        return "medium"
    return "hard"
