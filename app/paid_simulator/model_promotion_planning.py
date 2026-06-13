"""
model_promotion_planning.py

Phase 2G controlled model-promotion planning scaffold for the Covered Call
Strategy Stress Test paid simulator.

This module does not replace the active customer-facing model.  It reads the
Phase 2F model-decision summary and creates a controlled promotion plan that
keeps all promoted-model candidates behind developer-only gates until they are
explicitly approved later.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

MODEL_DECISION_CSV = TABLE_DIR / "model_decision_summary.csv"
ADJUSTED_PAYOFF_CSV = TABLE_DIR / "adjusted_premium_payoff_comparison.csv"
TUNING_CSV = TABLE_DIR / "premium_model_tuning_recommendations.csv"
VALIDATION_CSV = TABLE_DIR / "premium_model_validation_scaffold.csv"

PROMOTION_PLAN_CSV = TABLE_DIR / "model_promotion_plan.csv"
PROMOTION_PLAN_HTML = REPORT_DIR / "model_promotion_plan.html"
PROMOTION_PLAN_TEXT = REPORT_DIR / "model_promotion_plan.txt"


@dataclass
class PromotionPlanResult:
    """Container for Phase 2G promotion-planning outputs."""

    plan_df: pd.DataFrame
    csv_path: Path
    html_path: Path
    text_path: Path
    summary_text: str


def normalize_name(value: object) -> str:
    """Normalize a column name or label for tolerant matching."""
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value)).strip("_")


def find_column(df: pd.DataFrame, candidates: Iterable[str]) -> str | None:
    """Find a column using tolerant candidate matching."""
    normalized_map = {normalize_name(col): col for col in df.columns}
    for candidate in candidates:
        key = normalize_name(candidate)
        if key in normalized_map:
            return normalized_map[key]
    return None


def safe_read_csv(path: Path) -> pd.DataFrame:
    """Read a CSV file, returning an empty frame if it is unavailable."""
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def safe_text(value: object, default: str = "") -> str:
    """Convert a value to clean display text."""
    if value is None:
        return default
    try:
        if pd.isna(value):
            return default
    except Exception:
        pass
    text = str(value).strip()
    return text if text else default


def safe_float(value: object, default: float = 0.0) -> float:
    """Convert a value to float when possible."""
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def classify_decision(decision_text: str) -> tuple[str, str, str, str]:
    """
    Convert the Phase 2F model-decision label into a Phase 2G promotion plan.

    Returns
    -------
    promotion_status, next_action, promotion_gate, customer_visibility
    """
    text = decision_text.upper()

    if "CANDIDATE" in text and "CONTROLLED" in text:
        return (
            "PROMOTION CANDIDATE - INTERNAL ONLY",
            "Stage this scenario for controlled internal comparison against the current customer model.",
            "Requires side-by-side dashboard testing before any customer-facing use.",
            "Developer view only",
        )

    if "DO NOT" in text or "NOT PROMOTE" in text:
        return (
            "DO NOT PROMOTE",
            "Keep this scenario in research outputs only and inspect assumptions before reuse.",
            "Blocked from promotion until validation and tuning concerns are resolved.",
            "Developer view only",
        )

    if "REVIEW" in text:
        return (
            "REVIEW BEFORE PROMOTION",
            "Review validation flags, tuning recommendations, and adjusted-payoff sensitivity.",
            "Requires manual review before promotion planning continues.",
            "Developer view only",
        )

    if "RESEARCH" in text:
        return (
            "KEEP AS RESEARCH MODEL",
            "Keep as internal research evidence but do not promote to the main customer workflow yet.",
            "Research-only until more validation evidence is available.",
            "Developer view only",
        )

    return (
        "UNCLASSIFIED - REVIEW",
        "Inspect the Phase 2F decision label and supporting evidence manually.",
        "No promotion until the decision label is understood.",
        "Developer view only",
    )


def build_lookup(df: pd.DataFrame) -> dict[str, dict[str, object]]:
    """Build a tolerant scenario lookup from a data frame."""
    if df.empty:
        return {}

    scenario_col = find_column(
        df,
        [
            "scenario",
            "scenario_name",
            "scenario_id",
            "path_name",
            "market_path",
            "display_name",
        ],
    )
    if scenario_col is None:
        return {}

    lookup: dict[str, dict[str, object]] = {}
    for _, row in df.iterrows():
        key = normalize_name(row.get(scenario_col, ""))
        if key:
            lookup[key] = row.to_dict()
    return lookup


def generate_model_promotion_plan() -> PromotionPlanResult:
    """Generate the Phase 2G controlled model-promotion plan."""
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    decision_df = safe_read_csv(MODEL_DECISION_CSV)
    if decision_df.empty:
        raise FileNotFoundError(
            f"Missing or empty model-decision input: {MODEL_DECISION_CSV}"
        )

    adjusted_lookup = build_lookup(safe_read_csv(ADJUSTED_PAYOFF_CSV))
    tuning_lookup = build_lookup(safe_read_csv(TUNING_CSV))
    validation_lookup = build_lookup(safe_read_csv(VALIDATION_CSV))

    scenario_col = find_column(
        decision_df,
        [
            "scenario",
            "scenario_name",
            "scenario_id",
            "path_name",
            "market_path",
            "display_name",
        ],
    )
    decision_col = find_column(
        decision_df,
        [
            "model_decision",
            "decision_label",
            "promotion_decision",
            "decision",
            "recommendation",
            "status",
        ],
    )
    rationale_col = find_column(
        decision_df,
        [
            "rationale",
            "interpretation",
            "decision_interpretation",
            "notes",
            "summary",
        ],
    )

    adjusted_effect_candidates = [
        "adjusted_minus_original_model_pl",
        "adjusted_minus_prior_premium_aware_result",
        "adjusted_minus_original",
        "model_change",
        "adjustment_effect",
    ]
    adjusted_rel_candidates = [
        "adjusted_covered_call_minus_buy_hold",
        "adjusted_minus_buy_hold",
        "covered_call_minus_buy_hold",
        "premium_aware_minus_buy_hold",
    ]

    rows: list[dict[str, object]] = []
    for index, row in decision_df.iterrows():
        scenario = safe_text(row.get(scenario_col), f"scenario_{index + 1}") if scenario_col else f"scenario_{index + 1}"
        scenario_key = normalize_name(scenario)
        decision_text = safe_text(row.get(decision_col), "UNCLASSIFIED") if decision_col else "UNCLASSIFIED"
        rationale = safe_text(row.get(rationale_col), "No model-decision rationale column found.") if rationale_col else "No model-decision rationale column found."

        promotion_status, next_action, promotion_gate, customer_visibility = classify_decision(decision_text)

        adjusted_row = adjusted_lookup.get(scenario_key, {})
        tuning_row = tuning_lookup.get(scenario_key, {})
        validation_row = validation_lookup.get(scenario_key, {})

        adjusted_effect = 0.0
        for col in adjusted_effect_candidates:
            if col in adjusted_row:
                adjusted_effect = safe_float(adjusted_row.get(col))
                break

        adjusted_relative = 0.0
        for col in adjusted_rel_candidates:
            if col in adjusted_row:
                adjusted_relative = safe_float(adjusted_row.get(col))
                break

        validation_status = "Not found"
        for col in ["overall_status", "validation_status", "status", "result"]:
            if col in validation_row:
                validation_status = safe_text(validation_row.get(col), "Not found")
                break

        tuning_status = "Not found"
        for col in ["overall_status", "tuning_status", "status", "recommendation_status", "result"]:
            if col in tuning_row:
                tuning_status = safe_text(tuning_row.get(col), "Not found")
                break

        rows.append(
            {
                "scenario": scenario,
                "phase2f_model_decision": decision_text,
                "phase2g_promotion_status": promotion_status,
                "recommended_next_action": next_action,
                "promotion_gate": promotion_gate,
                "customer_visibility": customer_visibility,
                "validation_status": validation_status,
                "tuning_status": tuning_status,
                "adjusted_relative_result": adjusted_relative,
                "adjusted_model_effect": adjusted_effect,
                "phase2f_rationale": rationale,
            }
        )

    plan_df = pd.DataFrame(rows)
    plan_df.to_csv(PROMOTION_PLAN_CSV, index=False)
    write_html_report(plan_df, PROMOTION_PLAN_HTML)
    summary_text = build_text_summary(plan_df)
    PROMOTION_PLAN_TEXT.write_text(summary_text, encoding="utf-8")

    return PromotionPlanResult(
        plan_df=plan_df,
        csv_path=PROMOTION_PLAN_CSV,
        html_path=PROMOTION_PLAN_HTML,
        text_path=PROMOTION_PLAN_TEXT,
        summary_text=summary_text,
    )


def write_html_report(plan_df: pd.DataFrame, path: Path) -> None:
    """Write a small HTML report for the Phase 2G promotion plan."""
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    counts = plan_df["phase2g_promotion_status"].value_counts().reset_index()
    counts.columns = ["phase2g_promotion_status", "scenario_count"]

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset=\"utf-8\">
  <title>Phase 2G Model Promotion Plan</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 28px; color: #222; }}
    h1, h2 {{ color: #1f2937; }}
    .note {{ background: #f3f4f6; border-left: 4px solid #6b7280; padding: 12px; margin: 18px 0; }}
    table {{ border-collapse: collapse; width: 100%; margin: 16px 0; font-size: 14px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
    th {{ background: #f9fafb; }}
  </style>
</head>
<body>
  <h1>Phase 2G Controlled Model-Promotion Plan</h1>
  <p><strong>Generated:</strong> {generated}</p>
  <div class=\"note\">
    This is an internal model-development report. It does not promote any model into the customer-facing workflow by itself.
  </div>
  <h2>Promotion status counts</h2>
  {counts.to_html(index=False)}
  <h2>Scenario-level promotion plan</h2>
  {plan_df.to_html(index=False)}
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


def build_text_summary(plan_df: pd.DataFrame) -> str:
    """Build a plain-text Phase 2G summary report."""
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    counts = plan_df["phase2g_promotion_status"].value_counts()
    candidate_count = int(counts.get("PROMOTION CANDIDATE - INTERNAL ONLY", 0))
    review_count = int(counts.get("REVIEW BEFORE PROMOTION", 0))
    do_not_count = int(counts.get("DO NOT PROMOTE", 0))
    research_count = int(counts.get("KEEP AS RESEARCH MODEL", 0))

    lines = [
        "Phase 2G controlled model-promotion planning summary",
        "=" * 72,
        f"Generated: {generated}",
        "",
        "Purpose:",
        "  Consolidate Phase 2F model-decision evidence into a controlled",
        "  internal promotion plan. This does not alter the customer-facing model.",
        "",
        "Promotion status counts:",
    ]

    for status, count in counts.items():
        lines.append(f"  {status}: {count}")

    lines.extend(
        [
            "",
            "Overall Phase 2G interpretation:",
            f"  Internal promotion candidates: {candidate_count}",
            f"  Review-before-promotion scenarios: {review_count}",
            f"  Research-only scenarios: {research_count}",
            f"  Do-not-promote scenarios: {do_not_count}",
            "",
            "Standing gate:",
            "  Keep all Phase 2G promotion candidates in Developer view only until",
            "  side-by-side testing, customer-language review, and dashboard safety",
            "  checks are complete.",
            "",
            "Next recommended step:",
            "  Add a Phase 2G model-promotion viewer, then a Phase 2G pipeline check.",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    result = generate_model_promotion_plan()
    print("Phase 2G controlled model-promotion plan generated.")
    print(f"CSV:  {result.csv_path}")
    print(f"HTML: {result.html_path}")
    print(f"Text: {result.text_path}")
