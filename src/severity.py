from __future__ import annotations


def classify_severity(kind: str, value: float, threshold: float) -> str:
    """Classify a signal magnitude as Low, Medium, or High."""
    if threshold is None or threshold == 0:
        return "Low"

    try:
        magnitude = abs(float(value)) / abs(float(threshold))
    except (TypeError, ValueError):
        return "Low"

    if magnitude < 1.5:
        return "Low"
    if magnitude < 2.0:
        return "Medium"
    return "High"
