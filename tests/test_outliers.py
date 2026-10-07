import pandas as pd

from src.outlier_detection import detect_outliers


def test_iqr_outlier_detection():
    df = pd.DataFrame(
        {
            "month": ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05"],
            "district": ["Alpha", "Bravo", "Charlie", "Delta", "Echo"],
            "metric_a": [10, 11, 12, 13, 100],
            "metric_b": [20, 21, 23, 24, 25],
        }
    )
    outliers = detect_outliers(df, method="IQR", iqr_multiplier=1.5)
    assert any(item["indicator"] == "metric_a" and item["value"] == 100 for item in outliers)


def test_zscore_outlier_detection():
    df = pd.DataFrame(
        {
            "month": ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05"],
            "district": ["North", "South", "East", "West", "Central"],
            "metric_x": [10, 11, 12, 13, 40],
            "metric_y": [20, 22, 21, 23, 24],
        }
    )
    outliers = detect_outliers(df, method="Z-score", z_threshold=1.9)
    assert any(item["indicator"] == "metric_x" and item["value"] == 40 for item in outliers)
