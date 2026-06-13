"""
Phase 2 Scaffold Viewer.

Standalone Streamlit viewer for Phase 2 scaffold outputs. This viewer is
separate from the main paid simulator dashboard. It is intended for developer
review of Phase 2 assumptions, scenario payoffs, price paths, and comparison
outputs before any Phase 2 model is promoted into the customer-facing dashboard.
"""

from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

try:
    import altair as alt
except Exception:  # Altair normally ships with Streamlit.
    alt = None


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]
OUTPUT_TABLES = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORTS = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

SCENARIO_ASSUMPTIONS_PATH = OUTPUT_TABLES / "scenario_assumptions_scaffold.csv"
SCENARIO_PRICE_PATHS_PATH = OUTPUT_TABLES / "scenario_price_paths_scaffold.csv"
OPTION_PAYOFF_PATH = OUTPUT_TABLES / "option_payoff_scaffold.csv"
SCENARIO_PAYOFF_PATH = OUTPUT_TABLES / "scenario_payoff_scaffold.csv"
SCENARIO_PAYOFF_REPORT_CSV_PATH = OUTPUT_TABLES / "scenario_payoff_report_scaffold.csv"
SCENARIO_PAYOFF_REPORT_HTML_PATH = OUTPUT_REPORTS / "scenario_payoff_report_scaffold.html"
PHASE2_V0_COMPARISON_CSV_PATH = OUTPUT_TABLES / "phase2_v0_comparison_scaffold.csv"
PHASE2_V0_COMPARISON_HTML_PATH = OUTPUT_REPORTS / "phase2_v0_comparison_scaffold.html"

PIPELINE_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase2_pipeline_check.py"
INTEGRATION_READINESS_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase2_integration_readiness_check.py"
ASSUMPTIONS_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_scenario_assumptions_check.py"


st.set_page_config(page_title="Phase 2 Scaffold Viewer", layout="wide")

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1220px;
        padding-top: 2.0rem;
        padding-bottom: 3.0rem;
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 0.65rem;
        padding: 0.7rem 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def open_path_with_windows(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        os.startfile(str(path))  # type: ignore[attr-defined]
        return True
    except Exception:
        return False


def run_python_script(script_path: Path) -> tuple[int, str]:
    if not script_path.exists():
        return 1, f"Script not found: {script_path}"
    completed = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(PROJECT_ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    output = completed.stdout or ""
    if completed.stderr:
        output += "\n--- STDERR ---\n" + completed.stderr
    return completed.returncode, output


def load_csv(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    try:
        return pd.read_csv(path)
    except Exception as exc:
        st.warning(f"Could not read {path.name}: {exc}")
        return None


def normalize_column_name(name: str) -> str:
    return str(name).strip().lower().replace(" ", "_").replace("-", "_")


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    normalized = {normalize_column_name(col): col for col in df.columns}
    for candidate in candidates:
        key = normalize_column_name(candidate)
        if key in normalized:
            return normalized[key]
    for col in df.columns:
        norm = normalize_column_name(col)
        for candidate in candidates:
            if normalize_column_name(candidate) in norm:
                return col
    return None


def signed_currency(value: Any) -> str:
    try:
        number = float(value)
        sign = "+" if number >= 0 else "-"
        return f"{sign}${abs(number):,.2f}"
    except Exception:
        return str(value)


def percent_value(value: Any) -> str:
    try:
        return f"{float(value):.2%}"
    except Exception:
        try:
            return f"{float(value):.2f}%"
        except Exception:
            return str(value)


def compact_bar_chart(df: pd.DataFrame, category_col: str, value_col: str, height: int = 280) -> None:
    chart_df = df[[category_col, value_col]].copy()
    chart_df[value_col] = pd.to_numeric(chart_df[value_col], errors="coerce")
    chart_df = chart_df.dropna(subset=[value_col])
    if chart_df.empty:
        st.info("No numeric chart values were available.")
        return
    chart_df = chart_df.sort_values(value_col, ascending=False)
    if alt is not None:
        chart = (
            alt.Chart(chart_df)
            .mark_bar()
            .encode(
                x=alt.X(f"{value_col}:Q", title="Value"),
                y=alt.Y(f"{category_col}:N", sort="-x", title=None),
                tooltip=[
                    alt.Tooltip(f"{category_col}:N", title="Scenario"),
                    alt.Tooltip(f"{value_col}:Q", title="Value", format=",.2f"),
                ],
            )
            .properties(height=height)
        )
        st.altair_chart(chart, width="stretch")
    else:
        st.bar_chart(chart_df.set_index(category_col)[[value_col]], height=height)


def show_file_status() -> None:
    st.subheader("Phase 2 file status")
    rows = []
    for label, path in [
        ("Scenario assumptions CSV", SCENARIO_ASSUMPTIONS_PATH),
        ("Scenario price paths CSV", SCENARIO_PRICE_PATHS_PATH),
        ("Option payoff CSV", OPTION_PAYOFF_PATH),
        ("Scenario payoff CSV", SCENARIO_PAYOFF_PATH),
        ("Scenario payoff report CSV", SCENARIO_PAYOFF_REPORT_CSV_PATH),
        ("Scenario payoff report HTML", SCENARIO_PAYOFF_REPORT_HTML_PATH),
        ("Phase 2 vs v0 comparison CSV", PHASE2_V0_COMPARISON_CSV_PATH),
        ("Phase 2 vs v0 comparison HTML", PHASE2_V0_COMPARISON_HTML_PATH),
    ]:
        rows.append(
            {
                "Item": label,
                "Status": "FOUND" if path.exists() else "MISSING",
                "Path": str(path),
            }
        )
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)



def show_overview_tab() -> None:
    st.subheader("Phase 2 scaffold overview")
    st.caption("Developer-only review surface for Phase 2 scenario assumptions, payoff scaffolds, and v0 comparison outputs.")

    assumptions_df = load_csv(SCENARIO_ASSUMPTIONS_PATH)
    payoff_df = load_csv(SCENARIO_PAYOFF_REPORT_CSV_PATH)
    comparison_df = load_csv(PHASE2_V0_COMPARISON_CSV_PATH)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Assumption rows", 0 if assumptions_df is None else len(assumptions_df))
    col2.metric("Payoff rows", 0 if payoff_df is None else len(payoff_df))
    col3.metric("Comparison rows", 0 if comparison_df is None else len(comparison_df))
    col4.metric("HTML reports", int(SCENARIO_PAYOFF_REPORT_HTML_PATH.exists()) + int(PHASE2_V0_COMPARISON_HTML_PATH.exists()))

    st.info(
        "Phase 2 is still a scaffold. It is intended to test assumptions and modeling structure before any customer-facing model upgrade. "
        "Use the assumptions tab first, then inspect scenario payoff and Phase 2 vs v0 differences."
    )

    with st.expander("Run Phase 2 checks", expanded=False):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("Run pipeline check"):
                code, output = run_python_script(PIPELINE_CHECK_PATH)
                if code == 0:
                    st.success("Pipeline check passed.")
                else:
                    st.error(f"Pipeline check returned {code}.")
                st.text_area("Pipeline check output", value=output, height=280)
        with col_b:
            if st.button("Run integration-readiness check"):
                code, output = run_python_script(INTEGRATION_READINESS_PATH)
                if code == 0:
                    st.success("Integration-readiness check passed.")
                else:
                    st.error(f"Integration-readiness check returned {code}.")
                st.text_area("Integration-readiness output", value=output, height=280)
        with col_c:
            if st.button("Run assumptions check"):
                code, output = run_python_script(ASSUMPTIONS_CHECK_PATH)
                if code == 0:
                    st.success("Assumptions check passed.")
                else:
                    st.error(f"Assumptions check returned {code}.")
                st.text_area("Assumptions check output", value=output, height=280)

    show_file_status()



def show_assumptions_tab() -> None:
    st.subheader("Scenario assumptions")
    st.caption("Explicit modeled assumptions behind the Phase 2 scaffold scenarios.")
    df = load_csv(SCENARIO_ASSUMPTIONS_PATH)
    if df is None:
        st.info("No scenario assumptions CSV found. Run the scenario-assumptions check first.")
        return

    scenario_col = find_column(df, ["scenario_display_name", "display_name", "scenario_name", "name", "scenario"])
    return_col = find_column(df, ["modeled_total_return", "total_return", "scenario_total_return", "return"])
    vol_col = find_column(df, ["realized_volatility_label", "volatility_label", "realized_vol", "vol_label"])
    iv_col = find_column(df, ["implied_volatility_bias", "iv_bias", "implied_vol_bias"])
    skew_col = find_column(df, ["skew_bias", "skew"])
    profile_col = find_column(df, ["covered_call_profile", "profile"])
    interpretation_col = find_column(df, ["plain_english_interpretation", "interpretation", "description"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Scenarios", len(df))
    if return_col:
        numeric_returns = pd.to_numeric(df[return_col], errors="coerce")
        col2.metric("Lowest modeled return", percent_value(numeric_returns.min()))
        col3.metric("Highest modeled return", percent_value(numeric_returns.max()))
    else:
        col2.metric("Lowest modeled return", "N/A")
        col3.metric("Highest modeled return", "N/A")

    if scenario_col and return_col:
        st.caption("Modeled total return by scenario")
        chart_df = df[[scenario_col, return_col]].copy()
        chart_df[return_col] = pd.to_numeric(chart_df[return_col], errors="coerce")
        compact_bar_chart(chart_df, scenario_col, return_col, height=260)

    st.markdown("### Assumption cards")
    for idx, row in df.iterrows():
        scenario_label = str(row[scenario_col]) if scenario_col else f"Scenario {idx + 1}"
        with st.expander(scenario_label, expanded=False):
            cols = st.columns(4)
            if return_col:
                cols[0].metric("Modeled return", percent_value(row[return_col]))
            if vol_col:
                cols[1].metric("Realized vol", str(row[vol_col]))
            if iv_col:
                cols[2].metric("IV bias", str(row[iv_col]))
            if skew_col:
                cols[3].metric("Skew bias", str(row[skew_col]))
            if profile_col:
                st.write(f"**Covered-call profile:** {row[profile_col]}")
            if interpretation_col:
                st.write(str(row[interpretation_col]))
            st.dataframe(pd.DataFrame([row]), width="stretch", hide_index=True)

    with st.expander("Raw scenario assumptions table", expanded=False):
        st.dataframe(df, width="stretch", hide_index=True)



def show_scenario_payoffs_tab() -> None:
    st.subheader("Scenario payoffs")
    df = load_csv(SCENARIO_PAYOFF_REPORT_CSV_PATH)
    if df is None:
        st.info("No scenario payoff report scaffold CSV found. Run the Phase 2 pipeline first.")
        return

    scenario_col = find_column(df, ["scenario", "scenario_display_name", "scenario_name", "name"])
    relative_col = find_column(df, ["relative_result", "covered_call_minus_buy_hold", "covered_call_minus_buy_and_hold", "relative_p_l"])

    if relative_col:
        values = pd.to_numeric(df[relative_col], errors="coerce")
        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", len(df))
        c2.metric("Best relative result", signed_currency(values.max()))
        c3.metric("Worst relative result", signed_currency(values.min()))

    if scenario_col and relative_col:
        compact_bar_chart(df, scenario_col, relative_col, height=280)

    st.dataframe(df, width="stretch", hide_index=True)

    if SCENARIO_PAYOFF_REPORT_HTML_PATH.exists():
        if st.button("Open scenario payoff HTML report"):
            if not open_path_with_windows(SCENARIO_PAYOFF_REPORT_HTML_PATH):
                st.warning(f"Could not open: {SCENARIO_PAYOFF_REPORT_HTML_PATH}")



def show_phase2_vs_v0_tab() -> None:
    st.subheader("Phase 2 vs v0 comparison")
    df = load_csv(PHASE2_V0_COMPARISON_CSV_PATH)
    if df is None:
        st.info("No Phase 2 vs v0 comparison CSV found. Run the Phase 2 pipeline first.")
        return

    scenario_col = find_column(df, ["scenario", "scenario_display_name", "scenario_name", "name"])
    diff_col = find_column(df, ["difference", "phase2_minus_v0", "phase_2_minus_v0", "phase2_v0_difference"])

    if diff_col:
        diffs = pd.to_numeric(df[diff_col], errors="coerce")
        c1, c2, c3 = st.columns(3)
        c1.metric("Compared rows", len(df))
        c2.metric("Largest Phase 2 increase", signed_currency(diffs.max()))
        c3.metric("Largest Phase 2 decrease", signed_currency(diffs.min()))

    if scenario_col and diff_col:
        compact_bar_chart(df, scenario_col, diff_col, height=280)

    st.dataframe(df, width="stretch", hide_index=True)

    if PHASE2_V0_COMPARISON_HTML_PATH.exists():
        if st.button("Open Phase 2 vs v0 HTML report"):
            if not open_path_with_windows(PHASE2_V0_COMPARISON_HTML_PATH):
                st.warning(f"Could not open: {PHASE2_V0_COMPARISON_HTML_PATH}")



def show_price_paths_tab() -> None:
    st.subheader("Scenario price paths")
    df = load_csv(SCENARIO_PRICE_PATHS_PATH)
    if df is None:
        st.info("No scenario price-path CSV found. Run the price-path check or Phase 2 pipeline first.")
        return

    st.metric("Price-path rows", len(df))

    scenario_col = find_column(df, ["scenario_display_name", "scenario_name", "scenario", "name"])
    step_col = find_column(df, ["step", "path_step", "day"])
    price_col = find_column(df, ["price", "modeled_price", "underlying_price", "stock_price"])

    if alt is not None and scenario_col and step_col and price_col:
        chart_df = df[[scenario_col, step_col, price_col]].copy()
        chart_df[step_col] = pd.to_numeric(chart_df[step_col], errors="coerce")
        chart_df[price_col] = pd.to_numeric(chart_df[price_col], errors="coerce")
        chart_df = chart_df.dropna(subset=[step_col, price_col])
        chart = (
            alt.Chart(chart_df)
            .mark_line()
            .encode(
                x=alt.X(f"{step_col}:Q", title="Step"),
                y=alt.Y(f"{price_col}:Q", title="Modeled price"),
                color=alt.Color(f"{scenario_col}:N", title="Scenario"),
                tooltip=[scenario_col, step_col, price_col],
            )
            .properties(height=360)
        )
        st.altair_chart(chart, width="stretch")
    else:
        st.caption("Could not detect scenario, step, and price columns for a line chart. Showing raw table.")

    with st.expander("Raw price-path table", expanded=False):
        st.dataframe(df, width="stretch", hide_index=True)



def main() -> None:
    st.title("Phase 2 Scaffold Viewer")
    st.caption(f"Project root: {PROJECT_ROOT}")

    overview_tab, assumptions_tab, payoff_tab, comparison_tab, price_paths_tab = st.tabs(
        ["Overview", "Scenario assumptions", "Scenario payoffs", "Phase 2 vs v0", "Price paths"]
    )

    with overview_tab:
        show_overview_tab()
    with assumptions_tab:
        show_assumptions_tab()
    with payoff_tab:
        show_scenario_payoffs_tab()
    with comparison_tab:
        show_phase2_vs_v0_tab()
    with price_paths_tab:
        show_price_paths_tab()


if __name__ == "__main__":
    main()
