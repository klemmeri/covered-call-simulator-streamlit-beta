
"""
deployment_step_9_streamlit_cloud_app_setup.py

Deployment Step 9: Streamlit Cloud app setup instructions.

This module is passive. It creates a checklist for connecting the GitHub
repository to Streamlit Cloud and configuring the app entry point.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

CHECKLIST_CSV = OUTPUT_TABLE_DIR / "deployment_step_9_streamlit_cloud_app_setup_checklist.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "deployment_step_9_streamlit_cloud_app_setup_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "deployment_step_9_streamlit_cloud_app_setup.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "deployment_step_9_streamlit_cloud_app_setup_report.txt"

READY_MARKER = "DEPLOYMENT_STEP_9_STREAMLIT_CLOUD_APP_SETUP_READY"
RELEASE_DECISION = "DEPLOYMENT_STEP_9_STREAMLIT_CLOUD_APP_SETUP_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "streamlit_cloud_app_setup"
ENTRY_POINT = "app/paid_simulator/config_form_app.py"
LOCAL_RUN_COMMAND = "streamlit run app/paid_simulator/config_form_app.py"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_deployment_step_9_checklist() -> list[dict[str, Any]]:
    return [
        {
            "step": 1,
            "task": "Confirm the final local backup exists before connecting hosting.",
            "expected_result": "CoveredCallSimulator_Phase10_Complete_v1_0_0_YYYY-MM-DD.zip is stored safely.",
            "required": True,
        },
        {
            "step": 2,
            "task": "Confirm the GitHub repository exists and contains the latest project files.",
            "expected_result": "Repository is private for beta/MVP unless intentionally made public later.",
            "required": True,
        },
        {
            "step": 3,
            "task": "Open Streamlit Cloud and create a new app from the GitHub repository.",
            "expected_result": "Streamlit Cloud can see the repository and selected branch.",
            "required": True,
        },
        {
            "step": 4,
            "task": "Set the main app file path.",
            "expected_result": ENTRY_POINT,
            "required": True,
        },
        {
            "step": 5,
            "task": "Confirm requirements.txt is in the repository root.",
            "expected_result": "Streamlit Cloud installs pandas, numpy, matplotlib, and streamlit.",
            "required": True,
        },
        {
            "step": 6,
            "task": "Confirm no secrets or credentials are stored in the repository.",
            "expected_result": "No API keys, broker credentials, tokens, passwords, or payment secrets are committed.",
            "required": True,
        },
        {
            "step": 7,
            "task": "Deploy the app and watch build logs.",
            "expected_result": "Build finishes without import or dependency errors.",
            "required": True,
        },
        {
            "step": 8,
            "task": "Open the deployed app URL.",
            "expected_result": "Covered Call Strategy Stress Test loads in the browser.",
            "required": True,
        },
        {
            "step": 9,
            "task": "Run the hosted smoke-test checklist from Deployment Step 5.",
            "expected_result": "Synthetic default, historical opt-in, caution wording, and basic scenario flow all pass.",
            "required": True,
        },
    ]


def build_deployment_step_9_summary() -> dict[str, Any]:
    _ensure_dirs()

    checklist = build_deployment_step_9_checklist()
    checklist_df = pd.DataFrame(checklist)
    checklist_df.to_csv(CHECKLIST_CSV, index=False)

    required_count = int(checklist_df["required"].sum())

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "streamlit_cloud_setup_checklist_created": True,
        "entry_point": ENTRY_POINT,
        "local_run_command": LOCAL_RUN_COMMAND,
        "github_repository_required": True,
        "private_repository_recommended_for_beta": True,
        "requirements_file_required": True,
        "secrets_must_not_be_committed": True,
        "hosted_smoke_test_required_after_deploy": True,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "historical_data_is_scenario_input_not_forecast": True,
        "checklist_rows": int(len(checklist_df)),
        "required_steps": required_count,
        "row_count": int(len(checklist_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Deployment Step 9 — Streamlit Cloud app setup",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Entry point: {ENTRY_POINT}",
        f"Local run command: {LOCAL_RUN_COMMAND}",
        f"Checklist rows: {summary['checklist_rows']}",
        f"Required steps: {summary['required_steps']}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_deployment_step_9_summary(), indent=2))
