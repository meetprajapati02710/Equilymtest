from __future__ import annotations

from io import StringIO
from pathlib import Path

import pandas as pd
import streamlit as st

from src.correlation import calculate_correlation_matrix, flag_correlation_pairs
from src.data_loader import load_csv_from_input
from src.insight_generator import build_insight_dataframe
from src.outlier_detection import detect_outliers
from src.threshold_breach import detect_threshold_breaches
from src.trend_detection import detect_trends
from src.validation import validate_dataset
from src.visualization import (
    plot_correlation_heatmap,
    plot_district_line_chart,
    plot_latest_district_ranking,
    plot_monthly_change_bars,
    plot_monthly_indicator_summary,
    plot_severity_summary,
)


ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_PATH = ROOT_DIR / "data" / "sample_healthcare.csv"


def get_indicator_columns(frame: pd.DataFrame) -> list[str]:
    return [
        col
        for col in frame.columns
        if col not in {"month", "district"} and pd.api.types.is_numeric_dtype(frame[col])
    ]


def main() -> None:
    st.set_page_config(page_title="Auto-Analytics Engine", layout="wide")
    st.markdown(
        """
        <style>
        :root {
            --ink: #19342f;
            --muted: #60746e;
            --surface: #ffffff;
            --canvas: #f4f8f5;
            --line: #dce8e1;
            --green: #19745e;
            --mint: #e3f4eb;
            --blue: #e6f1fb;
            --yellow: #fff4d2;
            --rose: #fde9e5;
        }
        .stApp { background: var(--canvas); color: var(--ink); }
        header[data-testid="stHeader"],
        [data-testid="stToolbar"] {
            background: #ffffff !important;
            color: #111827 !important;
            border-bottom: 1px solid var(--line);
        }
        header[data-testid="stHeader"] button,
        [data-testid="stToolbar"] button { color: #111827 !important; }
        .block-container { max-width: 1440px; padding-top: 1.4rem; padding-bottom: 3rem; }
        [data-testid="stSidebar"] { background: #edf5f0; border-right: 1px solid var(--line); }
        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: var(--ink); }
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] label p,
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"],
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] * { color: var(--ink) !important; }
        [data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stTickBar"] * {
            color: var(--muted) !important;
        }
        .dashboard-header {
            display: flex; align-items: center; justify-content: space-between; gap: 1rem;
            background: #1d5d4e; color: #fff; border-radius: 12px; padding: 1.25rem 1.5rem;
            margin: 0 0 1.2rem; border-bottom: 5px solid #d7ec7a;
        }
        .dashboard-header h1 { color: #fff; font-size: 1.7rem; margin: 0; line-height: 1.2; }
        .dashboard-header p { color: #d5e9df; margin: 0.35rem 0 0; font-size: 0.95rem; }
        .header-badge {
            color: #183e33; background: #d7ec7a; border-radius: 20px; padding: 0.42rem 0.75rem;
            font-size: 0.75rem; font-weight: 700; white-space: nowrap;
        }
        h2, h3 { color: var(--ink); }
        [data-testid="stMetric"] {
            background: var(--surface); border: 1px solid var(--line); border-radius: 10px;
            padding: 0.8rem 1rem; box-shadow: 0 2px 8px rgba(25, 52, 47, 0.04);
        }
        [data-testid="stHorizontalBlock"] [data-testid="stMetric"] { border-top: 4px solid var(--green); }
        [data-testid="stHorizontalBlock"] [data-testid="stMetric"]:nth-child(2) { border-top-color: #3687bd; }
        [data-testid="stHorizontalBlock"] [data-testid="stMetric"]:nth-child(3) { border-top-color: #e3a62f; }
        [data-testid="stHorizontalBlock"] [data-testid="stMetric"]:nth-child(4) { border-top-color: #df7866; }
        [data-testid="stMetricLabel"] { color: var(--muted); }
        [data-testid="stMetricValue"] { color: var(--ink); }
        .stTabs [role="tablist"] { gap: 0.35rem; border-bottom: 1px solid var(--line); }
        .stTabs [role="tab"] { border-radius: 7px 7px 0 0; padding: 0.6rem 1rem; color: var(--muted); }
        .stTabs [role="tab"][aria-selected="true"] { color: var(--green); background: var(--mint); }
        [data-testid="stDataFrame"], [data-testid="stPlotlyChart"] {
            background: var(--surface); border: 1px solid var(--line); border-radius: 9px; overflow: hidden;
        }
        .stButton button, .stDownloadButton button {
            border-radius: 7px; border: 1px solid #19745e; color: #fff; background: #19745e;
        }
        .stButton button:hover, .stDownloadButton button:hover { background: #125c4a; border-color: #125c4a; color: #fff; }
        [data-testid="stAlert"] { border-radius: 8px; }
        @media (max-width: 700px) {
            .block-container { padding: 1rem 0.8rem 2rem; }
            .dashboard-header { align-items: flex-start; flex-direction: column; padding: 1rem; }
            .dashboard-header h1 { font-size: 1.4rem; }
            .stTabs [role="tablist"] { overflow-x: auto; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <header class="dashboard-header">
            <div>
                <h1>Automated Insight Generation / Auto-Analytics Engine</h1>
                <p>Explore health data, spot changes, and share clear findings.</p>
            </div>
            <span class="header-badge">HEALTH ANALYTICS</span>
        </header>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Your data")
        uploaded_file = st.file_uploader("Upload a healthcare CSV", type=["csv"], help="Use a CSV with month, district, and numeric indicator columns.")
        if uploaded_file is not None:
            df = load_csv_from_input(uploaded_file)
            st.success(f"Loaded {uploaded_file.name}")
        else:
            df = pd.read_csv(DEFAULT_DATA_PATH)
            st.caption("Demo dataset loaded")

        st.subheader("Explore")
        district_options = sorted(df["district"].dropna().astype(str).unique()) if "district" in df.columns else []
        chosen_districts = st.multiselect("District", district_options, default=district_options)

        if "month" in df.columns:
            normalized_months = pd.to_datetime(df["month"], errors="coerce").dt.strftime("%Y-%m")
            month_options = sorted(normalized_months.dropna().unique())
        else:
            month_options = []
        chosen_months = st.multiselect("Month", month_options, default=month_options)

        indicator_options = get_indicator_columns(df)
        chosen_indicator = st.selectbox("Indicator", indicator_options if indicator_options else ["No numeric indicators found"])

        st.subheader("Detection settings")
        trend_threshold = st.slider("Trend threshold (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)
        outlier_method = st.selectbox("Outlier method", ["IQR", "Z-score"])
        z_threshold = st.slider("Z-score threshold", min_value=1.0, max_value=10.0, value=3.0, step=0.1)
        correlation_threshold = st.slider("Correlation threshold |r|", min_value=0.0, max_value=1.0, value=0.7, step=0.01)
        breach_threshold = st.slider("Threshold breach value", min_value=0.0, max_value=100.0, value=80.0, step=0.5)

    valid, errors, warnings = validate_dataset(df)

    if not valid:
        st.error("Dataset validation failed.")
        for error in errors:
            st.write(f"- {error}")
        if warnings:
            for warning in warnings:
                st.warning(warning)
        st.info("The app is ready for a valid CSV upload or can be used with the default demo data.")
        return

    if warnings:
        for warning in warnings:
            st.warning(warning)

    filtered_df = df.copy()
    if chosen_districts:
        filtered_df = filtered_df[filtered_df["district"].astype(str).isin(chosen_districts)]

    if chosen_months:
        if "month" in filtered_df.columns:
            filtered_df = filtered_df.copy()
            filtered_df["month_label"] = pd.to_datetime(filtered_df["month"], errors="coerce").dt.strftime("%Y-%m")
            filtered_df = filtered_df[filtered_df["month_label"].isin(chosen_months)]
            filtered_df = filtered_df.drop(columns=["month_label"], errors="ignore")

    if chosen_indicator and chosen_indicator != "No numeric indicators found":
        filtered_df = filtered_df.copy()

    if filtered_df.empty:
        st.warning("The current filters produce an empty dataset. Adjust the district, month, or indicator selection.")
        return

    if "month" in filtered_df.columns:
        filtered_df["month"] = pd.to_datetime(filtered_df["month"], errors="coerce")
    numeric_indicators = get_indicator_columns(filtered_df)

    metric_cols = {
        "Districts": filtered_df["district"].nunique(),
        "Months": filtered_df["month"].nunique(),
        "Indicators": len(numeric_indicators),
        "Rows": len(filtered_df),
    }
    st.subheader("At a glance")
    metric_cols_display = st.columns(len(metric_cols))
    for idx, (label, value) in enumerate(metric_cols.items()):
        metric_cols_display[idx].metric(label, value)

    trends = detect_trends(filtered_df, threshold=trend_threshold)
    outliers = detect_outliers(filtered_df, method=outlier_method, z_threshold=z_threshold)
    correlation_matrix = calculate_correlation_matrix(filtered_df, indicator_cols=numeric_indicators)
    flagged_correlations = flag_correlation_pairs(correlation_matrix, threshold=correlation_threshold)
    threshold_breaches = detect_threshold_breaches(filtered_df, threshold=breach_threshold)

    insight_records = []
    insight_records.extend(trends)
    insight_records.extend(outliers)
    insight_records.extend(flagged_correlations)
    insight_records.extend(threshold_breaches)
    insights = build_insight_dataframe(insight_records)

    tabs = st.tabs(["Data", "Insights", "Explore trends", "Export"])

    with tabs[0]:
        st.subheader("Your dataset")
        st.dataframe(filtered_df.head(10), width="stretch")

        info_buffer = StringIO()
        filtered_df.info(buf=info_buffer)
        st.subheader("Dataset info")
        st.code(info_buffer.getvalue(), language="text")

        st.subheader("Missing values")
        st.dataframe(filtered_df.isna().sum().rename("missing_count").reset_index().rename(columns={"index": "column"}), width="stretch")

    with tabs[1]:
        st.subheader("Generated insights")
        if insights.empty:
            st.warning("No significant insights were detected using the selected filters and thresholds.")
        else:
            st.dataframe(insights, width="stretch")

    with tabs[2]:
        st.subheader("Trend analysis")
        if chosen_indicator and chosen_indicator != "No numeric indicators found":
            trend_col_a, trend_col_b = st.columns(2)
            with trend_col_a:
                st.plotly_chart(plot_district_line_chart(filtered_df, chosen_indicator, chosen_districts), width="stretch")
            with trend_col_b:
                st.plotly_chart(plot_monthly_indicator_summary(filtered_df, chosen_indicator, chosen_districts), width="stretch")

            st.plotly_chart(plot_monthly_change_bars(filtered_df, chosen_indicator, chosen_districts), width="stretch")
            st.plotly_chart(plot_latest_district_ranking(filtered_df, chosen_indicator, chosen_districts), width="stretch")

        st.subheader("Severity summary")
        st.plotly_chart(plot_severity_summary(insights), width="stretch")

        st.subheader("Correlation matrix")
        if not correlation_matrix.empty:
            st.plotly_chart(plot_correlation_heatmap(correlation_matrix), width="stretch")
            st.dataframe(correlation_matrix.round(3), width="stretch")
        else:
            st.warning("Correlation matrix is unavailable because there are not enough valid numeric columns.")

    with tabs[3]:
        st.subheader("Exports")
        csv_buffer = insights.to_csv(index=False).encode("utf-8")
        st.download_button("Download insights CSV", csv_buffer, file_name="insights.csv", mime="text/csv")

        corr_csv = correlation_matrix.to_csv().encode("utf-8")
        st.download_button("Download correlation matrix CSV", corr_csv, file_name="correlation_matrix.csv", mime="text/csv")

        if not insights.empty:
            json_payload = insights.to_json(orient="records")
            st.download_button("Download insights JSON", data=json_payload, file_name="insights.json", mime="application/json")


if __name__ == "__main__":
    main()
