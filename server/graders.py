"""
NexDesk Graders - scoring functions for ticket triage evaluation.
Each grader returns a float in [0.0, 1.0], deterministic for same input.
"""

from typing import Any, Dict, Optional


def _kw_score(text: str, keywords: list[str]) -> float:
    """Score based on how many keywords appear in text (case-insensitive)."""
    if not text or not keywords:
        return 0.0
    text_lower = text.lower()
    hits = sum(1 for kw in keywords if kw.lower() in text_lower)
    return min(hits / max(len(keywords) * 0.4, 1), 1.0)


def _sla_score(predicted: int | None, expected: int) -> float:
    """Score SLA estimate. Exact = 1.0, within 2x = 0.5, beyond = 0.0"""
    if predicted is None:
        return 0.0
    ratio = predicted / expected if expected > 0 else 1.0
    if 0.5 <= ratio <= 2.0:
        return 1.0
    if 0.25 <= ratio <= 4.0:
        return 0.5
    return 0.0


def _priority_score(predicted: str, ground_truth: str, acceptable: list) -> tuple[float, float]:
    """
    Score priority prediction.
    Returns (base_score, max_possible_score)
    """
    pred = (predicted or "").strip().lower()
    if pred == ground_truth:
        return 1.0, 1.0
    if pred in acceptable:
        return 0.5, 1.0
    return 0.0, 1.0


def _category_score(predicted: str, ground_truth: str, acceptable: list) -> tuple[float, float]:
    """Score category prediction."""
    pred = (predicted or "").strip().lower()
    if pred == ground_truth:
        return 1.0, 1.0
    if pred in acceptable:
        return 0.5, 1.0
    return 0.0, 1.0


def _team_score(predicted: str, ground_truth: str, acceptable: list) -> tuple[float, float]:
    """Score team assignment."""
    pred = (predicted or "").strip().lower()
    if pred == ground_truth:
        return 1.0, 1.0
    if pred in acceptable:
        return 0.5, 1.0
    return 0.0, 1.0


def compute_time_penalty(elapsed_minutes: float, sla_deadline: int, stress_level: float) -> float:
    """
    Compute penalty for time pressure.
    - No penalty if under 50% of SLA
    - Linear penalty from 50% to 100%
    - Max 30% penalty + stress multiplier
    """
    if sla_deadline <= 0:
        return 0.0

    ratio = elapsed_minutes / sla_deadline

    if ratio < 0.5:
        return 0.0
    elif ratio < 1.0:
        # Linear penalty from 0 to 0.2
        base_penalty = (ratio - 0.5) * 0.4  # 0 to 0.2
    else:
        # Over SLA: 0.2 + additional penalty
        base_penalty = 0.2 + min((ratio - 1.0) * 0.2, 0.1)  # max 0.3

    # Stress multiplier (high stress = less penalty tolerance)
    stress_multiplier = 1.0 + (stress_level * 0.5)

    return min(base_penalty * stress_multiplier, 0.4)


def compute_confidence_bonus(confidence: float, accuracy: float) -> float:
    """
    Compute bonus/penalty for confidence calibration.
    Well-calibrated agents (confidence ≈ accuracy) get bonus.
    Overconfident wrong answers get penalty.
    """
    if confidence is None:
        return 0.0

    error = abs(confidence - accuracy)

    # Perfect calibration bonus
    if error < 0.1:
        return 0.05  # 5% bonus for well-calibrated

    # Overconfident penalty (confidence >> accuracy)
    if confidence > accuracy + 0.3:
        return -0.1  # 10% penalty for overconfidence

    # Underconfident (slight penalty but less severe)
    if accuracy > confidence + 0.3:
        return -0.03  # 3% penalty for underconfidence

    return 0.0


def get_score_breakdown(
    task: str, step: int, action: Dict[str, Any], ticket: Dict[str, Any]
) -> Dict[str, float]:
    """
    Return detailed score breakdown by dimension.
    Useful for analysis and debugging.
    """
    breakdown = {}

    # Priority score
    pred_priority = (action.get("priority") or "").strip().lower()
    if pred_priority:
        p_score, _ = _priority_score(
            pred_priority, ticket["gt_priority"], ticket.get("gt_priority_ok", [])
        )
        breakdown["priority"] = round(p_score, 4)

    # Category score
    pred_category = (action.get("category") or "").strip().lower()
    if pred_category:
        c_score, _ = _category_score(
            pred_category, ticket["gt_category"], ticket.get("gt_category_ok", [])
        )
        breakdown["category"] = round(c_score, 4)

    # Team score
    pred_team = (action.get("team") or "").strip().lower()
    if pred_team:
        t_score, _ = _team_score(pred_team, ticket["gt_team"], ticket.get("gt_team_ok", []))
        breakdown["team"] = round(t_score, 4)

    # Affected system
    pred_system = (action.get("affected_system") or "").strip().lower()
    gt_system = ticket.get("gt_affected_system", "").lower()
    if pred_system:
        if gt_system and gt_system in pred_system:
            breakdown["affected_system"] = 1.0
        elif pred_system:
            breakdown["affected_system"] = 0.5

    # Response quality
    response = action.get("first_response") or ""
    if response and len(response) > 30:
        kw_score = _kw_score(response, ticket.get("gt_keywords_response", []))
        breakdown["response_quality"] = round(kw_score, 4)

    # Resolution quality
    steps = action.get("resolution_steps") or []
    if isinstance(steps, list) and steps:
        combined = " ".join(steps).lower()
        kw_score = _kw_score(combined, ticket.get("gt_keywords_resolution", []))
        breakdown["resolution_quality"] = round(kw_score, 4)

    # SLA accuracy
    sla = action.get("sla_hours")
    if sla is not None:
        sla_s = _sla_score(sla, ticket.get("gt_sla_hours", 8))
        breakdown["sla_accuracy"] = round(sla_s, 4)

    return breakdown


def grade_classify(action: Dict[str, Any], ticket: Dict[str, Any]) -> float:
    """Task 1: ticket_classify (easy). Max 1.0 = priority(0.5) + category(0.5)."""
    score = 0.0

    # Priority score
    pred_priority = (action.get("priority") or "").strip().lower()
    if pred_priority == ticket["gt_priority"]:
        score += 0.5
    elif pred_priority in ticket.get("gt_priority_ok", []):
        score += 0.25

    # Category score
    pred_category = (action.get("category") or "").strip().lower()
    if pred_category == ticket["gt_category"]:
        score += 0.5
    elif pred_category in ticket.get("gt_category_ok", []):
        score += 0.25

    return round(min(score, 1.0), 4)


def grade_route_step1(action: Dict[str, Any], ticket: Dict[str, Any]) -> float:
    """Task 2 step 1: priority(0.25) + category(0.25) + team(0.35) = 0.85 max."""
    score = 0.0

    pred_priority = (action.get("priority") or "").strip().lower()
    if pred_priority == ticket["gt_priority"]:
        score += 0.25
    elif pred_priority in ticket.get("gt_priority_ok", []):
        score += 0.12

    pred_category = (action.get("category") or "").strip().lower()
    if pred_category == ticket["gt_category"]:
        score += 0.25
    elif pred_category in ticket.get("gt_category_ok", []):
        score += 0.12

    pred_team = (action.get("team") or "").strip().lower()
    if pred_team == ticket["gt_team"]:
        score += 0.35
    elif pred_team in ticket.get("gt_team_ok", []):
        score += 0.17

    return round(min(score, 0.85), 4)


def grade_route_step2(action: Dict[str, Any], ticket: Dict[str, Any]) -> float:
    """Task 2 step 2: affected_system(0.15) to reach total 1.0."""
    pred_system = (action.get("affected_system") or "").strip().lower()
    gt_system = ticket.get("gt_affected_system", "").lower()
    if gt_system and gt_system in pred_system:
        return 0.15
    # partial: at least something provided
    if pred_system:
        return 0.07
    return 0.0


def grade_resolve_step1(action: Dict[str, Any], ticket: Dict[str, Any]) -> float:
    """Task 3 step 1: priority(0.15) + category(0.15) + team(0.15) = 0.45 max."""
    score = 0.0

    pred_priority = (action.get("priority") or "").strip().lower()
    if pred_priority == ticket["gt_priority"]:
        score += 0.15
    elif pred_priority in ticket.get("gt_priority_ok", []):
        score += 0.07

    pred_category = (action.get("category") or "").strip().lower()
    if pred_category == ticket["gt_category"]:
        score += 0.15
    elif pred_category in ticket.get("gt_category_ok", []):
        score += 0.07

    pred_team = (action.get("team") or "").strip().lower()
    if pred_team == ticket["gt_team"]:
        score += 0.15
    elif pred_team in ticket.get("gt_team_ok", []):
        score += 0.07

    return round(min(score, 0.45), 4)


def grade_resolve_step2(action: Dict[str, Any], ticket: Dict[str, Any]) -> float:
    """Task 3 step 2: affected_system(0.10) + first_response(0.20) = 0.30 max."""
    score = 0.0

    # affected system
    pred_system = (action.get("affected_system") or "").strip().lower()
    gt_system = ticket.get("gt_affected_system", "").lower()
    if gt_system and gt_system in pred_system:
        score += 0.10
    elif pred_system:
        score += 0.05

    # first response quality: keyword coverage
    response = action.get("first_response") or ""
    if len(response) > 30:  # must be a real attempt
        kw_score = _kw_score(response, ticket.get("gt_keywords_response", []))
        score += 0.20 * kw_score

    return round(min(score, 0.30), 4)


def grade_resolve_step3(action: Dict[str, Any], ticket: Dict[str, Any]) -> float:
    """Task 3 step 3: resolution_steps(0.15) + sla_hours(0.10) = 0.25 max."""
    score = 0.0

    # resolution steps: list with relevant content
    steps = action.get("resolution_steps") or []
    if isinstance(steps, list) and len(steps) >= 2:
        combined = " ".join(steps).lower()
        kw_score = _kw_score(combined, ticket.get("gt_keywords_resolution", []))
        score += 0.15 * min(kw_score * 1.5, 1.0)
    elif isinstance(steps, list) and len(steps) == 1:
        score += 0.05

    # SLA hours
    sla = action.get("sla_hours")
    score += 0.10 * _sla_score(sla, ticket.get("gt_sla_hours", 8))

    return round(min(score, 0.25), 4)


def grade_crisis_ticket(action: Dict[str, Any], ticket: Dict[str, Any], step: int) -> float:
    """Task 4: crisis_surge. Grade single ticket worth up to 0.10 points."""
    score = 0.0

    pred_priority = (action.get("priority") or "").strip().lower()
    if pred_priority == ticket["gt_priority"]:
        score += 0.03
    elif pred_priority in ticket.get("gt_priority_ok", []):
        score += 0.015

    pred_category = (action.get("category") or "").strip().lower()
    if pred_category == ticket["gt_category"]:
        score += 0.03
    elif pred_category in ticket.get("gt_category_ok", []):
        score += 0.015

    pred_team = (action.get("team") or "").strip().lower()
    if pred_team == ticket["gt_team"]:
        score += 0.04
    elif pred_team in ticket.get("gt_team_ok", []):
        score += 0.02

    # Bonus for handling critical tickets first (steps 1-3)
    if step <= 3 and ticket["gt_priority"] == "critical":
        score += 0.01  # Bonus for correct prioritization

    # Bonus for handling high priority in steps 4-6
    if 4 <= step <= 6 and ticket["gt_priority"] == "high":
        score += 0.005

    return round(min(score, 0.12), 4)


def grade_full_episode(
    task: str, rewards: list[float], metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Compute comprehensive episode metrics.
    Returns breakdown by dimension and aggregate scores.
    """
    total = sum(rewards)

    result = {
        "total_score": round(total, 4),
        "step_rewards": [round(r, 4) for r in rewards],
        "num_steps": len(rewards),
        "avg_step_reward": round(total / len(rewards), 4) if rewards else 0.0,
    }

    if metadata:
        # Include time and confidence metrics
        if "time_penalties" in metadata:
            result["total_time_penalty"] = round(sum(metadata["time_penalties"]), 4)
        if "confidence_bonuses" in metadata:
            result["total_confidence_bonus"] = round(sum(metadata["confidence_bonuses"]), 4)
        if "sla_breaches" in metadata:
            result["sla_breaches"] = metadata["sla_breaches"]

    return result
