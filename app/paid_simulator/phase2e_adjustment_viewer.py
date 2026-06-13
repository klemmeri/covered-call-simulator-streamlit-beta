"""
phase2e_adjustment_viewer.py

Standalone Streamlit viewer for Phase 2E controlled premium-model adjustment results.

This viewer is intentionally separate from the main paid simulator dashboard. It reads
existing Phase 2E CSV and text outputs and displays them in a browser for inspection.
"""

from pathlib import Path
import subprocess
import sys

import pandas as pd
import streamlit as st


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

ADJUSTED_PREMIUMS_CSV = TABLE_DIR / "premium_model_adjusted_premiums.csv"
ADJUSTED_PREMIUM_COMPARISON_HTML = REPORT_DIR / "premium_model_adjustment_comparison.html"
ADJUSTED_PREMIUM_SUMMARY_TXT = REPORT_DIR / "premium_model_adjustment_summary.txt"

ADJUSTED_PAYOFF_CSV = TABLE_DIR / "adjusted_premium_payoff_comparison.csv"
ADJUSTED_PAYOFF_HTML = REPORT_DIR / "adjusted_premium_payoff_comparison.html"
ADJUSTED_PAYOFF_SUMMARY_TXT = REPORT_DIR / "adjusted_premium_payoff_summary.txt"

ORIGINAL_PREMIUM_CSV = TABLE_DIR / "option_premium_scaffold.csv"
PREMIUM_AWARE_PAYOFF_CSV = TABLE_DIR / "premium_aware_payoff_scaffold.csv"
TUNING_RECOMMENDATIONS_CSV = TABLE_DIR / "premium_model_tuning_recommendations.csv"
VALIDATION_CSV = TABLE_DIR / "premium_model_validation_scaffold.csv"


st.set_page_config(
    page_title="Phase 2E Premium Adjustment Viewer",
    layout="wide",
)


st.markdown(
    """
    <style>
    .block-container {max-width: 1220px; padding-top: 1.25rem;}
    .small-note {font-size: 0.90rem; color: #666;}
    </style>
    """,
    unsafe_allow_html=True,
)


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception as exc:  # pragma: no cover - display helper
        st.error(f"Could not read {path}: {exc}")
        return pd.DataFrame()


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:  # pragma: no cover - display helper
        return f"Could not read {path}: {exc}"


def file_status_rows() -> list[dict[str, object]]:
    files = [
        ("Adjusted premiums CSV", ADJUSTED_PREMIUMS_CSV),
        ("Adjusted premium comparison HTML", ADJUSTED_PREMIUM_COMPARISON_HTML),
        ("Adjusted premium summary", ADJUSTED_PREMIUM_SUMMARY_TXT),
        ("Adjusted payoff comparison CSV", ADJUSTED_PAYOFF_CSV),
        ("Adjusted payoff comparison HTML", ADJUSTED_PAYOFF_HTML),
        ("Adjusted payoff summary", ADJUSTED_PAYOFF_SUMMARY_TXT),
        ("Original premium CSV", ORIGINAL_PREMIUM_CSV),
        ("Premium-aware payoff CSV", PREMIUM_AWARE_PAYOFF_CSV),
        ("Tuning recommendations CSV", TUNING_RECOMMENDATIONS_CSV),
        ("Validation CSV", VALIDATION_CSV),
    ]

    rows: list[dict[str, object]] = []
    for label, path in files:
        rows.append(
            {
                "item": label,
                "status": "FOUND" if path.exists() else "MISSING",
                "path": str(path),
            }
        )
    return rows


def open_file(path: Path) -> None:
    if not path.exists():
        st.warning(f"File not found: {path}")
        return
    try:
        if sys.platform.startswith("win"):
            import os
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception as exc:  # pragma: no cover - local OS helper
        st.error(f"Could not open file: {exc}")


def numeric_columns(df: pd.DataFrame) -> list[str]:
    return [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]


def scenario_column(df: pd.DataFrame) -> str | None:
    candidates = [
        "scenario",
        "scenario_name",
        "display_name",
        "market_path",
        "path_name",
    ]
    lowered = {str(col).lower(): col for col in df.columns}
    for candidate in candidates:
        if candidate in lowered:
            return str(lowered[candidate])
    return str(df.columns[0]) if len(df.columns) > 0 else None


def show_dataframe_section(title: str, path: Path, description: str = "") -> pd.DataFrame:
    st.subheader(title)
    if description:
        st.caption(description)
    df = read_csv(path)
    if df.empty:
        st.warning(f"No data available. Expected file: {path}")
    else:
        st.dataframe(df, use_container_width=True)
    return df


def show_summary_text(path: Path, title: str) -> None:
    st.subheader(title)
    text = read_text(path)
    if text:
        st.text(text)
    else:
        st.warning(f"Summary file not found: {path}")


def show_key_metrics(adjusted_premiums: pd.DataFrame, adjusted_payoff: pd.DataFrame) -> None:
    col1, col2, col3, col4 = st.columns(4)

    scenario_count = max(len(adjusted_premiums), len(adjusted_payoff))
    col1.metric("Scenarios", f"{scenario_count}")

    premium_cols = [
        col
        for col in adjusted_premiums.columns
        if "premium" in str(col).lower() and pd.api.types.is_numeric_dtype(adjusted_premiums[col])
    ]
    if premium_cols:
        col = premium_cols[-1]
        col2.metric("Avg adjusted premium", f"{adjusted_premiums[col].mean():.2f}")
    else:
        col2.metric("Avg adjusted premium", "n/a")

    diff_cols = [
        col
        for col in adjusted_payoff.columns
        if "adjusted_minus" in str(col).lower() and pd.api.types.is_numeric_dtype(adjusted_payoff[col])
    ]
    if diff_cols:
        col = diff_cols[-1]
        col3.metric("Avg adjusted difference", f"{adjusted_payoff[col].mean():,.2f}")
    else:
        col3.metric("Avg adjusted difference", "n/a")

    status_cols = [col for col in adjusted_payoff.columns if "interpret" in str(col).lower() or "status" in str(col).lower()]
    if status_cols and not adjusted_payoff.empty:
        col = status_cols[-1]
        unique_count = adjusted_payoff[col].nunique(dropna=True)
        col4.metric("Interpretation groups", f"{unique_count}")
    else:
        col4.metric("Interpretation groups", "n/a")


def show_simple_chart(df: pd.DataFrame, preferred_terms: list[str], title: str) -> None:
    if df.empty:
        return

    scen_col = scenario_column(df)
    if scen_col is None:
        return

    num_cols = numeric_columns(df)
    if not num_cols:
        return

    chosen = None
    for term in preferred_terms:
        for col in num_cols:
            if term.lower() in str(col).lower():
                chosen = col
                break
        if chosen is not None:
            break

    if chosen is None:
        chosen = num_cols[-1]

    chart_df = df[[scen_col, chosen]].copy()
    chart_df = chart_df.dropna()
    if chart_df.empty:
        return

    st.markdown(f"**{title}**")
    try:
        st.bar_chart(chart_df.set_index(scen_col)[chosen])
    except Exception:
        st.caption("Chart could not be rendered for the selected columns.")


def main() -> None:
    st.title("Phase 2E premium adjustment viewer")
    st.caption(
        "Standalone developer viewer for controlled premium-model adjustment outputs. "
        "This viewer does not change the main customer dashboard."
    )

    adjusted_premiums = read_csv(ADJUSTED_PREMIUMS_CSV)
    adjusted_payoff = read_csv(ADJUSTED_PAYOFF_CSV)

    tabs = st.tabs(
        [
            "Overview",
            "Adjusted premiums",
            "Adjusted payoff comparison",
            "Original context",
            "Files and reports",
            "Notes",
        ]
    )

    with tabs[0]:
        st.header("Overview")
        show_key_metrics(adjusted_premiums, adjusted_payoff)
        st.divider()
        show_summary_text(ADJUSTED_PREMIUM_SUMMARY_TXT, "Premium-adjustment summary")
        show_summary_text(ADJUSTED_PAYOFF_SUMMARY_TXT, "Adjusted-payoff summary")

    with tabs[1]:
        df = show_dataframe_section(
            "Adjusted premium estimates",
            ADJUSTED_PREMIUMS_CSV,
            "Separate adjusted-premium output. Original premium estimates are preserved.",
        )
        show_simple_chart(df, ["adjusted", "premium"], "Adjusted premiums by scenario")
        if st.button("Open adjusted premium HTML report"):
            open_file(ADJUSTED_PREMIUM_COMPARISON_HTML)

    with tabs[2]:
        df = show_dataframe_section(
            "Adjusted payoff comparison",
            ADJUSTED_PAYOFF_CSV,
            "Compares adjusted-premium payoff results against the prior premium-aware payoff layer.",
        )
        show_simple_chart(df, ["adjusted_minus", "covered_call_minus", "difference"], "Adjusted payoff difference by scenario")
        if st.button("Open adjusted payoff HTML report"):
            open_file(ADJUSTED_PAYOFF_HTML)

    with tabs[3]:
        st.header("Original premium-model context")
        left, right = st.columns(2)
        with left:
            show_dataframe_section("Original option premium scaffold", ORIGINAL_PREMIUM_CSV)
        with right:
            show_dataframe_section("Prior premium-aware payoff scaffold", PREMIUM_AWARE_PAYOFF_CSV)
        st.divider()
        left, right = st.columns(2)
        with left:
            show_dataframe_section("Phase 2D tuning recommendations", TUNING_RECOMMENDATIONS_CSV)
        with right:
            show_dataframe_section("Phase 2C validation checks", VALIDATION_CSV)

    with tabs[4]:
        st.header("Files and reports")
        status_df = pd.DataFrame(file_status_rows())
        st.dataframe(status_df, use_container_width=True)
        st.caption(f"Project root: {PROJECT_ROOT}")

    with tabs[5]:
        st.header("Notes")
        st.markdown(
            """
            The Phase 2E adjustment layer is intentionally conservative.

            - It does not overwrite the original premium model.
            - It writes separate adjusted-premium outputs.
            - It allows us to inspect whether tuning materially changes scenario results.
            - It remains a developer-side modeling layer until validated.

            The next project step is a Phase 2E pipeline check, followed by a Developer-view-only
            dashboard tab if the pipeline passes.
            """
        )


if __name__ == "__main__":
    main()
