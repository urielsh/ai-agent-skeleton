"""Sample blackbox engine — deterministic argument strength scoring.

This is a placeholder engine that demonstrates the INPUT -> ENGINE -> OUTPUT
pattern. Replace this module with your own domain-specific computation logic.

Input fields:
    claim (str): The argument/claim text
    confidence_level (str): "low" | "medium" | "high"
    supporting_reasons (list[str]): Up to 3 supporting reasons
    domain (str, optional): Domain/industry context
    time_horizon (str, optional): Relevant time frame

Output:
    score (int): 1-10 argument strength score
    label (str): "Weak" | "Moderate" | "Strong"
    summary (str): One-paragraph summary
    breakdown (dict): Per-reason sub-scores and component details
"""

from __future__ import annotations

from typing import Any

_CONFIDENCE_MAP = {"low": 1, "medium": 2, "high": 3}


def compute(engine_input: dict[str, Any]) -> dict[str, Any]:
    """Run the blackbox computation on structured input.

    This function is fully deterministic — same input always produces same output.
    """
    claim = str(engine_input.get("claim", ""))
    confidence_level = str(engine_input.get("confidence_level", "low")).lower()
    reasons = engine_input.get("supporting_reasons", [])
    domain = str(engine_input.get("domain", ""))
    time_horizon = str(engine_input.get("time_horizon", ""))

    # 1. Claim detail score (0-3): reward longer, more detailed claims
    claim_words = len(claim.split())
    claim_score = min(3, claim_words // 10)

    # 2. Confidence contribution (1-3)
    confidence_score = _CONFIDENCE_MAP.get(confidence_level, 1)

    # 3. Per-reason quality scores (0-4 each)
    reason_scores = []
    for reason in reasons[:3]:
        words = len(str(reason).split())
        reason_scores.append(min(4, words // 5))

    avg_reason = sum(reason_scores) / max(len(reason_scores), 1)

    # 4. Domain and time horizon bonus (0-1 each)
    domain_bonus = 0.5 if domain.strip() else 0.0
    time_bonus = 0.5 if time_horizon.strip() else 0.0

    # 5. Composite score (weighted average mapped to 1-10)
    raw = (claim_score + confidence_score + avg_reason + domain_bonus + time_bonus)
    max_possible = 3 + 3 + 4 + 0.5 + 0.5  # 11
    normalized = raw / max_possible
    score = max(1, min(10, round(normalized * 10)))

    # 6. Label
    if score <= 3:
        label = "Weak"
    elif score <= 6:
        label = "Moderate"
    else:
        label = "Strong"

    # 7. Summary
    claim_preview = claim[:80] + ("..." if len(claim) > 80 else "")
    summary = (
        f"The argument \"{claim_preview}\" received a {label.lower()} score of {score}/10. "
        f"Based on {len(reasons)} supporting reason(s) with {confidence_level} confidence"
        f"{f' in the {domain} domain' if domain else ''}."
    )

    return {
        "score": score,
        "label": label,
        "summary": summary,
        "breakdown": {
            "claim_detail_score": claim_score,
            "confidence_score": confidence_score,
            "reason_scores": reason_scores,
            "avg_reason_score": round(avg_reason, 2),
            "domain_bonus": domain_bonus,
            "time_bonus": time_bonus,
            "raw_composite": round(raw, 2),
            "max_possible": max_possible,
        },
    }
