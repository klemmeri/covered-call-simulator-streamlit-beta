"""
phase9_trial_run_smoke_test_script.py

Phase 9-5 trial-run smoke-test script.

This module is passive. It creates a beta-trial smoke-test checklist for running
through the paid simulator as a prospective customer would use it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

SCRIPT_CSV = OUTPUT_TABLE_DIR / "phase9_5_trial_run_smoke_test_script.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase9_5_trial_run_smoke_test_script_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase9_5_trial_run_smoke_test_script.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase9_5_trial_run_smoke_test_script_report.txt"

READY_MARKER = "PHASE9_5_TRIAL_RUN_SMOKE_TEST_SCRIPT_READY"
RELEASE_DECISION = "PHASE9_5_TRIAL_RUN_SMOKE_TEST_SCRIPT_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "trial_run_smoke_test_script"
CAUTION = "Historical data is scenario input, not forecast"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_phase9_5_script() -> list[dict[str, Any]]:
    return [
        {
            "step_number": 1,
            "test_step": "Open the hosted or local beta app.",
            "expected_result": "The paid simulator dashboard loads without errors.",
            "required_for_beta": True,
        },
        {
            "step_number": 2,
            "test_step": "Run the default synthetic scenario without changing the data mode.",
            "expected_result": "Synthetic scenarios remain the default workflow.",
            "required_for_beta": True,
        },
        {
            "step_number": 3,
            "test_step": "Confirm that imported historical data is not selected by default.",
            "expected_result": "Historical mode requires explicit customer selection.",
            "required_for_beta": True,
        },
        {
            "step_number": 4,
            "test_step": "Select imported historical data explicitly if available in the beta setup.",
            "expected_result": "Historical mode routes to historical_import only after explicit selection.",
            "required_for_beta": True,
        },
        {
            "step_number": 5,
            "test_step": "Review the historical-data caution text.",
            "expected_result": CAUTION,
            "required_for_beta": True,
        },
        {
            "step_number": 6,
            "test_step": "Run a basic covered-call scenario and inspect the results summary.",
            "expected_result": "The result is customer-readable and does not imply guaranteed profit.",
            "required_for_beta": True,
        },
        {
            "step_number": 7,
            "test_step": "Review charts and tables for clarity.",
            "expected_result": "Charts and tables support the scenario interpretation without overwhelming the user.",
            "required_for_beta": True,
        },
        {
            "step_number": 8,
            "test_step": "Review risk and no-advice wording.",
            "expected_result": "Options risk and no-financial-advice language are visible and clear.",
            "required_for_beta": True,
        },
        {
            "step_number": 9,
            "test_step": "Record tester feedback after the trial run.",
            "expected_result": "Feedback captures usability, trust, clarity, and value-proposition comments.",
            "required_for_beta": True,
        },
    ]


def build_phase9_5_summary() -> dict[str, Any]:
    _ensure_dirs()

    script_rows = build_phase9_5_script()
    script_df = pd.DataFrame(script_rows)
    script_df.to_csv(SCRIPT_CSV, index=False)

    required_count = int(script_df["required_for_beta"].sum())

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "trial_run_smoke_test_script_created": True,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "unknown_modes_fall_back_to_synthetic": True,
        "historical_data_is_scenario_input_not_forecast": True,
        "no_guaranteed_profit_wording_required": True,
        "risk_wording_required": True,
        "feedback_capture_required": True,
        "script_rows": int(len(script_df)),
        "required_trial_steps": required_count,
        "row_count": int(len(script_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 9-5 trial-run smoke-test script",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Script rows: {summary['script_rows']}",
        f"Required trial steps: {summary['required_trial_steps']}",
        f"{CAUTION}: {summary['historical_data_is_scenario_input_not_forecast']}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase9_5_summary(), indent=2))
