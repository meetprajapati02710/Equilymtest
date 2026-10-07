# Automated Insight Generation / Auto-Analytics Engine

## Overview
This project builds a general-purpose analytics engine for district-level healthcare data. It accepts a CSV with one row per district-month pair, validates it, and dynamically generates actionable insights covering trends, outliers, correlations, and threshold breaches. The application works with arbitrary datasets and does not contain district-specific narratives or hardcoded examples.

## Problem statement
Healthcare teams often need a fast way to review monthly district performance without writing custom analysis scripts each time. This engine automatically detects meaningful changes, unusual values, relationships between indicators, and rule-based threshold breaches, then presents the findings in a simple Streamlit UI.

## Features
- CSV upload and validation
- Live district, month, and indicator filters
- Trend detection with a configurable threshold
- IQR and Z-score outlier detection
- Pearson correlation analysis with configurable threshold
- Threshold breach detection for numeric indicators
- Centralized severity scoring
- Dynamic insight generation with structured output
- Plotly charts for severity, correlation heatmap, and district trend lines
- CSV and JSON export

## Architecture
The project follows a data-science pipeline separated into modules:

1. Data loading
2. Validation
3. Filtering
4. Trend detection
5. Outlier detection
6. Correlation detection
7. Threshold breach detection
8. Severity scoring
9. Insight generation
10. Visualization
11. Export

## Project structure

- `app.py` – Streamlit entry point
- `data/sample_healthcare.csv` – demo dataset
- `src/data_loader.py` – CSV loading utilities
- `src/validation.py` – schema and data validation
- `src/trend_detection.py` – trend calculations
- `src/outlier_detection.py` – outlier detection logic
- `src/correlation.py` – Pearson correlation analysis
- `src/threshold_breach.py` – threshold breach detection
- `src/severity.py` – centralized severity scoring
- `src/insight_generator.py` – structured insight generation
- `src/visualization.py` – chart generation
- `tests/` – automated validation tests

## Installation
1. Create a virtual environment if you want one.
2. Install the dependencies:

```bash
pip install -r requirements.txt
```

## How to run
```bash
streamlit run app.py
```

## Input CSV schema
The engine expects a CSV with one row per `(district, month)` pair. Minimum required columns are:

- `month`
- `district`
- `anc_coverage`
- `institutional_delivery`
- `immunization`
- `high_risk_cases`

Additional numeric indicators are supported as long as they are numeric fields.

## Trend detection methodology
For every district-indicator pair, observations are sorted chronologically and the percent change from the immediately preceding period is computed:

$$
\text{pct\_change} = \frac{\text{current} - \text{previous}}{\text{previous}} \times 100
$$

If the previous value is zero, the change is treated as undefined and skipped rather than causing division errors. A trend is flagged when the absolute percentage change exceeds the configured trend threshold. The default threshold is 10%.

## Outlier methodology
The engine supports:

- IQR method: values outside $Q1 - 1.5 \times IQR$ or $Q3 + 1.5 \times IQR$
- Z-score method: values with $|z|$ above the configured threshold

The user can switch between methods and adjust the threshold in the UI.

## Correlation methodology
The engine calculates a Pearson correlation matrix across numeric indicators using pandas. It flags pairs where the absolute value exceeds the configured threshold. The default threshold is 0.70. Correlations are shown only once for each pair to avoid duplicates. The app also warns when the number of observations is too small for stable estimates.

## Severity methodology
Severity is derived from the relative magnitude of the signal compared with the relevant threshold. A centralized scoring function handles the logic so it is easy to adjust:

- Trend: relative to the configured trend threshold
- Outlier: relative to the statistical distance threshold
- Correlation: relative to the configured correlation threshold
- Threshold breach: relative to the configured breach cutoff

The classifications are:

- Low: below 1.5x the reference threshold
- Medium: between 1.5x and 2x the reference threshold
- High: 2x or more the reference threshold

## Insight-generation methodology
The engine builds a reusable structured insight model with fields such as `insight_id`, `type`, `indicator`, `entity`, `period`, `metric`, `prev_value`, `change_pct`, `severity`, and `explanation`. The output is generated from real computed values and template phrasing, not from hardcoded district narratives.

## UI explanation
The Streamlit UI includes:
- CSV upload
- district, month, and indicator filters
- trend and outlier controls
- correlation threshold controls
- breach-threshold controls
- dataset overview
- validation and missing-value reporting
- key metrics
- generated insights table
- severity summary chart
- correlation heatmap
- district trend line chart
- CSV and JSON export buttons

## Output files
The application can export:
- insights CSV
- correlation matrix CSV
- insights JSON

## Limitations
- Correlation can be unstable when the sample size is very small.
- Threshold breach logic is generic and may require domain tuning for a specific indicator profile.
- The app is intended for structured district-level indicator data, not unstructured free-text health records.

## Correlation limitation with small datasets
Pearson correlation is a descriptive statistic and can be unstable when calculated from a very small number of observations. The application warns users when the available data is insufficient to interpret the pattern reliably. Correlation does not imply causation.

## Example output
An example dynamic insight looks like:

> `A district indicator changed by 18.8% from one month to the next, exceeding the configured 10% threshold.`

This pattern is generated from the actual data values and does not rely on hardcoded district or indicator names.

## Future improvements
- Add configurable per-indicator threshold dictionaries
- Support more advanced anomaly detection methods
- Add historical forecast or rolling-window analysis
- Create a multi-page dashboard for multi-dataset comparisons

## Important notes
- The engine is intentionally general-purpose.
- It does not contain district-specific narratives.
- Templates are used only for language generation.
- Numerical values are produced from actual data.
- Correlation does not imply causation.
- Pearson correlations can be unstable with very small sample sizes.
