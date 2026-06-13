"""
phase9_customer_feedback_capture_template.py

Phase 9-3 customer feedback capture template.

This module is passive. It creates a structured beta/customer feedback template
for evaluating the paid Covered Call Simulator during trial use.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

TEMPLATE_CSV = OUTPUT_TABLE_DIR / "phase9_3_customer_feedback_capture_template.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase9_3_customer_feedback_capture_template_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase9_3_customer_feedback_capture_template.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase9_3_customer_feedback_capture_template_report.txt"

READY_MARKER = "PHASE9_3_CUSTOMER_FEEDBACK_CAPTURE_TEMPLATE_READY"
RELEASE_DECISION = "PHASE9_3_CUSTOMER_FEEDBACK_CAPTURE_TEMPLATE_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "customer_feedback_capture_template"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_phase9_3_template() -> list[dict[str, Any]]:
    return [
        {
            "feedback_area": "First impression",
            "question": "What did you think this simulator was designed to help you understand?",
            "response_type": "free_text",
            "required_for_beta": True,
            "why_it_matters": "Tests whether product positioning is clear.",
        },
        {
            "feedback_area": "Setup clarity",
            "question": "Were the ticker, account size, risk tier, delta, and DTE inputs understandable?",
            "response_type": "1_to_5_plus_comment",
            "required_for_beta": True,
            "why_it_matters": "Identifies friction in the customer setup workflow.",
        },
        {
            "feedback_area": "Synthetic default",
            "question": "Was it clear that synthetic scenarios are the default mode?",
            "response_type": "yes_no_plus_comment",
            "required_for_beta": True,
            "why_it_matters": "Confirms default-mode safety.",
        },
        {
            "feedback_area": "Historical mode",
            "question": "Was it clear that imported historical data is optional and must be selected intentionally?",
            "response_type": "yes_no_plus_comment",
            "required_for_beta": True,
            "why_it_matters": "Confirms historical mode is understood as explicit opt-in.",
        },
        {
            "feedback_area": "Forecast caution",
            "question": "Was it clear that historical data is scenario input, not a forecast?",
            "response_type": "yes_no_plus_comment",
            "required_for_beta": True,
            "why_it_matters": "Tests whether the product avoids oracle-like interpretation.",
        },
        {
            "feedback_area": "Risk wording",
            "question": "Did the simulator make the risks and tradeoffs of covered calls clear?",
            "response_type": "1_to_5_plus_comment",
            "required_for_beta": True,
            "why_it_matters": "Checks commercial and trust-safe language.",
        },
        {
            "feedback_area": "Results clarity",
            "question": "Were the results, charts, and reports easy to interpret?",
            "response_type": "1_to_5_plus_comment",
            "required_for_beta": True,
            "why_it_matters": "Evaluates customer usefulness of outputs.",
        },
        {
            "feedback_area": "Value proposition",
            "question": "Would you use this before placing or managing a covered-call trade? Why or why not?",
            "response_type": "free_text",
            "required_for_beta": True,
            "why_it_matters": "Tests commercial value and product-market fit.",
        },
        {
            "feedback_area": "Trust blockers",
            "question": "What, if anything, made you hesitate to trust or use the simulator?",
            "response_type": "free_text",
            "required_for_beta": True,
            "why_it_matters": "Identifies adoption barriers before launch.",
        },
        {
            "feedback_area": "Improvement request",
            "question": "What one change would make the simulator more useful to you?",
            "response_type": "free_text",
            "required_for_beta": True,
            "why_it_matters": "Prioritizes next product changes.",
        },
    ]


def build_phase9_3_summary() -> dict[str, Any]:
    _ensure_dirs()

    template = build_phase9_3_template()
    template_df = pd.DataFrame(template)
    template_df.to_csv(TEMPLATE_CSV, index=False)

    required_count = int(template_df["required_for_beta"].sum())

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "customer_feedback_template_created": True,
        "feedback_questions": int(len(template_df)),
        "required_beta_questions": required_count,
        "synthetic_default_feedback_included": True,
        "historical_opt_in_feedback_included": True,
        "historical_data_is_scenario_input_not_forecast": True,
        "risk_wording_feedback_included": True,
        "value_proposition_feedback_included": True,
        "trust_blocker_feedback_included": True,
        "row_count": int(len(template_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 9-3 customer feedback capture template",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Feedback questions: {summary['feedback_questions']}",
        f"Required beta questions: {summary['required_beta_questions']}",
        f"Synthetic default feedback included: {summary['synthetic_default_feedback_included']}",
        f"Historical opt-in feedback included: {summary['historical_opt_in_feedback_included']}",
        f"Historical data is scenario input, not forecast: {summary['historical_data_is_scenario_input_not_forecast']}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase9_3_summary(), indent=2))
