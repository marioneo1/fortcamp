"""Rank-aware critical progression with soft caps and exact percentile confirmation."""
import math

CRITICAL_SOFT_CAPS = {"E": 20, "D": 16, "C": 12, "B": 10, "A": 8, "S": 5}
CRITICAL_STAT_LIMITS = {"E": 100, "D": 100, "C": 100, "B": 49.99, "A": 9.99, "S": 5}
CRITICAL_FLOORS = {"E": 3, "D": 3, "C": 3, "B": 3, "A": 2, "S": 2}
SOFT_CAP_MARGINS = {"E": 12, "D": 12, "C": 12, "B": 12, "A": 8, "S": 8}


def critical_chance(rank, margin):
    """Percentage after a successful check; two decimals match a 10,000-face roll."""
    rank = rank if rank in CRITICAL_SOFT_CAPS else "E"
    margin = max(0, int(margin))
    soft = CRITICAL_SOFT_CAPS[rank]
    knee = SOFT_CAP_MARGINS[rank]
    if margin <= knee:
        chance = CRITICAL_FLOORS[rank] + margin * (soft - CRITICAL_FLOORS[rank]) / knee
    else:
        extra = margin - knee
        if rank in {"E", "D", "C"}:
            # Each additional percentage costs more than the previous one.
            rate = {"E": 10, "D": 8, "C": 3}[rank]
            bend = {"E": 16, "D": 25, "C": 100}[rank]
            chance = soft + rate * (math.sqrt(extra + bend) - math.sqrt(bend))
        elif rank == "B":
            chance = soft + 40 * extra / (extra + 240)
        elif rank == "A":
            chance = soft + 2 * extra / (extra + 80)
        else:
            chance = soft
    # Floor rather than round: B/A must never round up to their forbidden thresholds.
    return min(CRITICAL_STAT_LIMITS[rank], math.floor(chance * 100 + 1e-9) / 100)


def classify_roll(die, total, difficulty, rank="E", available=True, critical_roll=101, severe_failure=True):
    chance = critical_chance(rank, total - difficulty) if available and total >= difficulty else 0
    # Exceptional mastery can make low-rank missions certain, including a natural one.
    if chance == 100:
        return "critical_success"
    if die == 1 or (severe_failure and total <= difficulty - 6):
        return "critical_failure"
    if total < difficulty:
        return "failure"
    if available and critical_roll <= chance:
        return "critical_success"
    return "success"


def outcome_probabilities(bonus, difficulty, rank="E", available=True, severe_failure=True):
    counts = dict.fromkeys(("critical_failure", "failure", "success", "critical_success"), 0)
    for die in range(1, 21):
        total = die + bonus
        chance = critical_chance(rank, total - difficulty) if available and total >= difficulty else 0
        if chance == 100:
            counts["critical_success"] += 10000
            continue
        base = classify_roll(die, total, difficulty, rank, False, severe_failure=severe_failure)
        critical_faces = round(chance * 100) if base == "success" else 0
        counts[base] += 10000 - critical_faces
        counts["critical_success"] += critical_faces
    # Keep sufficient precision so all four preview probabilities sum to exactly 100.
    return {key: round(value / 2000, 4) for key, value in counts.items()}


def scene_critical_chance(history, rank, available):
    if not available or not history or any(h.get("outcome") not in {"success", "critical_success"} for h in history):
        return 0
    checks = [h for h in history if h.get("die") is not None]
    if not checks:
        return 0
    margin = sum(max(0, h["total"] - h["difficulty"]) for h in checks) // len(checks)
    return critical_chance(rank, margin)
