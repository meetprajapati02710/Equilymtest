import pandas as pd

from src.insight_generator import build_insight_dataframe, generate_dynamic_insight
from src.severity import classify_severity


def test_severity_classification():
    assert classify_severity("trend", 20.0, 10.0) == "High"
    assert classify_severity("trend", 10.0, 10.0) == "Low"


def test_generate_dynamic_insight_uses_live_values():
    insight = generate_dynamic_insight(
        insight_type="trend",
        indicator="coverage",
        entity="Metro",
        period="2026-02",
        metric=75,
        prev_value=60,
        change_pct=25,
        threshold=10,
        severity="High",
        previous_period="2026-01",
    )
    assert "Metro" in insight["explanation"]
    assert "coverage" in insight["explanation"]
    assert "25" in insight["explanation"]


def test_insight_dataframe_has_required_schema_and_ids():
    records = [
        {
            "type": "trend",
            "indicator": "coverage",
            "entity": "Alpha",
            "period": "2026-02",
            "metric": 80,
            "prev_value": 70,
            "change_pct": 14.3,
            "severity": "Medium",
            "explanation": "coverage in Alpha changed by 14.3% from 2026-01 to 2026-02, exceeding the configured 10% threshold.",
        },
        {
            "type": "outlier",
            "indicator": "cases",
            "entity": "Beta",
            "period": "2026-04",
            "metric": 40,
            "prev_value": None,
            "change_pct": None,
            "severity": "Low",
            "explanation": "cases in Beta reached 40 during 2026-04, which is outside the expected distribution according to the selected outlier detection method.",
        },
    ]
    df = build_insight_dataframe(records)
    assert list(df.columns) == ["insight_id", "type", "indicator", "entity", "period", "metric", "change", "prev_value", "change_pct", "severity", "explanation"]
    assert df["insight_id"].iloc[0].startswith("INS-")
    assert df["insight_id"].iloc[1].startswith("INS-")
