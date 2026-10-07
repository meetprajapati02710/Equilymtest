from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.severity import classify_severity


def detect_outliers(
    df: pd.DataFrame,
    method: str = "IQR",
    iqr_multiplier: float = 1.5,
    z_threshold: float = 3.0,
) -> list[dict[str, Any]]:
    if df is None or df.empty:
        return []

    working = df.copy()
    if "month" in working.columns:
        working["month"] = pd.to_datetime(working["month"], errors="coerce")
    working = working.dropna(subset=["month", "district"]).copy()

    indicator_cols = [
        column for column in working.columns if column not in {"month", "district"} and pd.api.types.is_numeric_dtype(working[column])
    ]
    if not indicator_cols:
        return []

    results: list[dict[str, Any]] = []

    for indicator in indicator_cols:
        series = pd.to_numeric(working[indicator], errors="coerce").dropna()
        if series.empty:
            continue

        if method == "IQR":
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - iqr_multiplier * iqr
            upper_bound = q3 + iqr_multiplier * iqr
            mask = (series < lower_bound) | (series > upper_bound)
        else:
            mean_value = series.mean()
            std_value = series.std(ddof=0)
            if pd.isna(std_value) or std_value == 0:
                continue
            z_scores = (series - mean_value) / std_value
            mask = z_scores.abs() >= float(z_threshold)

        for _, value in series[mask].items():
            row = working.loc[working[indicator] == value].iloc[0]
            if method == "IQR":
                severity = classify_severity("outlier", abs(float(value) - float(series.median())), max(float(series.quantile(0.75) - series.quantile(0.25)), 1e-9))
            else:
                mean_value = series.mean()
                std_value = series.std(ddof=0)
                z_score = abs((float(value) - mean_value) / std_value) if std_value else 0.0
                severity = classify_severity("outlier", z_score, z_threshold)

            results.append(
                {
                    "type": "outlier",
                    "indicator": indicator,
                    "entity": str(row["district"]),
                    "period": row["month"].strftime("%Y-%m") if pd.notna(row["month"]) else "n/a",
                    "metric": float(value),
                    "value": float(value),
                    "prev_value": None,
                    "change_pct": None,
                    "severity": severity,
                    "explanation": f"{indicator} in {row['district']} reached {value} during {row['month'].strftime('%Y-%m')}, which is outside the expected distribution according to the selected outlier detection method.",
                }
            )

    return results
