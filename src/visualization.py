from __future__ import annotations

import pandas as pd
import plotly.express as px


def _prepare_indicator_timeseries(df: pd.DataFrame, indicator: str, districts: list[str] | None = None) -> pd.DataFrame:
    if df is None or df.empty or indicator is None:
        return pd.DataFrame(columns=["district", "month", indicator])

    working = df.copy()
    working["month"] = pd.to_datetime(working["month"], errors="coerce")
    if districts:
        working = working[working["district"].astype(str).isin(districts)]
    working = working[["district", "month", indicator]].dropna().copy()
    return working


def _summarise_monthly_indicator(df: pd.DataFrame, indicator: str, districts: list[str] | None = None) -> pd.DataFrame:
    working = _prepare_indicator_timeseries(df, indicator, districts)
    if working.empty:
        return pd.DataFrame(columns=["month", indicator])

    summary = (
        working.groupby("month", as_index=False)[indicator]
        .mean()
        .sort_values("month")
        .rename(columns={indicator: indicator})
    )
    summary["month_label"] = summary["month"].dt.strftime("%Y-%m")
    return summary


def plot_severity_summary(insights_df: pd.DataFrame):
    if insights_df is None or insights_df.empty:
        return px.bar(x=["Low", "Medium", "High"], y=[0, 0, 0], title="Severity summary")

    counts = insights_df["severity"].fillna("Low").value_counts().reindex(["Low", "Medium", "High"], fill_value=0)
    fig = px.bar(
        x=["Low", "Medium", "High"],
        y=[counts.get("Low", 0), counts.get("Medium", 0), counts.get("High", 0)],
        color=["Low", "Medium", "High"],
        title="Generated insight severity summary",
        labels={"x": "Severity", "y": "Count"},
    )
    return fig


def plot_correlation_heatmap(correlation_matrix: pd.DataFrame):
    if correlation_matrix is None or correlation_matrix.empty:
        return px.imshow([[0]], text_auto=True, title="Correlation heatmap")

    fig = px.imshow(
        correlation_matrix.round(3),
        text_auto=True,
        aspect="auto",
        labels=dict(x="Indicator", y="Indicator", color="Pearson r"),
        title="Indicator correlation heatmap",
    )
    return fig


def plot_district_line_chart(df: pd.DataFrame, indicator: str, districts: list[str] | None = None):
    if df is None or df.empty or indicator is None:
        return px.line(title="District trend chart")

    working = _prepare_indicator_timeseries(df, indicator, districts)
    if working.empty:
        return px.line(title="District trend chart")

    fig = px.line(
        working,
        x="month",
        y=indicator,
        color="district",
        markers=True,
        title=f"{indicator} over time by district",
    )
    return fig


def plot_monthly_indicator_summary(df: pd.DataFrame, indicator: str, districts: list[str] | None = None):
    summary = _summarise_monthly_indicator(df, indicator, districts)
    if summary.empty:
        return px.line(title=f"{indicator} monthly average trend")

    fig = px.line(
        summary,
        x="month",
        y=indicator,
        markers=True,
        title=f"{indicator} monthly average trend",
        labels={"month": "Month", indicator: indicator},
    )
    fig.update_layout(xaxis_title="Month", yaxis_title=indicator)
    return fig


def plot_monthly_change_bars(df: pd.DataFrame, indicator: str, districts: list[str] | None = None):
    summary = _summarise_monthly_indicator(df, indicator, districts)
    if summary.empty:
        return px.bar(title=f"{indicator} month-over-month change")

    summary = summary.sort_values("month").copy()
    summary["pct_change"] = summary[indicator].pct_change().mul(100).fillna(0)

    fig = px.bar(
        summary,
        x="month_label",
        y="pct_change",
        color="pct_change",
        color_continuous_scale="RdBu",
        title=f"{indicator} month-over-month change (%)",
        labels={"month_label": "Month", "pct_change": "Change (%)"},
    )
    fig.update_layout(xaxis_title="Month", yaxis_title="Change (%)")
    return fig


def plot_latest_district_ranking(df: pd.DataFrame, indicator: str, districts: list[str] | None = None):
    working = _prepare_indicator_timeseries(df, indicator, districts)
    if working.empty:
        return px.bar(title=f"{indicator} latest district ranking")

    latest = working.sort_values("month").groupby("district", as_index=False)[indicator].last()
    latest = latest.sort_values(indicator, ascending=False)

    fig = px.bar(
        latest,
        x=indicator,
        y="district",
        orientation="h",
        color=indicator,
        color_continuous_scale="Viridis",
        title=f"Latest {indicator} by district",
        labels={"district": "District", indicator: indicator},
    )
    fig.update_layout(xaxis_title=indicator, yaxis_title="District")
    return fig
