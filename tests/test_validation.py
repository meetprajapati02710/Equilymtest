import pandas as pd

from src.validation import validate_dataset


def test_validate_dataset_accepts_well_formed_data():
    df = pd.DataFrame(
        {
            "month": ["2026-01", "2026-02"],
            "district": ["A", "B"],
            "anc_coverage": [80, 85],
            "institutional_delivery": [90, 88],
            "immunization": [92, 95],
            "high_risk_cases": [10, 9],
        }
    )
    valid, errors, warnings = validate_dataset(df)
    assert valid is True
    assert errors == []
    assert isinstance(warnings, list)


def test_validate_dataset_reports_missing_values_and_required_columns():
    df = pd.DataFrame({
        "month": ["2026-01", None],
        "district": ["A", "B"],
        "anc_coverage": [80, "bad"],
        "institutional_delivery": [90, 88],
    })
    valid, errors, warnings = validate_dataset(df)
    assert valid is False
    assert len(errors) >= 1
    assert isinstance(warnings, list)
