"""
phase9_beta_safety_disclaimer_review.py

Phase 9-4 beta safety and disclaimer review.

This module is passive. It defines the beta safety and disclaimer review
checklist for the paid Covered Call Simulator before broader customer trials.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

REVIEW_CSV = OUTPUT_TABLE_DIR / "phase9_4_beta_safety_disclaimer_review.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase9_4_beta_safety_disclaimer_review_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase9_4_beta_safety_disclaimer_review.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase9_4_beta_safety_disclaimer_review_report.txt"

READY_MARKER = "PHASE9_4_BETA_SAFETY_DISCLAIMER_REVIEW_READY"
RELEASE_DECISION = "PHASE9_4_BETA_SAFETY_DISCLAIMER_REVIEW_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "beta_safety_disclaimer_review"
CAUTION = "Historical data is scenario input, not forecast"
REGIME_CAUTION = "Regime detection is probabilistic guidance, not an oracle"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_phase9_4_review() -> list[dict[str, Any]]:
    return [
        {
            "review_area": "Options risk",
            "required_wording": "Options involve risk and covered calls can underperform buy-and-hold in rising markets.",
            "unsafe_wording_to_avoid": "safe income, guaranteed income, risk-free income",
            "required_for_beta": True,
        },
        {
            "review_area": "No financial advice",
            "required_wording": "The simulator is educational and analytical, not personalized investment advice.",
            "unsafe_wording_to_avoid": "you should buy, this is suitable for you, advisor-approved",
            "required_for_beta": True,
        },
        {
            "review_area": "Historical data caution",
            "required_wording": CAUTION,
            "unsafe_wording_to_avoid": "history predicts the next outcome, forecast engine",
            "required_for_beta": True,
        },
        {
            "review_area": "Regime detection caution",
            "required_wording": REGIME_CAUTION,
            "unsafe_wording_to_avoid": "market regime oracle, guaranteed regime signal",
            "required_for_beta": True,
        },
        {
            "review_area": "Profit claims",
            "required_wording": "Simulation output is scenario-dependent and does not guarantee future results.",
            "unsafe_wording_to_avoid": "guaranteed profit, guaranteed outperformance, no-loss strategy",
            "required_for_beta": True,
        },
        {
            "review_area": "Beta limitations",
            "required_wording": "Beta access is for testing usability, clarity, and workflow reliability.",
            "unsafe_wording_to_avoid": "production guarantee, final commercial release",
            "required_for_beta": True,
        },
        {
            "review_area": "Data quality",
            "required_wording": "Imported data and option-chain inputs should be checked for completeness and reasonableness.",
            "unsafe_wording_to_avoid": "data is always complete, no validation needed",
            "required_for_beta": True,
        },
        {
            "review_area": "Customer responsibility",
            "required_wording": "Users remain responsible for their own trading decisions and risk controls.",
            "unsafe_wording_to_avoid": "the app manages your risk for you",
            "required_for_beta": True,
        },
    ]


def build_phase9_4_summary() -> dict[str, Any]:
    _ensure_dirs()

    review_rows = build_phase9_4_review()
    review_df = pd.DataFrame(review_rows)
    review_df.to_csv(REVIEW_CSV, index=False)

    required_count = int(review_df["required_for_beta"].sum())

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "beta_safety_disclaimer_review_created": True,
        "options_risk_wording_required": True,
        "no_financial_advice_wording_required": True,
        "historical_data_is_scenario_input_not_forecast": True,
        "regime_detection_probabilistic_not_oracle": True,
        "no_guaranteed_profit_wording": True,
        "customer_responsibility_wording_required": True,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "review_rows": int(len(review_df)),
        "required_review_items": required_count,
        "row_count": int(len(review_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 9-4 beta safety and disclaimer review",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Review rows: {summary['review_rows']}",
        f"Required review items: {summary['required_review_items']}",
        f"{CAUTION}: {summary['historical_data_is_scenario_input_not_forecast']}",
        f"{REGIME_CAUTION}: {summary['regime_detection_probabilistic_not_oracle']}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase9_4_summary(), indent=2))
