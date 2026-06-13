"""
phase2c_premium_validation_viewer.py

Standalone Streamlit viewer for the Phase 2C premium-model validation layer.

This viewer is intentionally separate from the main paid simulator dashboard.
It reads the validation outputs created by:

    app/run_paid_simulator_premium_model_validation_check.py

and presents the results in a compact browser view.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

try:
    import altair as alt
except Exception:  # pragma: no cover
    alt = None


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parents[1]
PROJECT_ROOT = CURRENT_FILE.parents[2]

TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

VALIDATION_CSV = TABLE_DIR / "premium_model_validation_scaffold.csv"
VALIDATION_HTML = REPORT_DIR / "premium_model_validation_scaffold.html"
VALIDATION_SUMMARY = REPORT_DIR / "premium_model_validation_summary.txt"
OPTION_PREMIUM_CSV = TABLE_DIR / "option_premium_scaffold.csv"
PREMIUM_AWARE_PAYOFF_CSV = TABLE_DIR / "premium_aware_payoff_scaffold.csv"
PREMIUM_VS_SCAFFOLD_CSV = TABLE_DIR / "premium_vs_scaffold_comparison.csv"


STATUS_ORDER = {
    "PASS": 0,
    "WATCH": 1,
    "REVIEW": 2,
    "FAIL": 3,
    "ERROR": 4,
}


def normalize_column_name(name: str) -> str:
    return "".join(ch.lower() for ch in str(name) if ch.isalnum())


def find_column(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    normalized = {normalize_column_name(col): col for col in df.columns}
    for candidate in candidates:
        key = normalize_column_name(candidate)
        if key in normalized:
            return normalized[key]
    return None


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def status_rank(value: object) -> int:
    return STATUS_ORDER.get(str(value).upper().strip(), 99)


def overall_status(df: pd.DataFrame) -> str:
    if df.empty:
        return "MISSING"

    status_col = find_column(df, ["status", "validation_status", "result", "check_status"])
    if status_col is None:
        return "UNKNOWN"

    statuses = [str(value).upper().strip() for value in df[status_col].dropna().tolist()]
    if not statuses:
        return "UNKNOWN"

    worst = max(statuses, key=status_rank)
    if worst == "PASS":
        return "PASS"
    return worst


def count_statuses(df: pd.DataFrame) -> dict[str, int]:
    status_col = find_column(df, ["status", "validation_status", "result", "check_status"])
    if df.empty or status_col is None:
        return {}
    counts: dict[str, int] = {}
    for value in df[status_col].fillna("UNKNOWN"):
        label = str(value).upper().strip() or "UNKNOWN"
        counts[label] = counts.get(label, 0) + 1
    return counts


def currency(value: object) -> str:
    try:
        return f"${float(value):,.2f}"
    except Exception:
        return "n/a"


def percentage(value: object) -> str:
    try:
        return f"{float(value):.2f}%"
    except Exception:
        return "n/a"


def display_file_status() -> None:
    rows = []
    for label, path in [
        ("Validation CSV", VALIDATION_CSV),
        ("Validation HTML", VALIDATION_HTML),
        ("Validation summary", VALIDATION_SUMMARY),
        ("Option premium CSV", OPTION_PREMIUM_CSV),
        ("Premium-aware payoff CSV", PREMIUM_AWARE_PAYOFF_CSV),
        ("Premium vs scaffold CSV", PREMIUM_VS_SCAFFOLD_CSV),
    ]:
        rows.append(
            {
                "Item": label,
                "Status": "FOUND" if path.exists() else "MISSING",
                "Path": str(path.relative_to(PROJECT_ROOT)) if path.exists() else str(path),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def show_status_chart(status_counts: dict[str, int]) -> None:
    if not status_counts:
        st.info("No status counts are available yet.")
        return

    chart_df = pd.DataFrame(
        [{"Status": key, "Count": value} for key, value in sorted(status_counts.items())]
    )

    if alt is None:
        st.bar_chart(chart_df.set_index("Status"))
        return

    chart = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            x=alt.X("Status:N", title="Validation status"),
            y=alt.Y("Count:Q", title="Number of checks"),
            tooltip=["Status:N", "Count:Q"],
        )
        .properties(height=280)
    )
    st.altair_chart(chart, use_container_width=True)


def show_overview(validation_df: pd.DataFrame) -> None:
    st.subheader("Phase 2C premium-model validation overview")

    status = overall_status(validation_df)
    counts = count_statuses(validation_df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Overall status", status)
    col2.metric("Validation rows", len(validation_df))
    col3.metric("PASS", counts.get("PASS", 0))
    col4.metric("WATCH/REVIEW", counts.get("WATCH", 0) + counts.get("REVIEW", 0))

    if status == "PASS":
        st.success("The premium-model validation layer is currently passing.")
    elif status in {"WATCH", "REVIEW"}:
        st.warning("The validation layer is installed, but at least one modeling assumption needs review.")
    elif status == "MISSING":
        st.error("The validation CSV is missing. Run app\\run_paid_simulator_premium_model_validation_check.py first.")
    else:
        st.warning("The validation status could not be classified cleanly.")

    st.markdown(
        "This viewer does not change the pricing model. It only displays the validation outputs "
        "so that premium assumptions can be inspected before they are promoted into the customer workflow."
    )

    show_status_chart(counts)

    with st.expander("File status", expanded=False):
        display_file_status()



def show_validation_table(validation_df: pd.DataFrame) -> None:
    st.subheader("Validation checks")

    if validation_df.empty:
        st.error("No validation table found. Run the Phase 2C validation check first.")
        return

    status_col = find_column(validation_df, ["status", "validation_status", "result", "check_status"])
    if status_col:
        selected_statuses = st.multiselect(
            "Filter by status",
            sorted(validation_df[status_col].dropna().astype(str).unique().tolist()),
            default=sorted(validation_df[status_col].dropna().astype(str).unique().tolist()),
        )
        if selected_statuses:
            display_df = validation_df[validation_df[status_col].astype(str).isin(selected_statuses)].copy()
        else:
            display_df = validation_df.copy()
    else:
        display_df = validation_df.copy()

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    if VALIDATION_SUMMARY.exists():
        with st.expander("Validation summary text", expanded=True):
            try:
                st.text(VALIDATION_SUMMARY.read_text(encoding="utf-8"))
            except UnicodeDecodeError:
                st.text(VALIDATION_SUMMARY.read_text(errors="ignore"))

    if VALIDATION_HTML.exists():
        st.link_button("Open validation HTML report", VALIDATION_HTML.as_uri())



def show_option_premiums(option_df: pd.DataFrame) -> None:
    st.subheader("Option-premium assumptions")

    if option_df.empty:
        st.error("No option-premium scaffold CSV found.")
        return

    scenario_col = find_column(option_df, ["scenario", "scenario_name", "display_name", "scenario_display_name"])
    premium_col = find_column(option_df, ["estimated_call_premium", "call_premium", "premium"])
    strike_col = find_column(option_df, ["estimated_call_strike", "call_strike", "strike"])
    iv_col = find_column(option_df, ["estimated_iv", "implied_volatility", "iv"])
    delta_col = find_column(option_df, ["estimated_call_delta", "call_delta", "delta"])

    col1, col2, col3 = st.columns(3)
    if premium_col:
        col1.metric("Average premium", currency(option_df[premium_col].mean()))
    if iv_col:
        col2.metric("Average IV", percentage(option_df[iv_col].mean() * 100 if option_df[iv_col].max() <= 2 else option_df[iv_col].mean()))
    if delta_col:
        col3.metric("Average delta", f"{option_df[delta_col].mean():.3f}")

    if alt is not None and scenario_col and premium_col:
        chart_data = option_df[[scenario_col, premium_col]].copy()
        chart_data.columns = ["Scenario", "Estimated premium"]
        chart = (
            alt.Chart(chart_data)
            .mark_bar()
            .encode(
                x=alt.X("Scenario:N", title="Scenario", sort=None),
                y=alt.Y("Estimated premium:Q", title="Estimated call premium"),
                tooltip=["Scenario:N", "Estimated premium:Q"],
            )
            .properties(height=300)
        )
        st.altair_chart(chart, use_container_width=True)

    shown_cols = [col for col in [scenario_col, premium_col, strike_col, iv_col, delta_col] if col]
    if shown_cols:
        st.dataframe(option_df[shown_cols], use_container_width=True, hide_index=True)
    else:
        st.dataframe(option_df, use_container_width=True, hide_index=True)



def show_premium_aware_payoffs(payoff_df: pd.DataFrame) -> None:
    st.subheader("Premium-aware payoff output")

    if payoff_df.empty:
        st.error("No premium-aware payoff scaffold CSV found.")
        return

    scenario_col = find_column(payoff_df, ["scenario", "scenario_name", "display_name", "scenario_display_name"])
    relative_col = find_column(
        payoff_df,
        [
            "covered_call_minus_buy_hold",
            "covered_call_minus_buy_and_hold",
            "relative_result",
            "premium_aware_relative_result",
        ],
    )

    if relative_col:
        avg_value = payoff_df[relative_col].mean()
        best_value = payoff_df[relative_col].max()
        worst_value = payoff_df[relative_col].min()

        col1, col2, col3 = st.columns(3)
        col1.metric("Average relative result", currency(avg_value))
        col2.metric("Best relative result", currency(best_value))
        col3.metric("Worst relative result", currency(worst_value))

    if alt is not None and scenario_col and relative_col:
        chart_data = payoff_df[[scenario_col, relative_col]].copy()
        chart_data.columns = ["Scenario", "Relative result"]
        chart = (
            alt.Chart(chart_data)
            .mark_bar()
            .encode(
                x=alt.X("Scenario:N", title="Scenario", sort=None),
                y=alt.Y("Relative result:Q", title="Covered call minus buy-and-hold"),
                tooltip=["Scenario:N", "Relative result:Q"],
            )
            .properties(height=300)
        )
        st.altair_chart(chart, use_container_width=True)

    st.dataframe(payoff_df, use_container_width=True, hide_index=True)



def show_notes() -> None:
    st.subheader("How to use this viewer")

    st.markdown(
        """
This viewer is a Phase 2C diagnostic screen. It is intended for developer review, not for customer-facing trade guidance yet.

Recommended workflow:

1. Run the Phase 2B pipeline check.
2. Run the Phase 2C premium-model validation check.
3. Open this viewer.
4. Inspect any WATCH or REVIEW rows.
5. Tune the premium-model assumptions only after the validation report shows where the model is weak.

Important interpretation:

- PASS means the row is internally reasonable under the current simple assumptions.
- WATCH means the result is acceptable for a scaffold but worth monitoring.
- REVIEW means the assumption may be too aggressive, too conservative, or inconsistent.
- A passing installation check does not mean the model is market-calibrated.
"""
    )



def main() -> None:
    st.set_page_config(
        page_title="Phase 2C Premium Validation Viewer",
        layout="wide",
    )

    st.title("Phase 2C Premium Validation Viewer")
    st.caption("Covered Call Strategy Stress Test - developer diagnostic view")

    validation_df = load_csv(VALIDATION_CSV)
    option_df = load_csv(OPTION_PREMIUM_CSV)
    payoff_df = load_csv(PREMIUM_AWARE_PAYOFF_CSV)

    tabs = st.tabs(
        [
            "Overview",
            "Validation checks",
            "Option premiums",
            "Premium-aware payoffs",
            "Notes",
        ]
    )

    with tabs[0]:
        show_overview(validation_df)
    with tabs[1]:
        show_validation_table(validation_df)
    with tabs[2]:
        show_option_premiums(option_df)
    with tabs[3]:
        show_premium_aware_payoffs(payoff_df)
    with tabs[4]:
        show_notes()


if __name__ == "__main__":
    main()
