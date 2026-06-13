"""
phase2f_model_decision_viewer.py

Standalone Streamlit viewer for Phase 2F model-decision summary results.

This viewer is intentionally separate from the main paid simulator dashboard. It reads
existing Phase 2F model-decision outputs and related Phase 2B/2C/2D/2E context files,
then displays them in a browser for developer review.
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

MODEL_DECISION_CSV = TABLE_DIR / "model_decision_summary.csv"
MODEL_DECISION_HTML = REPORT_DIR / "model_decision_summary.html"
MODEL_DECISION_TXT = REPORT_DIR / "model_decision_summary.txt"
MODEL_DECISION_CHECK_REPORT = REPORT_DIR / "phase2f_model_decision_summary_check_report.txt"

OPTION_PREMIUM_CSV = TABLE_DIR / "option_premium_scaffold.csv"
PREMIUM_AWARE_PAYOFF_CSV = TABLE_DIR / "premium_aware_payoff_scaffold.csv"
PREMIUM_VALIDATION_CSV = TABLE_DIR / "premium_model_validation_scaffold.csv"
PREMIUM_TUNING_CSV = TABLE_DIR / "premium_model_tuning_recommendations.csv"
ADJUSTED_PREMIUM_CSV = TABLE_DIR / "premium_model_adjusted_premiums.csv"
ADJUSTED_PAYOFF_CSV = TABLE_DIR / "adjusted_premium_payoff_comparison.csv"


st.set_page_config(
    page_title="Phase 2F Model Decision Viewer",
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


def file_status_rows() -> list[dict[str, object]]:
    files = [
        ("Model decision CSV", MODEL_DECISION_CSV),
        ("Model decision HTML", MODEL_DECISION_HTML),
        ("Model decision text summary", MODEL_DECISION_TXT),
        ("Model decision check report", MODEL_DECISION_CHECK_REPORT),
        ("Option premium CSV", OPTION_PREMIUM_CSV),
        ("Premium-aware payoff CSV", PREMIUM_AWARE_PAYOFF_CSV),
        ("Premium validation CSV", PREMIUM_VALIDATION_CSV),
        ("Premium tuning CSV", PREMIUM_TUNING_CSV),
        ("Adjusted premium CSV", ADJUSTED_PREMIUM_CSV),
        ("Adjusted payoff CSV", ADJUSTED_PAYOFF_CSV),
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


def find_column(df: pd.DataFrame, terms: list[str]) -> str | None:
    if df.empty:
        return None
    normalized = {"".join(ch.lower() for ch in str(col) if ch.isalnum()): col for col in df.columns}
    for term in terms:
        key = "".join(ch.lower() for ch in term if ch.isalnum())
        for norm_col, original_col in normalized.items():
            if key in norm_col or norm_col in key:
                return str(original_col)
    return None


def show_key_metrics(decision_df: pd.DataFrame) -> None:
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Scenarios", f"{len(decision_df)}")

    decision_col = find_column(decision_df, ["model_decision", "decision"])
    if decision_col and not decision_df.empty:
        candidate_count = decision_df[decision_df[decision_col].astype(str).str.contains("CANDIDATE", case=False, na=False)].shape[0]
        review_count = decision_df[decision_df[decision_col].astype(str).str.contains("REVIEW|DO NOT", case=False, na=False, regex=True)].shape[0]
        col2.metric("Promotion candidates", f"{candidate_count}")
        col3.metric("Needs review", f"{review_count}")
    else:
        col2.metric("Promotion candidates", "n/a")
        col3.metric("Needs review", "n/a")

    diff_col = find_column(decision_df, ["adjusted_minus_original", "adjusted difference", "premium_change"])
    if diff_col and pd.api.types.is_numeric_dtype(decision_df[diff_col]):
        col4.metric("Avg adjusted change", f"{decision_df[diff_col].mean():,.2f}")
    else:
        col4.metric("Avg adjusted change", "n/a")


def show_decision_counts(decision_df: pd.DataFrame) -> None:
    if decision_df.empty:
        return

    decision_col = find_column(decision_df, ["model_decision", "decision"])
    if decision_col is None:
        return

    counts = decision_df[decision_col].astype(str).value_counts().reset_index()
    counts.columns = ["model_decision", "count"]
    st.subheader("Decision counts")
    st.dataframe(counts, use_container_width=True)
    try:
        st.bar_chart(counts.set_index("model_decision")["count"])
    except Exception:
        st.caption("Decision-count chart could not be rendered.")


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

    chart_df = df[[scen_col, chosen]].copy().dropna()
    if chart_df.empty:
        return

    st.markdown(f"**{title}**")
    try:
        st.bar_chart(chart_df.set_index(scen_col)[chosen])
    except Exception:
        st.caption("Chart could not be rendered for the selected columns.")


def show_promotion_candidates(decision_df: pd.DataFrame) -> None:
    st.subheader("Promotion candidates and review items")
    if decision_df.empty:
        st.warning(f"No model-decision summary data found: {MODEL_DECISION_CSV}")
        return

    decision_col = find_column(decision_df, ["model_decision", "decision"])
    if decision_col is None:
        st.dataframe(decision_df, use_container_width=True)
        return

    candidates = decision_df[decision_df[decision_col].astype(str).str.contains("CANDIDATE", case=False, na=False)]
    review = decision_df[~decision_df.index.isin(candidates.index)]

    st.markdown("**Candidate rows**")
    if candidates.empty:
        st.info("No scenarios are currently marked as candidates for controlled promotion.")
    else:
        st.dataframe(candidates, use_container_width=True)

    st.markdown("**Research / review rows**")
    if review.empty:
        st.info("No review rows detected.")
    else:
        st.dataframe(review, use_container_width=True)


def main() -> None:
    st.title("Phase 2F model-decision viewer")
    st.caption(
        "Standalone developer viewer for model-promotion evidence. "
        "This viewer does not change the main customer dashboard or promote any model automatically."
    )

    decision_df = read_csv(MODEL_DECISION_CSV)

    tabs = st.tabs(
        [
            "Overview",
            "Model decisions",
            "Promotion candidates",
            "Evidence context",
            "Files and reports",
            "Notes",
        ]
    )

    with tabs[0]:
        st.header("Overview")
        show_key_metrics(decision_df)
        st.divider()
        show_summary_text(MODEL_DECISION_TXT, "Model-decision text summary")
        show_decision_counts(decision_df)

    with tabs[1]:
        df = show_dataframe_section(
            "Model decision summary",
            MODEL_DECISION_CSV,
            "Consolidated scenario-level decision report from Phase 2B through Phase 2E evidence.",
        )
        show_simple_chart(df, ["adjusted_minus_original", "adjusted_relative_result", "premium_change"], "Model-decision numeric comparison")
        if st.button("Open model-decision HTML report"):
            open_file(MODEL_DECISION_HTML)

    with tabs[2]:
        show_promotion_candidates(decision_df)

    with tabs[3]:
        st.header("Evidence context")
        left, right = st.columns(2)
        with left:
            show_dataframe_section("Original premium estimates", OPTION_PREMIUM_CSV)
            show_dataframe_section("Premium validation checks", PREMIUM_VALIDATION_CSV)
            show_dataframe_section("Adjusted premium estimates", ADJUSTED_PREMIUM_CSV)
        with right:
            show_dataframe_section("Premium-aware payoff", PREMIUM_AWARE_PAYOFF_CSV)
            show_dataframe_section("Tuning recommendations", PREMIUM_TUNING_CSV)
            show_dataframe_section("Adjusted payoff comparison", ADJUSTED_PAYOFF_CSV)

    with tabs[4]:
        st.header("Files and reports")
        status_df = pd.DataFrame(file_status_rows())
        st.dataframe(status_df, use_container_width=True)
        st.caption(f"Project root: {PROJECT_ROOT}")
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Open model-decision HTML"):
                open_file(MODEL_DECISION_HTML)
        with col2:
            if st.button("Open model-decision text summary"):
                open_file(MODEL_DECISION_TXT)
        with col3:
            if st.button("Open Phase 2F check report"):
                open_file(MODEL_DECISION_CHECK_REPORT)

    with tabs[5]:
        st.header("Notes")
        st.markdown(
            """
            The Phase 2F model-decision layer is an internal developer checkpoint.

            - It does not replace the current customer-facing model.
            - It does not automatically promote the adjusted premium model.
            - It consolidates validation, tuning, and adjusted-payoff evidence.
            - Decision labels are model-development labels, not customer-facing trade recommendations.

            The next project step is a Phase 2F model-decision pipeline check, followed by a
            Developer-view-only dashboard tab if the viewer and pipeline pass.
            """
        )


if __name__ == "__main__":
    main()
