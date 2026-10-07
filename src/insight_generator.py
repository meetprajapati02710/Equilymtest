from __future__ import annotations

from typing import Any

import pandas as pd


def generate_dynamic_insight(
    insight_type: str,
    indicator: str,
    entity: str,
    period: str,
    metric: float | None,
    prev_value: float | None = None,
    change_pct: float | None = None,
    threshold: float | None = None,
    severity: str | None = None,
    previous_period: str | None = None,
    correlation_pair: str | None = None,
    correlation_value: float | None = None,
) -> dict[str, Any]:
    if insight_type == "trend":
        if threshold is None:
            threshold = 0
        change_value = change_pct if change_pct is not None else 0.0
        output = {
            "type": "trend",
            "indicator": indicator,
            "entity": entity,
            "period": str(period),
            "metric": metric,
            "value": metric,
            "prev_value": prev_value,
            "change_pct": change_pct,
            "change": change_pct,
            "severity": severity or "Low",
            "explanation": (
                f"{indicator} in {entity} changed by {float(change_value):.2f}% from {previous_period} to {period}, exceeding the configured {float(threshold):.0f}% threshold."
                if change_pct is not None and previous_period is not None
                else f"{indicator} in {entity} changed by {change_value} from {previous_period} to {period}."
            ),
        }
        return output

    if insight_type == "outlier":
        return {
            "type": "outlier",
            "indicator": indicator,
            "entity": entity,
            "period": str(period),
            "metric": metric,
            "value": metric,
            "prev_value": prev_value,
            "change_pct": change_pct,
            "change": change_pct,
            "severity": severity or "Low",
            "explanation": f"{indicator} in {entity} reached {metric} during {period}, which is outside the expected distribution according to the selected outlier detection method.",
        }

    if insight_type == "correlation":
        if correlation_value is None:
            correlation_value = 0.0
        direction = "positive" if float(correlation_value) >= 0 else "negative"
        pair_a, pair_b = (correlation_pair or "A:B").split(":", 1) if ":" in (correlation_pair or "A:B") else (indicator, "value")
        return {
            "type": "correlation",
            "indicator": correlation_pair or indicator,
            "entity": entity,
            "period": period,
            "metric": float(correlation_value),
            "value": float(correlation_value),
            "prev_value": None,
            "change_pct": None,
            "change": float(correlation_value),
            "severity": severity or "Low",
            "explanation": f"{pair_a} and {pair_b} show a {direction} Pearson correlation of {float(correlation_value):.3f} across the available observations.",
        }

    if insight_type == "threshold_breach":
        return {
            "type": "threshold_breach",
            "indicator": indicator,
            "entity": entity,
            "period": str(period),
            "metric": metric,
            "value": metric,
            "prev_value": prev_value,
            "change_pct": change_pct,
            "change": change_pct,
            "severity": severity or "Low",
            "explanation": f"{indicator} in {entity} reached {metric}, breaching the configured threshold.",
        }

    return {
        "type": insight_type,
        "indicator": indicator,
        "entity": entity,
        "period": str(period),
        "metric": metric,
        "value": metric,
        "prev_value": prev_value,
        "change_pct": change_pct,
        "change": change_pct,
        "severity": severity or "Low",
        "explanation": "Insight generated from the calculated dataset.",
    }


def build_insight_dataframe(records: list[dict[str, Any]]) -> pd.DataFrame:
    columns = [
        "insight_id",
        "type",
        "indicator",
        "entity",
        "period",
        "metric",
        "change",
        "prev_value",
        "change_pct",
        "severity",
        "explanation",
    ]

    if not records:
        return pd.DataFrame(columns=columns)

    normalized = []
    for record in records:
        if record.get("type") is None:
            continue

        insight = {
            "type": record.get("type"),
            "indicator": record.get("indicator"),
            "entity": record.get("entity"),
            "period": record.get("period"),
            "metric": record.get("metric"),
            "change": record.get("change", record.get("change_pct", record.get("metric"))),
            "prev_value": record.get("prev_value"),
            "change_pct": record.get("change_pct"),
            "severity": record.get("severity"),
            "explanation": record.get("explanation"),
        }
        normalized.append(insight)

    df = pd.DataFrame(normalized, columns=["type", "indicator", "entity", "period", "metric", "change", "prev_value", "change_pct", "severity", "explanation"])
    df.insert(0, "insight_id", [f"INS-{idx:04d}" for idx in range(1, len(df) + 1)])
    return df[columns]
