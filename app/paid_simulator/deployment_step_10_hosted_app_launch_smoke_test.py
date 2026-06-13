"""
deployment_step_10_hosted_app_launch_smoke_test.py

Deployment Step 10 hosted app launch and smoke-test checklist.

This module is passive. It creates a checklist for manually verifying the hosted
Streamlit app after it is created from the GitHub repository.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

CHECKLIST_CSV = OUTPUT_TABLE_DIR / "deployment_step_10_hosted_app_launch_smoke_test_checklist.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "deployment_step_10_hosted_app_launch_smoke_test_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "deployment_step_10_hosted_app_launch_smoke_test.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "deployment_step_10_hosted_app_launch_smoke_test_report.txt"

READY_MARKER = "DEPLOYMENT_STEP_10_HOSTED_APP_LAUNCH_SMOKE_TEST_READY"
RELEASE_DECISION = "DEPLOYMENT_STEP_10_HOSTED_APP_LAUNCH_SMOKE_TEST_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "hosted_app_launch_smoke_test"
ENTRY_POINT = "app/paid_simulator/config_form_app.py"
CAUTION = "Historical data is scenario input, not forecast"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_deployment_step_10_checklist() -> list[dict[str, Any]]:
    return [
        {
            "test_area": "Streamlit Cloud build",
            "manual_check": "Deploy the app from the GitHub repository and watch the build log.",
            "expected_result": "Build finishes without package, import, or file-path errors.",
            "required": True,
        },
        {
            "test_area": "Hosted app launch",
            "manual_check": "Open the hosted Streamlit URL in a browser.",
            "expected_result": "Covered Call Strategy Stress Test dashboard loads.",
            "required": True,
        },
        {
            "test_area": "Customer view",
            "manual_check": "Select Customer view in the sidebar.",
            "expected_result": "Developer-only diagnostics are hidden.",
            "required": True,
        },
        {
            "test_area": "Synthetic default",
            "manual_check": "Open the app without selecting historical mode.",
            "expected_result": "Synthetic scenarios remain the default workflow.",
            "required": True,
        },
        {
            "test_area": "Historical opt-in",
            "manual_check": "Select Imported historical data only deliberately.",
            "expected_result": "Historical mode is explicit opt-in only.",
            "required": True,
        },
        {
            "test_area": "Historical caution",
            "manual_check": "Review historical-data wording in the app.",
            "expected_result": CAUTION,
            "required": True,
        },
        {
            "test_area": "Basic scenario run",
            "manual_check": "Run a standard covered-call scenario from the dashboard.",
            "expected_result": "Scenario results, tables, and report sections appear without errors.",
            "required": True,
        },
        {
            "test_area": "Risk wording",
            "manual_check": "Review the visible risk/disclaimer language.",
            "expected_result": "No guaranteed-profit, risk-free, advisory, or oracle wording appears.",
            "required": True,
        },
        {
            "test_area": "Second browser sanity check",
            "manual_check": "Open the hosted app in a second browser or private window.",
            "expected_result": "The app loads consistently outside the first browser session.",
            "required": False,
        },
    ]


def build_deployment_step_10_summary() -> dict[str, Any]:
    _ensure_dirs()

    checklist = build_deployment_step_10_checklist()
    checklist_df = pd.DataFrame(checklist)
    checklist_df.to_csv(CHECKLIST_CSV, index=False)

    required_count = int(checklist_df["required"].sum())

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "hosted_app_launch_smoke_test_created": True,
        "streamlit_entry_point": ENTRY_POINT,
        "streamlit_cloud_app_setup_complete": True,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "historical_data_is_scenario_input_not_forecast": True,
        "risk_wording_required": True,
        "hosted_manual_verification_required": True,
        "checklist_rows": int(len(checklist_df)),
        "required_smoke_tests": required_count,
        "row_count": int(len(checklist_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Deployment Step 10 hosted app launch and smoke-test checklist",
        "=" * 78,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Streamlit entry point: {ENTRY_POINT}",
        f"Checklist rows: {summary['checklist_rows']}",
        f"Required smoke tests: {summary['required_smoke_tests']}",
        f"{CAUTION}: {summary['historical_data_is_scenario_input_not_forecast']}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_deployment_step_10_summary(), indent=2))
