from __future__ import annotations

from typing import Any

import pandas as pd

from src.severity import classify_severity


def detect_threshold_breaches(df: pd.DataFrame, threshold: float = 80.0) -> list[dict[str, Any]]:
    """Flag any value greater than or equal to the configured threshold."""
    if df is None or df.empty:
        return []

    working = df.copy()
    required = {"month", "district"}
    if not required.issubset(working.columns):
        return []

    working["month"] = pd.to_datetime(working["month"], errors="coerce")
    rows: list[dict[str, Any]] = []

    for _, row in working.iterrows():
        for indicator in [col for col in working.columns if col not in {"month", "district"} and pd.api.types.is_numeric_dtype(working[col])]:
            value = row[indicator]
            if pd.isna(value):
                continue
            if float(value) >= float(threshold):
                rows.append(
                    {
                        "type": "threshold_breach",
                        "indicator": indicator,
                        "entity": str(row["district"]),
                        "period": row["month"].strftime("%Y-%m") if pd.notna(row["month"]) else "n/a",
                        "metric": float(value),
                        "value": float(value),
                        "prev_value": None,
                        "change_pct": None,
                        "severity": classify_severity("threshold_breach", value, threshold),
                        "explanation": f"{indicator} in {row['district']} reached {value}, breaching the configured threshold.",
                    }
                )

    return rows
