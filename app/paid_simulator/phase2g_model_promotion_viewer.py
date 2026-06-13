"""
phase2g_model_promotion_viewer.py

Standalone Streamlit viewer for the Phase 2G controlled model-promotion
planning layer of the Covered Call Strategy Stress Test project.

This viewer is intentionally separate from the main customer dashboard. It is
for internal developer review only. It reads existing Phase 2G outputs and
context files; it does not promote any model automatically.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]
APP_DIR = PROJECT_ROOT / "app"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CONFIG_DIR = PROJECT_ROOT / "config"

PROMOTION_PLAN_CSV = TABLE_DIR / "model_promotion_plan.csv"
PROMOTION_PLAN_HTML = REPORT_DIR / "model_promotion_plan.html"
PROMOTION_PLAN_TEXT = REPORT_DIR / "model_promotion_plan.txt"
PROMOTION_PLAN_CHECK_REPORT = REPORT_DIR / "phase2g_model_promotion_planning_check_report.txt"
MODEL_DECISION_CSV = TABLE_DIR / "model_decision_summary.csv"
MODEL_DECISION_HTML = REPORT_DIR / "model_decision_summary.html"
MODEL_DECISION_TEXT = REPORT_DIR / "model_decision_summary.txt"
ADJUSTED_PAYOFF_CSV = TABLE_DIR / "adjusted_premium_payoff_comparison.csv"
TUNING_CSV = TABLE_DIR / "premium_model_tuning_recommendations.csv"
VALIDATION_CSV = TABLE_DIR / "premium_model_validation_scaffold.csv"
PREMIUM_CSV = TABLE_DIR / "option_premium_scaffold.csv"

PHASE2G_PLANNING_CHECK = APP_DIR / "run_paid_simulator_model_promotion_planning_check.py"


st.set_page_config(
    page_title="Phase 2G Model-Promotion Viewer",
    layout="wide",
)


st.markdown(
    """
    <style>
        .block-container {
            max-width: 1220px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }
        div[data-testid="stMetric"] {
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 0.65rem;
            padding: 0.75rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception as exc:  # pragma: no cover - display only
        st.warning(f"Could not read {path.name}: {exc}")
        return pd.DataFrame()


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(errors="replace")
    except Exception as exc:  # pragma: no cover - display only
        return f"Could not read {path.name}: {exc}"


def open_file(path: Path) -> None:
    if not path.exists():
        st.warning(f"File not found: {path}")
        return
    try:
        if os.name == "nt":
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception as exc:  # pragma: no cover - display only
        st.warning(f"Could not open {path.name}: {exc}")


def run_python_script(script_path: Path) -> tuple[int, str]:
    if not script_path.exists():
        return 1, f"Missing script: {script_path}"
    completed = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    return completed.returncode, output


def find_column(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    normalized = {str(col).strip().lower().replace("_", " "): col for col in df.columns}
    for candidate in candidates:
        key = candidate.strip().lower().replace("_", " ")
        if key in normalized:
            return normalized[key]
    for candidate in candidates:
        key = candidate.strip().lower().replace("_", " ")
        for normalized_key, original in normalized.items():
            if key in normalized_key:
                return original
    return None


def display_file_status() -> None:
    files = [
        ("Model promotion plan CSV", PROMOTION_PLAN_CSV),
        ("Model promotion plan HTML", PROMOTION_PLAN_HTML),
        ("Model promotion plan text", PROMOTION_PLAN_TEXT),
        ("Phase 2G planning check report", PROMOTION_PLAN_CHECK_REPORT),
        ("Model decision summary CSV", MODEL_DECISION_CSV),
        ("Adjusted payoff comparison CSV", ADJUSTED_PAYOFF_CSV),
        ("Premium tuning recommendations CSV", TUNING_CSV),
        ("Premium validation CSV", VALIDATION_CSV),
        ("Option premium CSV", PREMIUM_CSV),
    ]
    rows = []
    for label, path in files:
        rows.append(
            {
                "File": label,
                "Status": "FOUND" if path.exists() else "MISSING",
                "Path": str(path),
            }
        )
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def display_decision_counts(df: pd.DataFrame) -> None:
    if df.empty:
        return
    decision_col = find_column(
        df,
        [
            "promotion_label",
            "promotion decision",
            "promotion_decision",
            "decision_label",
            "model decision",
            "decision",
        ],
    )
    if not decision_col:
        st.info("No promotion-decision column was found in the promotion plan.")
        return
    counts = df[decision_col].fillna("Unclassified").astype(str).value_counts().reset_index()
    counts.columns = ["Decision label", "Count"]
    st.dataframe(counts, width="stretch", hide_index=True)


def display_promotion_candidates(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No model-promotion plan CSV is available yet.")
        return
    decision_col = find_column(
        df,
        [
            "promotion_label",
            "promotion decision",
            "promotion_decision",
            "decision_label",
            "model decision",
            "decision",
        ],
    )
    if not decision_col:
        st.info("No promotion-decision column was found in the promotion plan.")
        st.dataframe(df, width="stretch", hide_index=True)
        return
    mask = df[decision_col].fillna("").astype(str).str.contains("PROMOTION", case=False, na=False)
    candidates = df.loc[mask].copy()
    if candidates.empty:
        st.info("No internal promotion candidates are currently flagged by the Phase 2G plan.")
    else:
        st.dataframe(candidates, width="stretch", hide_index=True)


def main() -> None:
    st.title("Phase 2G model-promotion viewer")
    st.caption(
        "Internal Developer-view tool for reviewing controlled model-promotion planning. "
        "This does not promote any model into the customer dashboard."
    )

    promotion_df = read_csv(PROMOTION_PLAN_CSV)
    decision_df = read_csv(MODEL_DECISION_CSV)
    adjusted_df = read_csv(ADJUSTED_PAYOFF_CSV)
    tuning_df = read_csv(TUNING_CSV)
    validation_df = read_csv(VALIDATION_CSV)
    premium_df = read_csv(PREMIUM_CSV)
    plan_text = read_text(PROMOTION_PLAN_TEXT)

    tabs = st.tabs(
        [
            "Overview",
            "Promotion plan",
            "Promotion candidates",
            "Evidence context",
            "Files and reports",
            "Notes",
        ]
    )

    with tabs[0]:
        st.subheader("Overview")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Plan rows", len(promotion_df))
        c2.metric("Decision rows", len(decision_df))
        c3.metric("Adjusted payoff rows", len(adjusted_df))
        c4.metric("Validation rows", len(validation_df))

        st.markdown(
            """
            Phase 2G is a controlled planning layer. Its job is to decide whether the
            adjusted premium model should remain a research model, be reviewed further,
            or become an internal candidate for later promotion.

            No customer-facing behavior is changed by this viewer.
            """
        )

        if plan_text:
            st.subheader("Text summary")
            st.text(plan_text)
        else:
            st.info("Model-promotion plan text summary has not been generated yet.")

        st.subheader("Decision-count summary")
        display_decision_counts(promotion_df)

    with tabs[1]:
        st.subheader("Model-promotion plan")
        if promotion_df.empty:
            st.info("Run the Phase 2G model-promotion planning check to create the plan CSV.")
        else:
            st.dataframe(promotion_df, width="stretch", hide_index=True)

    with tabs[2]:
        st.subheader("Internal promotion candidates")
        display_promotion_candidates(promotion_df)
        st.caption(
            "These labels are internal model-development classifications, not customer-facing trade guidance."
        )

    with tabs[3]:
        st.subheader("Evidence context")
        with st.expander("Phase 2F model-decision summary", expanded=True):
            if decision_df.empty:
                st.info("No model_decision_summary.csv file was found.")
            else:
                st.dataframe(decision_df, width="stretch", hide_index=True)
        with st.expander("Phase 2E adjusted payoff comparison", expanded=False):
            if adjusted_df.empty:
                st.info("No adjusted_premium_payoff_comparison.csv file was found.")
            else:
                st.dataframe(adjusted_df, width="stretch", hide_index=True)
        with st.expander("Phase 2D tuning recommendations", expanded=False):
            if tuning_df.empty:
                st.info("No premium_model_tuning_recommendations.csv file was found.")
            else:
                st.dataframe(tuning_df, width="stretch", hide_index=True)
        with st.expander("Phase 2C validation checks", expanded=False):
            if validation_df.empty:
                st.info("No premium_model_validation_scaffold.csv file was found.")
            else:
                st.dataframe(validation_df, width="stretch", hide_index=True)
        with st.expander("Phase 2B option premium estimates", expanded=False):
            if premium_df.empty:
                st.info("No option_premium_scaffold.csv file was found.")
            else:
                st.dataframe(premium_df, width="stretch", hide_index=True)

    with tabs[4]:
        st.subheader("Files and reports")
        display_file_status()

        st.divider()
        c1, c2, c3 = st.columns(3)
        if c1.button("Run Phase 2G planning check"):
            code, output = run_python_script(PHASE2G_PLANNING_CHECK)
            st.code(output or "No output returned.")
            if code == 0:
                st.success("Phase 2G planning check completed.")
            else:
                st.warning("Phase 2G planning check returned a nonzero exit code.")
        if c2.button("Open promotion-plan HTML"):
            open_file(PROMOTION_PLAN_HTML)
        if c3.button("Open promotion-plan text"):
            open_file(PROMOTION_PLAN_TEXT)

        st.caption(f"Project root: {PROJECT_ROOT}")

    with tabs[5]:
        st.subheader("Notes")
        st.markdown(
            """
            **Interpretation rules**

            - Phase 2G is internal only.
            - A promotion candidate is not automatically promoted.
            - Promotion should require clean validation, acceptable tuning behavior,
              reasonable adjusted payoff behavior, and stable dashboard integration.
            - Customer-facing promotion should occur only after another controlled
              checkpoint and explicit decision.
            """
        )


if __name__ == "__main__":
    main()
