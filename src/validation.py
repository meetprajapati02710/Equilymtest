from __future__ import annotations

from typing import Any

import pandas as pd

REQUIRED_COLUMNS = [
    "month",
    "district",
    "anc_coverage",
    "institutional_delivery",
    "immunization",
    "high_risk_cases",
]


def validate_dataset(df: pd.DataFrame) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if df is None:
        return False, ["No dataset was provided."], []

    if isinstance(df, pd.DataFrame) is False:
        return False, ["The uploaded content is not a valid pandas DataFrame."], []

    if df.empty:
        return False, ["The CSV is empty."], []

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")

    if "month" in df.columns and "district" in df.columns:
        duplicates = df.duplicated(subset=["month", "district"], keep=False)
        if duplicates.any():
            warnings.append("Duplicate (district, month) rows detected. The last occurrence was kept for each pair.")
            df = df.drop_duplicates(subset=["month", "district"], keep="last").reset_index(drop=True)

    if "month" in df.columns:
        parsed_months = pd.to_datetime(df["month"], errors="coerce")
        invalid_months = df.loc[parsed_months.isna(), "month"]
        if not invalid_months.empty:
            errors.append(f"Invalid month values found: {sorted(invalid_months.astype(str).unique())[:5]}")
        df["month"] = parsed_months

    if "district" in df.columns:
        district_values = df["district"].astype(str).str.strip()
        if (district_values == "nan").any() or district_values.eq("").any():
            errors.append("District column contains blank or missing values.")

    numeric_cols = [
        column for column in REQUIRED_COLUMNS if column not in {"month", "district"} and column in df.columns
    ]
    for column in numeric_cols:
        series = pd.to_numeric(df[column], errors="coerce")
        bad_values = df.loc[series.isna() & df[column].notna(), column]
        if not bad_values.empty:
            errors.append(f"Non-numeric values detected in column '{column}'.")
        df[column] = series

    if "month" in df.columns and df["month"].notna().sum() < 2:
        warnings.append("Fewer than two valid months were found. Some trend and correlation analyses may be unstable.")

    missing_value_counts = df.isna().sum()
    columns_with_missing = missing_value_counts[missing_value_counts > 0]
    if not columns_with_missing.empty:
        warnings.append(f"Missing values detected in: {', '.join(columns_with_missing.index.tolist())}.")

    if df.empty:
        errors.append("No usable rows remain after validation.")

    return len(errors) == 0, errors, warnings
