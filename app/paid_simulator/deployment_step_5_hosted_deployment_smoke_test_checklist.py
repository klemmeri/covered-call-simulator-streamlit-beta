"""
deployment_step_5_hosted_deployment_smoke_test_checklist.py

Deployment Step 5 hosted deployment smoke-test checklist.

This module is passive. It defines the manual checks to run after the app is
hosted on Streamlit Cloud or a Streamlit-compatible hosting service.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

CHECKLIST_CSV = OUTPUT_TABLE_DIR / "deployment_step_5_hosted_deployment_smoke_test_checklist.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "deployment_step_5_hosted_deployment_smoke_test_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "deployment_step_5_hosted_deployment_smoke_test_checklist.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "deployment_step_5_hosted_deployment_smoke_test_checklist_report.txt"

READY_MARKER = "DEPLOYMENT_STEP_5_HOSTED_DEPLOYMENT_SMOKE_TEST_CHECKLIST_READY"
RELEASE_DECISION = "DEPLOYMENT_STEP_5_HOSTED_DEPLOYMENT_SMOKE_TEST_CHECKLIST_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "hosted_deployment_smoke_test_checklist"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_deployment_step_5_checklist() -> list[dict[str, Any]]:
    return [
        {
            "test_order": 1,
            "test_area": "Hosted app launch",
            "manual_check": "Open the hosted Streamlit URL in a browser.",
            "expected_result": "The paid simulator dashboard loads without import or startup errors.",
            "required_for_beta": True,
        },
        {
            "test_order": 2,
            "test_area": "Synthetic default path",
            "manual_check": "Load the dashboard without changing the data mode.",
            "expected_result": "Synthetic scenarios are the default workflow.",
            "required_for_beta": True,
        },
        {
            "test_order": 3,
            "test_area": "Historical opt-in path",
            "manual_check": "Select Imported historical data explicitly.",
            "expected_result": "Historical mode is available only after explicit user selection.",
            "required_for_beta": True,
        },
        {
            "test_order": 4,
            "test_area": "Scenario caution wording",
            "manual_check": "Review text near the historical data option and generated reports.",
            "expected_result": "Historical data is described as scenario input, not a forecast.",
            "required_for_beta": True,
        },
        {
            "test_order": 5,
            "test_area": "Basic simulation run",
            "manual_check": "Run one default covered-call scenario with the hosted app.",
            "expected_result": "Results, tables, and charts display without error.",
            "required_for_beta": True,
        },
        {
            "test_order": 6,
            "test_area": "Risk wording",
            "manual_check": "Review visible risk/disclaimer language.",
            "expected_result": "No guaranteed-profit, risk-free, financial-advice, or oracle wording appears.",
            "required_for_beta": True,
        },
        {
            "test_order": 7,
            "test_area": "Access control",
            "manual_check": "Confirm the app URL/access method is private enough for the beta stage.",
            "expected_result": "Only intended beta/customer users can access the app.",
            "required_for_beta": True,
        },
        {
            "test_order": 8,
            "test_area": "Cross-browser sanity check",
            "manual_check": "Open the hosted app in at least one alternate browser or private window.",
            "expected_result": "The dashboard still loads and the default workflow remains usable.",
            "required_for_beta": False,
        },
    ]


def build_deployment_step_5_summary() -> dict[str, Any]:
    _ensure_dirs()
    rows = build_deployment_step_5_checklist()
    df = pd.DataFrame(rows)
    df.to_csv(CHECKLIST_CSV, index=False)
    required_count = int(df["required_for_beta"].sum())

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "hosted_smoke_test_checklist_created": True,
        "streamlit_hosted_url_required": True,
        "manual_browser_review_required": True,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "historical_data_is_scenario_input_not_forecast": True,
        "risk_wording_required": True,
        "access_control_required": True,
        "checklist_rows": int(len(df)),
        "required_beta_checks": required_count,
        "row_count": int(len(df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Deployment Step 5 hosted deployment smoke-test checklist",
        "=" * 76,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Checklist rows: {summary['checklist_rows']}",
        f"Required beta checks: {summary['required_beta_checks']}",
        f"Manual browser review required: {summary['manual_browser_review_required']}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(build_deployment_step_5_summary(), indent=2))
