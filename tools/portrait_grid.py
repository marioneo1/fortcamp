"""Grid-boundary detection for generated portrait contact sheets."""
from __future__ import annotations

from PIL import Image


def _axis_bounds(
    darkness: list[float],
    length: int,
    count: int,
    *,
    minimum_dark_fraction: float,
) -> tuple[list[int], list[dict[str, float | int | bool]]]:
    bounds = [0]
    evidence: list[dict[str, float | int | bool]] = []
    for index in range(1, count):
        expected = round(length * index / count)
        # Generated sheets can contain noticeably uneven row heights. Search up
        # to 40% of one nominal cell around the expected divider while keeping
        # adjacent divider windows separate.
        radius = max(4, round(length / count * 0.40))
        low, high = max(1, expected - radius), min(length - 2, expected + radius)
        detected = max(range(low, high + 1), key=darkness.__getitem__)
        confidence = float(darkness[detected])
        accepted = confidence >= minimum_dark_fraction
        boundary = detected + 1 if accepted else expected
        # A false divider would produce an invalid or tiny cell. Equal spacing is
        # safer whenever the measured boundary is not monotonically plausible.
        minimum_gap = max(2, round(length / count * 0.45))
        if boundary - bounds[-1] < minimum_gap:
            boundary, accepted = expected, False
        bounds.append(boundary)
        evidence.append({
            "expected": expected,
            "detected": detected,
            "dark_fraction": round(confidence, 4),
            "accepted": accepted,
        })
    bounds.append(length)
    return bounds, evidence


def detect_grid_bounds(
    image: Image.Image,
    columns: int,
    rows: int,
    *,
    dark_threshold: int = 55,
    minimum_dark_fraction: float = 0.72,
) -> tuple[list[int], list[int], dict[str, list[dict[str, float | int | bool]]]]:
    """Return x/y cell bounds, falling back to equal spacing without strong lines."""
    gray = image.convert("L")
    width, height = gray.size
    # Pillow performs these binary projections in native code. This stays fast
    # for large generation sheets while preserving one-pixel grid dividers.
    mask = gray.point(lambda value: 255 if value < dark_threshold else 0)
    row_projection = mask.resize((1, height), Image.Resampling.BOX)
    column_projection = mask.resize((width, 1), Image.Resampling.BOX)
    row_darkness = [value / 255 for value in row_projection.tobytes()]
    column_darkness = [value / 255 for value in column_projection.tobytes()]
    y_bounds, y_evidence = _axis_bounds(
        row_darkness, image.height, rows,
        minimum_dark_fraction=minimum_dark_fraction,
    )
    x_bounds, x_evidence = _axis_bounds(
        column_darkness, image.width, columns,
        minimum_dark_fraction=minimum_dark_fraction,
    )
    return x_bounds, y_bounds, {"x": x_evidence, "y": y_evidence}
