"""
Phase 2B premium-model viewer for the Covered Call Strategy Stress Test.

This standalone Streamlit app displays the premium-aware scaffold outputs.
It is intentionally separate from the main paid-simulator dashboard so the
new premium-pricing work can be inspected without risking the v0.1 dashboard.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

try:
    import altair as alt
except Exception:  # Altair normally ships with Streamlit; fall back if unavailable.
    alt = None


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

OPTION_PREMIUM_PATH = TABLE_DIR / "option_premium_scaffold.csv"
PREMIUM_AWARE_PAYOFF_PATH = TABLE_DIR / "premium_aware_payoff_scaffold.csv"
PREMIUM_VS_SCAFFOLD_PATH = TABLE_DIR / "premium_vs_scaffold_comparison.csv"
PREMIUM_AWARE_REPORT_PATH = REPORT_DIR / "premium_aware_payoff_scaffold.html"
PREMIUM_VS_SCAFFOLD_REPORT_PATH = REPORT_DIR / "premium_vs_scaffold_comparison.html"


st.set_page_config(page_title="Phase 2B Premium Model Viewer", layout="wide")

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


def normalize_column_name(name: Any) -> str:
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


def load_csv(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    try:
        return pd.read_csv(path)
    except Exception as exc:
        st.warning(f"Could not read {path.name}: {exc}")
        return None


def signed_currency(value: Any) -> str:
    try:
        number = float(value)
        sign = "+" if number >= 0 else "-"
        return f"{sign}${abs(number):,.2f}"
    except Exception:
        return str(value)


def percent_text(value: Any) -> str:
    try:
        return f"{float(value):.2f}%"
    except Exception:
        return str(value)


def open_path_with_windows(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        os.startfile(str(path))  # type: ignore[attr-defined]
        return True
    except Exception:
        return False


def compact_horizontal_bar_chart(
    df: pd.DataFrame,
    category_col: str,
    value_col: str,
    title: str | None = None,
    height: int = 280,
) -> bool:
    if alt is None or df is None or df.empty:
        return False
    chart_df = df[[category_col, value_col]].copy()
    chart_df[value_col] = pd.to_numeric(chart_df[value_col], errors="coerce")
    chart_df = chart_df.dropna(subset=[value_col])
    if chart_df.empty:
        return False
    chart_df = chart_df.sort_values(value_col, ascending=False)
    chart = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            x=alt.X(f"{value_col}:Q", title=value_col.replace("_", " ")),
            y=alt.Y(f"{category_col}:N", sort="-x", title=None),
            tooltip=[
                alt.Tooltip(f"{category_col}:N", title="Scenario"),
                alt.Tooltip(f"{value_col}:Q", title=value_col.replace("_", " "), format=",.2f"),
            ],
        )
        .properties(height=height)
    )
    if title:
        chart = chart.properties(title=title)
    st.altair_chart(chart, width="stretch")
    return True


def show_file_status() -> None:
    st.subheader("File status")
    rows = []
    for label, path in [
        ("Option premium CSV", OPTION_PREMIUM_PATH),
        ("Premium-aware payoff CSV", PREMIUM_AWARE_PAYOFF_PATH),
        ("Premium vs scaffold CSV", PREMIUM_VS_SCAFFOLD_PATH),
        ("Premium-aware payoff HTML", PREMIUM_AWARE_REPORT_PATH),
        ("Premium vs scaffold HTML", PREMIUM_VS_SCAFFOLD_REPORT_PATH),
    ]:
        rows.append(
            {
                "Item": label,
                "Status": "FOUND" if path.exists() else "MISSING",
                "Path": str(path),
            }
        )
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def show_overview() -> None:
    st.subheader("Phase 2B premium-model overview")
    st.caption("Standalone viewer for option-premium estimates and premium-aware covered-call payoffs.")

    premium_df = load_csv(OPTION_PREMIUM_PATH)
    payoff_df = load_csv(PREMIUM_AWARE_PAYOFF_PATH)
    comparison_df = load_csv(PREMIUM_VS_SCAFFOLD_PATH)

    col1, col2, col3 = st.columns(3)
    col1.metric("Premium scenarios", 0 if premium_df is None else len(premium_df))
    col2.metric("Payoff scenarios", 0 if payoff_df is None else len(payoff_df))
    col3.metric("Comparison rows", 0 if comparison_df is None else len(comparison_df))

    if premium_df is None or payoff_df is None or comparison_df is None:
        st.warning("One or more Phase 2B output files are missing. Run the premium-model, premium-aware payoff, and premium-vs-scaffold checks first.")
    else:
        st.success("Phase 2B premium-aware scaffold outputs are available.")

    show_file_status()

    st.markdown("### Suggested workflow")
    st.write("1. Review option premium estimates.")
    st.write("2. Review premium-aware payoff results.")
    st.write("3. Compare premium-aware results against the older Phase 2 payoff scaffold.")
    st.write("4. Use this viewer for development inspection before integrating Phase 2B into the main dashboard.")


def show_option_premiums() -> None:
    st.subheader("Option premium estimates")
    df = load_csv(OPTION_PREMIUM_PATH)
    if df is None or df.empty:
        st.info("No option_premium_scaffold.csv found. Run run_paid_simulator_option_premium_check.py first.")
        return

    scenario_col = find_column(df, ["scenario_display_name", "display_name", "scenario_name", "scenario"])
    premium_col = find_column(df, ["estimated_call_premium", "call_premium", "premium"])
    strike_col = find_column(df, ["estimated_call_strike", "call_strike", "strike"])
    delta_col = find_column(df, ["estimated_call_delta", "call_delta", "delta"])
    iv_col = find_column(df, ["scenario_implied_volatility", "implied_volatility", "iv"])

    col1, col2, col3, col4 = st.columns(4)
    if premium_col:
        premiums = pd.to_numeric(df[premium_col], errors="coerce")
        col1.metric("Average premium", signed_currency(premiums.mean()))
        col2.metric("Highest premium", signed_currency(premiums.max()))
    else:
        col1.metric("Average premium", "n/a")
        col2.metric("Highest premium", "n/a")
    if strike_col:
        strikes = pd.to_numeric(df[strike_col], errors="coerce")
        col3.metric("Average strike", f"{strikes.mean():,.2f}")
    else:
        col3.metric("Average strike", "n/a")
    if iv_col:
        ivs = pd.to_numeric(df[iv_col], errors="coerce")
        col4.metric("Average IV", percent_text(ivs.mean()))
    else:
        col4.metric("Average IV", "n/a")

    if scenario_col and premium_col:
        st.caption("Estimated call premium by scenario.")
        chart_df = df[[scenario_col, premium_col]].copy()
        compact_horizontal_bar_chart(chart_df, scenario_col, premium_col, height=250)

    display_cols = [col for col in [scenario_col, premium_col, strike_col, delta_col, iv_col] if col]
    if display_cols:
        st.markdown("**Key premium fields**")
        st.dataframe(df[display_cols], width="stretch", hide_index=True)

    with st.expander("Raw option premium table", expanded=False):
        st.dataframe(df, width="stretch")


def show_premium_payoffs() -> None:
    st.subheader("Premium-aware payoffs")
    df = load_csv(PREMIUM_AWARE_PAYOFF_PATH)
    if df is None or df.empty:
        st.info("No premium_aware_payoff_scaffold.csv found. Run run_paid_simulator_premium_aware_payoff_check.py first.")
        return

    scenario_col = find_column(df, ["scenario_display_name", "display_name", "scenario_name", "scenario"])
    rel_col = find_column(df, ["covered_call_minus_buy_hold", "covered_call_minus_buy_and_hold", "relative_result", "premium_aware_relative_result"])
    premium_col = find_column(df, ["premium_income", "estimated_call_premium", "call_premium"])
    intrinsic_col = find_column(df, ["call_intrinsic_loss", "intrinsic_call_loss", "intrinsic_loss"])
    assigned_col = find_column(df, ["assignment_flag", "assigned", "is_assigned"])

    if rel_col:
        values = pd.to_numeric(df[rel_col], errors="coerce")
        col1, col2, col3 = st.columns(3)
        col1.metric("Best relative result", signed_currency(values.max()))
        col2.metric("Worst relative result", signed_currency(values.min()))
        col3.metric("Average relative result", signed_currency(values.mean()))

    if scenario_col and rel_col:
        st.caption("Premium-aware covered-call result relative to buy-and-hold. Higher is better.")
        chart_df = df[[scenario_col, rel_col]].copy()
        compact_horizontal_bar_chart(chart_df, scenario_col, rel_col, height=280)

    display_cols = [col for col in [scenario_col, rel_col, premium_col, intrinsic_col, assigned_col] if col]
    if display_cols:
        st.markdown("**Key payoff fields**")
        st.dataframe(df[display_cols], width="stretch", hide_index=True)

    with st.expander("Raw premium-aware payoff table", expanded=False):
        st.dataframe(df, width="stretch")

    if PREMIUM_AWARE_REPORT_PATH.exists():
        if st.button("Open premium-aware payoff HTML report"):
            if not open_path_with_windows(PREMIUM_AWARE_REPORT_PATH):
                st.warning(f"Could not open report directly: {PREMIUM_AWARE_REPORT_PATH}")


def show_comparison() -> None:
    st.subheader("Premium-aware vs older Phase 2 scaffold")
    df = load_csv(PREMIUM_VS_SCAFFOLD_PATH)
    if df is None or df.empty:
        st.info("No premium_vs_scaffold_comparison.csv found. Run run_paid_simulator_premium_vs_scaffold_check.py first.")
        return

    scenario_col = find_column(df, ["scenario_display_name", "display_name", "scenario_name", "scenario"])
    diff_col = find_column(df, ["premium_aware_minus_old", "premium_minus_scaffold", "difference", "difference_p_l"])
    premium_rel_col = find_column(df, ["premium_aware_relative_result", "premium_relative_result", "premium_aware"])
    old_rel_col = find_column(df, ["old_phase2_relative_result", "old_relative_result", "scaffold_relative_result"])

    if diff_col:
        values = pd.to_numeric(df[diff_col], errors="coerce")
        col1, col2, col3 = st.columns(3)
        col1.metric("Largest premium-aware improvement", signed_currency(values.max()))
        col2.metric("Largest premium-aware reduction", signed_currency(values.min()))
        col3.metric("Average change", signed_currency(values.mean()))

    if scenario_col and diff_col:
        st.caption("Premium-aware result minus older Phase 2 scaffold. Positive means the premium-aware model improves the relative result.")
        chart_df = df[[scenario_col, diff_col]].copy()
        compact_horizontal_bar_chart(chart_df, scenario_col, diff_col, height=280)

    display_cols = [col for col in [scenario_col, old_rel_col, premium_rel_col, diff_col] if col]
    if display_cols:
        st.markdown("**Comparison table**")
        st.dataframe(df[display_cols], width="stretch", hide_index=True)

    with st.expander("Raw premium-vs-scaffold table", expanded=False):
        st.dataframe(df, width="stretch")

    if PREMIUM_VS_SCAFFOLD_REPORT_PATH.exists():
        if st.button("Open premium-vs-scaffold HTML report"):
            if not open_path_with_windows(PREMIUM_VS_SCAFFOLD_REPORT_PATH):
                st.warning(f"Could not open report directly: {PREMIUM_VS_SCAFFOLD_REPORT_PATH}")


def main() -> None:
    st.title("Phase 2B Premium Model Viewer")
    st.caption(f"Project root: {PROJECT_ROOT}")
    st.info("Development viewer only. This does not replace the v0.1 customer dashboard.")

    overview_tab, premium_tab, payoff_tab, comparison_tab = st.tabs(
        ["Overview", "Option premiums", "Premium-aware payoffs", "Premium vs scaffold"]
    )

    with overview_tab:
        show_overview()
    with premium_tab:
        show_option_premiums()
    with payoff_tab:
        show_premium_payoffs()
    with comparison_tab:
        show_comparison()


if __name__ == "__main__":
    main()
