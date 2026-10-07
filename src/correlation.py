from __future__ import annotations

from typing import Any

import pandas as pd

from src.severity import classify_severity


def calculate_correlation_matrix(df: pd.DataFrame, indicator_cols: list[str] | None = None) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    working = df.copy()
    if indicator_cols is None:
        indicator_cols = [
            col for col in working.columns if col not in {"month", "district"} and pd.api.types.is_numeric_dtype(working[col])
        ]

    numeric = working[indicator_cols].apply(pd.to_numeric, errors="coerce")
    if numeric.empty or numeric.shape[1] < 2:
        return pd.DataFrame()

    return numeric.corr()


def flag_correlation_pairs(correlation_matrix: pd.DataFrame, threshold: float = 0.7) -> list[dict[str, Any]]:
    if correlation_matrix is None or correlation_matrix.empty:
        return []

    pairs: list[dict[str, Any]] = []
    labels = list(correlation_matrix.columns)

    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            label_a = labels[i]
            label_b = labels[j]
            corr_value = correlation_matrix.iloc[i, j]
            if pd.isna(corr_value):
                continue
            if abs(float(corr_value)) >= abs(float(threshold)):
                direction = "positive" if corr_value >= 0 else "negative"
                pairs.append(
                    {
                        "type": "correlation",
                        "indicator": f"{label_a}:{label_b}",
                        "entity": "overall",
                        "period": "overall",
                        "metric": float(corr_value),
                        "value": float(corr_value),
                        "prev_value": None,
                        "change_pct": None,
                        "severity": classify_severity("correlation", abs(corr_value), threshold),
                        "explanation": (
                            f"{label_a} and {label_b} show a {direction} Pearson correlation of {corr_value:.3f} across the available observations. "
                            "Correlation does not imply causation."
                        ),
                        "change": float(corr_value),
                    }
                )

    return pairs
