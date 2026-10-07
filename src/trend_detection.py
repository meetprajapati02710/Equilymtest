from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.severity import classify_severity


def safe_pct_change(current: float, previous: float) -> float:
    if pd.isna(previous) or pd.isna(current):
        return np.nan
    if previous == 0:
        return np.nan
    return ((current - previous) / previous) * 100.0


def detect_trends(df: pd.DataFrame, threshold: float = 10.0) -> list[dict[str, Any]]:
    if df is None or df.empty:
        return []

    working = df.copy()
    if "month" not in working.columns or "district" not in working.columns:
        return []

    working["month"] = pd.to_datetime(working["month"], errors="coerce")
    working = working.dropna(subset=["month", "district"]).copy()
    if working.empty:
        return []

    indicator_cols = [
        column for column in working.columns if column not in {"month", "district"} and pd.api.types.is_numeric_dtype(working[column])
    ]
    if not indicator_cols:
        return []

    records: list[dict[str, Any]] = []

    for district, district_df in working.groupby("district"):
        district_df = district_df.sort_values("month")
        for indicator in indicator_cols:
            for idx in range(1, len(district_df)):
                previous_row = district_df.iloc[idx - 1]
                current_row = district_df.iloc[idx]
                previous_value = previous_row[indicator]
                current_value = current_row[indicator]
                if pd.isna(previous_value) or pd.isna(current_value):
                    continue

                change_pct = safe_pct_change(float(current_value), float(previous_value))
                if np.isnan(change_pct):
                    continue

                if abs(change_pct) >= float(threshold):
                    records.append(
                        {
                            "type": "trend",
                            "indicator": indicator,
                            "entity": str(district),
                            "period": current_row["month"].strftime("%Y-%m"),
                            "metric": float(current_value),
                            "value": float(current_value),
                            "prev_value": float(previous_value),
                            "change_pct": float(change_pct),
                            "severity": classify_severity("trend", abs(change_pct), threshold),
                            "explanation": (
                                f"{indicator} in {district} changed by {change_pct:.2f}% from {previous_row['month'].strftime('%Y-%m')} to {current_row['month'].strftime('%Y-%m')}, "
                                f"exceeding the configured {float(threshold):.0f}% threshold."
                            ),
                        }
                    )

    return records
