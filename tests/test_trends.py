import pandas as pd

from src.trend_detection import detect_trends


def test_trend_calculation_uses_dynamic_values():
    df = pd.DataFrame(
        {
            "month": ["2026-01", "2026-02", "2026-01", "2026-02"],
            "district": ["North", "North", "South", "South"],
            "anc_coverage": [80, 70, 90, 95],
            "institutional_delivery": [85, 80, 88, 87],
            "immunization": [90, 95, 88, 87],
            "high_risk_cases": [12, 14, 9, 10],
        }
    )
    trends = detect_trends(df, threshold=10)
    assert len(trends) >= 1
    assert any(item["indicator"] in {"anc_coverage", "institutional_delivery", "immunization", "high_risk_cases"} for item in trends)
    assert any(abs(item["change_pct"]) >= 10 for item in trends)


def test_zero_previous_value_is_handled_safely():
    df = pd.DataFrame(
        {
            "month": ["2026-01", "2026-02", "2026-01", "2026-02"],
            "district": ["East", "East", "West", "West"],
            "anc_coverage": [0, 40, 10, 15],
            "institutional_delivery": [50, 55, 0, 12],
            "immunization": [100, 100, 0, 5],
            "high_risk_cases": [7, 8, 0, 2],
        }
    )
    trends = detect_trends(df, threshold=10)
    assert isinstance(trends, list)
    assert all("change_pct" in item for item in trends)
