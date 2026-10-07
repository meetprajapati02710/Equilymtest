import pandas as pd

from src.correlation import calculate_correlation_matrix, flag_correlation_pairs


def test_correlation_matrix_and_threshold_flagging():
    df = pd.DataFrame(
        {
            "month": ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05"],
            "district": ["A", "B", "C", "D", "E"],
            "indicator_a": [10, 20, 30, 40, 50],
            "indicator_b": [5, 15, 25, 35, 45],
            "indicator_c": [20, 19, 18, 17, 16],
        }
    )
    corr_matrix = calculate_correlation_matrix(df, indicator_cols=["indicator_a", "indicator_b", "indicator_c"])
    assert corr_matrix["indicator_a"]["indicator_b"] > 0.9
    flagged = flag_correlation_pairs(corr_matrix, threshold=0.7)
    assert len(flagged) >= 1
    assert all(item["indicator"] != "indicator_b:indicator_a" for item in flagged)
