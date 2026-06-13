"""
phase9_beta_testing_customer_trial_workflow_map.py

Phase 9-1 beta testing and customer-trial workflow map.

This module is passive. It defines the beta-test structure for the paid Covered
Call Simulator before any real customer trial is started.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

WORKFLOW_CSV = OUTPUT_TABLE_DIR / "phase9_1_beta_testing_customer_trial_workflow_map.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase9_1_beta_testing_customer_trial_workflow_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase9_1_beta_testing_customer_trial_workflow_map.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase9_1_beta_testing_customer_trial_workflow_map_report.txt"

READY_MARKER = "PHASE9_1_BETA_TESTING_CUSTOMER_TRIAL_WORKFLOW_MAP_READY"
RELEASE_DECISION = "PHASE9_1_BETA_TESTING_CUSTOMER_TRIAL_WORKFLOW_MAP_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "beta_testing_customer_trial_workflow_map"


PHASE9_PLAN = [
    "Phase 9-1  Beta testing and customer-trial workflow map",
    "Phase 9-2  Beta tester onboarding checklist",
    "Phase 9-3  Customer feedback capture template",
    "Phase 9-4  Beta safety and disclaimer review",
    "Phase 9-5  Trial-run smoke-test script",
    "Phase 9-6  Phase 9 completion handoff",
]


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_phase9_1_workflow() -> list[dict[str, Any]]:
    return [
        {
            "workflow_step": "Select beta testers",
            "purpose": "Use a small private group before broad release.",
            "customer_visible": False,
            "required_for_beta": True,
            "risk_control": "Limit early exposure while finding usability problems.",
        },
        {
            "workflow_step": "Send onboarding instructions",
            "purpose": "Explain access, expected use, limitations, and feedback process.",
            "customer_visible": True,
            "required_for_beta": True,
            "risk_control": "Set expectations before anyone uses the simulator.",
        },
        {
            "workflow_step": "Confirm disclaimer acceptance",
            "purpose": "Make risk and no-advice language visible before use.",
            "customer_visible": True,
            "required_for_beta": True,
            "risk_control": "Avoid treating simulator output as financial advice.",
        },
        {
            "workflow_step": "Run synthetic default scenario",
            "purpose": "Confirm customer can run the default workflow.",
            "customer_visible": True,
            "required_for_beta": True,
            "risk_control": "Synthetic mode remains default and stable.",
        },
        {
            "workflow_step": "Run optional historical scenario",
            "purpose": "Confirm historical mode is explicit opt-in only.",
            "customer_visible": True,
            "required_for_beta": True,
            "risk_control": "Historical data remains scenario input, not forecast.",
        },
        {
            "workflow_step": "Collect structured feedback",
            "purpose": "Capture confusion, bugs, wording issues, and missing features.",
            "customer_visible": True,
            "required_for_beta": True,
            "risk_control": "Convert subjective comments into actionable fixes.",
        },
        {
            "workflow_step": "Review results before expanding access",
            "purpose": "Decide whether the simulator is ready for a larger trial.",
            "customer_visible": False,
            "required_for_beta": True,
            "risk_control": "Do not expand access before core workflow is stable.",
        },
    ]


def build_phase9_1_summary() -> dict[str, Any]:
    _ensure_dirs()

    workflow_rows = build_phase9_1_workflow()
    workflow_df = pd.DataFrame(workflow_rows)
    workflow_df.to_csv(WORKFLOW_CSV, index=False)

    required_count = int(workflow_df["required_for_beta"].sum())
    customer_visible_count = int(workflow_df["customer_visible"].sum())

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "beta_workflow_map_created": True,
        "phase9_plan_defined": True,
        "phase9_step_count": len(PHASE9_PLAN),
        "workflow_rows": int(len(workflow_df)),
        "required_beta_steps": required_count,
        "customer_visible_steps": customer_visible_count,
        "private_beta_first": True,
        "feedback_capture_required": True,
        "disclaimer_acceptance_required": True,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "historical_data_is_scenario_input_not_forecast": True,
        "regime_detection_probabilistic_not_oracle": True,
        "row_count": int(len(workflow_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 9-1 beta testing and customer-trial workflow map",
        "=" * 78,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Workflow rows: {summary['workflow_rows']}",
        f"Required beta steps: {summary['required_beta_steps']}",
        f"Customer-visible steps: {summary['customer_visible_steps']}",
        "Private beta first: True",
        "Feedback capture required: True",
        "Disclaimer acceptance required: True",
        "Dashboard changed: False",
        "Engine changed: False",
        "",
        "Phase 9 plan:",
    ] + PHASE9_PLAN

    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase9_1_summary(), indent=2))
