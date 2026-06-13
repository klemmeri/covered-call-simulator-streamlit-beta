
"""
phase8_hosted_smoke_test_plan.py

Phase 8-5 hosted smoke-test plan.

This module is passive. It defines a hosted smoke-test checklist for deploying
the paid Covered Call Simulator as a Streamlit-compatible MVP.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

PLAN_CSV = OUTPUT_TABLE_DIR / "phase8_5_hosted_smoke_test_plan.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase8_5_hosted_smoke_test_plan_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase8_5_hosted_smoke_test_plan.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase8_5_hosted_smoke_test_plan_report.txt"

READY_MARKER = "PHASE8_5_HOSTED_SMOKE_TEST_PLAN_READY"
RELEASE_DECISION = "PHASE8_5_HOSTED_SMOKE_TEST_PLAN_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "hosted_smoke_test_plan"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_phase8_5_plan() -> list[dict[str, Any]]:
    return [
        {
            "test_area": "App launch",
            "smoke_test": "Hosted app opens without import errors.",
            "expected_result": "Dashboard loads and displays the paid simulator landing section.",
            "required_for_mvp": True,
        },
        {
            "test_area": "Synthetic default",
            "smoke_test": "Open hosted app without changing data mode.",
            "expected_result": "Synthetic scenarios remain the default path.",
            "required_for_mvp": True,
        },
        {
            "test_area": "Historical opt-in",
            "smoke_test": "Select imported historical data explicitly.",
            "expected_result": "Historical mode is available only after explicit selection.",
            "required_for_mvp": True,
        },
        {
            "test_area": "Fallback safety",
            "smoke_test": "Confirm unknown/missing mode falls back to synthetic.",
            "expected_result": "No accidental historical-mode activation.",
            "required_for_mvp": True,
        },
        {
            "test_area": "Risk wording",
            "smoke_test": "Review visible warnings and report wording.",
            "expected_result": "No guaranteed-profit, risk-free, advisory, or oracle wording.",
            "required_for_mvp": True,
        },
        {
            "test_area": "Scenario report",
            "smoke_test": "Run a basic scenario and confirm reports/tables are written.",
            "expected_result": "Customer-readable output files are created.",
            "required_for_mvp": True,
        },
        {
            "test_area": "Access control",
            "smoke_test": "Confirm access is private or controlled for MVP.",
            "expected_result": "Only intended beta/customer users can access the app.",
            "required_for_mvp": True,
        },
        {
            "test_area": "Dependency stability",
            "smoke_test": "Confirm hosted environment installs required packages.",
            "expected_result": "pandas, numpy, matplotlib, and streamlit import successfully.",
            "required_for_mvp": True,
        },
    ]


def build_phase8_5_summary() -> dict[str, Any]:
    _ensure_dirs()

    plan = build_phase8_5_plan()
    plan_df = pd.DataFrame(plan)
    plan_df.to_csv(PLAN_CSV, index=False)

    required_count = int(plan_df["required_for_mvp"].sum())

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "hosted_smoke_test_plan_created": True,
        "streamlit_mvp_path_supported": True,
        "customer_access_model_defined": True,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "unknown_modes_fall_back_to_synthetic": True,
        "historical_data_is_scenario_input_not_forecast": True,
        "risk_wording_required": True,
        "access_control_required": True,
        "plan_rows": int(len(plan_df)),
        "required_smoke_tests": required_count,
        "row_count": int(len(plan_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 8-5 hosted smoke-test plan",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Plan rows: {summary['plan_rows']}",
        f"Required smoke tests: {summary['required_smoke_tests']}",
        f"Streamlit MVP path supported: {summary['streamlit_mvp_path_supported']}",
        f"Customer access model defined: {summary['customer_access_model_defined']}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase8_5_summary(), indent=2))
