import pandas as pd

from src.visualization import (
    plot_latest_district_ranking,
    plot_monthly_change_bars,
    plot_monthly_indicator_summary,
)


def test_trend_visualizations_generate_plot_objects():
    df = pd.DataFrame(
        {
            "month": ["2026-01", "2026-02", "2026-01", "2026-02"],
            "district": ["North", "North", "South", "South"],
            "anc_coverage": [80, 72, 90, 94],
            "immunization": [88, 91, 84, 89],
        }
    )

    summary_fig = plot_monthly_indicator_summary(df, "anc_coverage", ["North", "South"])
    change_fig = plot_monthly_change_bars(df, "anc_coverage", ["North", "South"])
    ranking_fig = plot_latest_district_ranking(df, "anc_coverage", ["North", "South"])

    assert summary_fig is not None
    assert len(summary_fig.data) >= 1
    assert change_fig is not None
    assert len(change_fig.data) >= 1
    assert ranking_fig is not None
    assert len(ranking_fig.data) >= 1
