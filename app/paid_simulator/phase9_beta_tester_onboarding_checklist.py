"""
phase9_beta_tester_onboarding_checklist.py

Phase 9-2 beta tester onboarding checklist.

This module is passive. It creates the customer-trial onboarding checklist for
beta testers of the Covered Call Simulator.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

CHECKLIST_CSV = OUTPUT_TABLE_DIR / "phase9_2_beta_tester_onboarding_checklist.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase9_2_beta_tester_onboarding_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase9_2_beta_tester_onboarding_checklist.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase9_2_beta_tester_onboarding_checklist_report.txt"

READY_MARKER = "PHASE9_2_BETA_TESTER_ONBOARDING_CHECKLIST_READY"
RELEASE_DECISION = "PHASE9_2_BETA_TESTER_ONBOARDING_CHECKLIST_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "beta_tester_onboarding_checklist"
CAUTION = "Historical data is scenario input, not forecast"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_phase9_2_checklist() -> list[dict[str, Any]]:
    return [
        {
            "step": "Invite beta tester",
            "purpose": "Identify the tester and confirm they understand this is a beta product.",
            "customer_message": "You are helping test a covered-call simulation tool before public release.",
            "required": True,
        },
        {
            "step": "Confirm risk understanding",
            "purpose": "Make clear that options strategies involve risk and the tool is educational/scenario-based.",
            "customer_message": "The simulator is not financial advice and does not guarantee outcomes.",
            "required": True,
        },
        {
            "step": "Explain default mode",
            "purpose": "Clarify that synthetic scenarios are the default workflow.",
            "customer_message": "Synthetic scenarios are the default starting point.",
            "required": True,
        },
        {
            "step": "Explain historical mode",
            "purpose": "Clarify that imported historical data is explicit opt-in only.",
            "customer_message": CAUTION,
            "required": True,
        },
        {
            "step": "Provide access instructions",
            "purpose": "Tell the tester how to open the hosted app or private beta link.",
            "customer_message": "Use the provided private link or access instructions only for beta testing.",
            "required": True,
        },
        {
            "step": "Run first scenario",
            "purpose": "Ask the tester to run one simple default synthetic scenario.",
            "customer_message": "Start with the default setup before changing advanced inputs.",
            "required": True,
        },
        {
            "step": "Record usability feedback",
            "purpose": "Capture where the tester was confused or unsure.",
            "customer_message": "Please note any confusing labels, results, or steps.",
            "required": True,
        },
        {
            "step": "Record trust and wording feedback",
            "purpose": "Check whether warnings, disclaimers, and output wording are clear.",
            "customer_message": "Tell us whether any wording sounds like advice, a forecast, or a promise.",
            "required": True,
        },
    ]


def build_phase9_2_summary() -> dict[str, Any]:
    _ensure_dirs()

    checklist = build_phase9_2_checklist()
    checklist_df = pd.DataFrame(checklist)
    checklist_df.to_csv(CHECKLIST_CSV, index=False)

    required_count = int(checklist_df["required"].sum())

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "beta_tester_onboarding_checklist_created": True,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "historical_data_is_scenario_input_not_forecast": True,
        "financial_advice_disclaimer_required": True,
        "options_risk_disclosure_required": True,
        "feedback_capture_required": True,
        "checklist_rows": int(len(checklist_df)),
        "required_steps": required_count,
        "row_count": int(len(checklist_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 9-2 beta tester onboarding checklist",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Checklist rows: {summary['checklist_rows']}",
        f"Required steps: {summary['required_steps']}",
        f"Historical data is scenario input, not forecast: {summary['historical_data_is_scenario_input_not_forecast']}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase9_2_summary(), indent=2))
