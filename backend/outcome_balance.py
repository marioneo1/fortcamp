"""Shared bounded critical chances; success checks remain independent of loot rolls."""
CRITICAL_CAPS = {"E": 20, "D": 16, "C": 12, "B": 10, "A": 8, "S": 5}


def critical_chance(rank, margin):
    # Close successes stay uncommon; large margins reward developed teams revisiting easy jobs.
    cap = CRITICAL_CAPS.get(rank, CRITICAL_CAPS["E"])
    floor = {"E": 3, "D": 3, "C": 3, "B": 3, "A": 2, "S": 2}.get(rank, 3)
    return min(cap, floor + max(0, int(margin)) * (cap - floor) // 24)


def classify_roll(die, total, difficulty, rank="E", available=True, critical_roll=101, severe_failure=True):
    if die == 1 or (severe_failure and total <= difficulty - 6):
        return "critical_failure"
    if total < difficulty:
        return "failure"
    if available and critical_roll <= critical_chance(rank, total - difficulty):
        return "critical_success"
    return "success"


def outcome_probabilities(bonus, difficulty, rank="E", available=True, severe_failure=True):
    counts = dict.fromkeys(("critical_failure", "failure", "success", "critical_success"), 0)
    for die in range(1, 21):
        base = classify_roll(die, die + bonus, difficulty, rank, False, severe_failure=severe_failure)
        chance = critical_chance(rank, die + bonus - difficulty) if available and base == "success" else 0
        counts[base] += 100 - chance
        counts["critical_success"] += chance
    return {key: round(value / 20, 2) for key, value in counts.items()}


def scene_critical_chance(history, rank, available):
    if not available or not history or any(h.get("outcome") not in {"success", "critical_success"} for h in history):
        return 0
    checks = [h for h in history if h.get("die") is not None]
    if not checks:
        return 0
    margin = sum(max(0, h["total"] - h["difficulty"]) for h in checks) // len(checks)
    return critical_chance(rank, margin)
