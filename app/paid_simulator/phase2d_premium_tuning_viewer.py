"""
phase2d_premium_tuning_viewer.py

Standalone Streamlit viewer for Phase 2D premium-model tuning results.

This viewer is intentionally separate from the main paid simulator dashboard.
It reads the tuning recommendation outputs created by:

    app/run_paid_simulator_premium_model_tuning_check.py

and displays them in a compact browser interface.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

try:
    import altair as alt
except Exception:  # pragma: no cover - optional chart dependency
    alt = None


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CONFIG_DIR = PROJECT_ROOT / "config"

TUNING_CSV = TABLE_DIR / "premium_model_tuning_recommendations.csv"
TUNING_HTML = REPORT_DIR / "premium_model_tuning_recommendations.html"
TUNING_SUMMARY = REPORT_DIR / "premium_model_tuning_summary.txt"
TUNING_CHECK_REPORT = REPORT_DIR / "phase2d_premium_model_tuning_check_report.txt"
TUNING_CONFIG = CONFIG_DIR / "premium_model_tuning_config.json"

OPTION_PREMIUM_CSV = TABLE_DIR / "option_premium_scaffold.csv"
VALIDATION_CSV = TABLE_DIR / "premium_model_validation_scaffold.csv"
PREMIUM_PAYOFF_CSV = TABLE_DIR / "premium_aware_payoff_scaffold.csv"


def read_csv_if_exists(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception as exc:
        st.warning(f"Could not read {path.name}: {exc}")
        return pd.DataFrame()


def read_text_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(errors="replace")
    except Exception as exc:
        return f"Could not read {path.name}: {exc}"


def choose_column(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    normal = {str(c).strip().lower().replace(" ", "_"): c for c in df.columns}
    for candidate in candidates:
        key = candidate.strip().lower().replace(" ", "_")
        if key in normal:
            return normal[key]
    return None


def file_status_rows() -> list[dict[str, str]]:
    paths = [
        ("Tuning recommendations CSV", TUNING_CSV),
        ("Tuning recommendations HTML", TUNING_HTML),
        ("Tuning summary", TUNING_SUMMARY),
        ("Tuning check report", TUNING_CHECK_REPORT),
        ("Tuning config", TUNING_CONFIG),
        ("Option premium CSV", OPTION_PREMIUM_CSV),
        ("Validation CSV", VALIDATION_CSV),
        ("Premium-aware payoff CSV", PREMIUM_PAYOFF_CSV),
    ]
    rows: list[dict[str, str]] = []
    for label, path in paths:
        rows.append(
            {
                "Item": label,
                "Status": "FOUND" if path.exists() else "MISSING",
                "Path": str(path),
            }
        )
    return rows


def show_metric_row(df: pd.DataFrame) -> None:
    rows = len(df)
    status_col = choose_column(df, ["status", "recommendation_status", "check_status"])
    action_col = choose_column(df, ["action", "recommended_action", "recommendation", "tuning_action"])

    tune_count = 0
    review_count = 0
    pass_count = 0

    if status_col:
        status_series = df[status_col].astype(str).str.upper()
        tune_count = int(status_series.str.contains("TUNE", na=False).sum())
        review_count = int(status_series.str.contains("REVIEW", na=False).sum())
        pass_count = int(status_series.str.contains("PASS|OK", regex=True, na=False).sum())
    elif action_col:
        action_series = df[action_col].astype(str).str.upper()
        tune_count = int(action_series.str.contains("TUNE|ADJUST", regex=True, na=False).sum())
        review_count = int(action_series.str.contains("REVIEW|WATCH", regex=True, na=False).sum())

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tuning rows", rows)
    col2.metric("Pass / OK", pass_count)
    col3.metric("Review / watch", review_count)
    col4.metric("Tune / adjust", tune_count)


def show_tuning_chart(df: pd.DataFrame) -> None:
    if df.empty or alt is None:
        return

    status_col = choose_column(df, ["status", "recommendation_status", "check_status"])
    scenario_col = choose_column(df, ["scenario", "scenario_name", "display_name"])
    premium_pct_col = choose_column(
        df,
        [
            "premium_pct_of_stock",
            "premium_percent_of_stock",
            "premium_as_percent_of_stock",
            "estimated_premium_percent",
        ],
    )

    if scenario_col and premium_pct_col:
        chart_df = df[[scenario_col, premium_pct_col]].copy()
        chart_df[premium_pct_col] = pd.to_numeric(chart_df[premium_pct_col], errors="coerce")
        chart_df = chart_df.dropna(subset=[premium_pct_col])
        if not chart_df.empty:
            st.subheader("Premium level by scenario")
            chart = (
                alt.Chart(chart_df)
                .mark_bar()
                .encode(
                    x=alt.X(f"{premium_pct_col}:Q", title="Premium as percent of stock"),
                    y=alt.Y(f"{scenario_col}:N", title="Scenario", sort="-x"),
                    tooltip=[scenario_col, premium_pct_col],
                )
                .properties(height=260)
            )
            st.altair_chart(chart, use_container_width=True)
            return

    if status_col:
        chart_df = df[status_col].astype(str).str.upper().value_counts().reset_index()
        chart_df.columns = ["Status", "Count"]
        st.subheader("Validation / tuning status counts")
        chart = (
            alt.Chart(chart_df)
            .mark_bar()
            .encode(
                x=alt.X("Count:Q", title="Count"),
                y=alt.Y("Status:N", title="Status", sort="-x"),
                tooltip=["Status", "Count"],
            )
            .properties(height=220)
        )
        st.altair_chart(chart, use_container_width=True)


def show_report_links() -> None:
    st.subheader("Generated reports")
    for label, path in [
        ("Premium-model tuning recommendations HTML", TUNING_HTML),
        ("Premium-model tuning summary", TUNING_SUMMARY),
        ("Phase 2D tuning check report", TUNING_CHECK_REPORT),
    ]:
        if path.exists():
            st.markdown(f"- **{label}:** `{path}`")
        else:
            st.markdown(f"- **{label}:** missing")


def main() -> None:
    st.set_page_config(
        page_title="Phase 2D Premium Tuning Viewer",
        layout="wide",
    )

    st.title("Phase 2D Premium-Model Tuning Viewer")
    st.caption("Standalone developer viewer for premium-model tuning recommendations.")

    tuning_df = read_csv_if_exists(TUNING_CSV)
    validation_df = read_csv_if_exists(VALIDATION_CSV)
    premium_df = read_csv_if_exists(OPTION_PREMIUM_CSV)
    payoff_df = read_csv_if_exists(PREMIUM_PAYOFF_CSV)
    tuning_summary = read_text_if_exists(TUNING_SUMMARY)

    tabs = st.tabs(
        [
            "Overview",
            "Tuning recommendations",
            "Validation context",
            "Premium inputs",
            "Payoff context",
            "Files",
        ]
    )

    with tabs[0]:
        st.header("Overview")
        if tuning_df.empty:
            st.warning(
                "No tuning recommendations were found. Run app\\run_paid_simulator_premium_model_tuning_check.py first."
            )
        else:
            show_metric_row(tuning_df)
            show_tuning_chart(tuning_df)

        st.subheader("Summary")
        if tuning_summary:
            st.text(tuning_summary)
        else:
            st.info("No tuning summary text found yet.")
        show_report_links()

    with tabs[1]:
        st.header("Tuning recommendations")
        if tuning_df.empty:
            st.warning("No tuning recommendation CSV found.")
        else:
            st.dataframe(tuning_df, width="stretch", hide_index=True)

    with tabs[2]:
        st.header("Validation context")
        if validation_df.empty:
            st.info("No Phase 2C validation CSV found.")
        else:
            st.dataframe(validation_df, width="stretch", hide_index=True)

    with tabs[3]:
        st.header("Option premium inputs")
        if premium_df.empty:
            st.info("No option premium CSV found.")
        else:
            st.dataframe(premium_df, width="stretch", hide_index=True)

    with tabs[4]:
        st.header("Premium-aware payoff context")
        if payoff_df.empty:
            st.info("No premium-aware payoff CSV found.")
        else:
            st.dataframe(payoff_df, width="stretch", hide_index=True)

    with tabs[5]:
        st.header("File status")
        status_df = pd.DataFrame(file_status_rows())
        st.dataframe(status_df, width="stretch", hide_index=True)


if __name__ == "__main__":
    main()
