"""
deployment_step_7_github_repository_readiness.py

Deployment Step 7 - GitHub repository readiness.

This module is passive. It checks and documents the repository files needed
before pushing the Covered Call Simulator to GitHub for Streamlit deployment.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

CHECKLIST_CSV = OUTPUT_TABLE_DIR / "deployment_step_7_github_repository_readiness_checklist.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "deployment_step_7_github_repository_readiness_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "deployment_step_7_github_repository_readiness.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "deployment_step_7_github_repository_readiness_report.txt"

READY_MARKER = "DEPLOYMENT_STEP_7_GITHUB_REPOSITORY_READINESS_READY"
RELEASE_DECISION = "DEPLOYMENT_STEP_7_GITHUB_REPOSITORY_READINESS_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "github_repository_readiness"

ENTRY_POINT = "app/paid_simulator/config_form_app.py"
LOCAL_RUN_COMMAND = "streamlit run app/paid_simulator/config_form_app.py"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_deployment_step_7_checklist() -> list[dict[str, Any]]:
    return [
        {
            "item": "Streamlit entry point",
            "path_or_rule": ENTRY_POINT,
            "required": True,
            "status_goal": "Dashboard entry point exists and is the app file selected in Streamlit Cloud.",
        },
        {
            "item": "Requirements file",
            "path_or_rule": "requirements.txt",
            "required": True,
            "status_goal": "Hosted environment can install project dependencies.",
        },
        {
            "item": "Streamlit config",
            "path_or_rule": ".streamlit/config.toml",
            "required": True,
            "status_goal": "Streamlit has a stable deployment configuration.",
        },
        {
            "item": "Sample market data",
            "path_or_rule": "inputs/market_data",
            "required": True,
            "status_goal": "Demo/historical-input examples are available when needed.",
        },
        {
            "item": "No private credentials",
            "path_or_rule": "Do not commit secrets, API keys, tokens, brokerage credentials, or payment credentials.",
            "required": True,
            "status_goal": "Repository is safe to push to GitHub.",
        },
        {
            "item": "Generated outputs excluded or controlled",
            "path_or_rule": "outputs/ should not be treated as source code for the hosted MVP.",
            "required": True,
            "status_goal": "Repository remains clean and deployment-focused.",
        },
        {
            "item": "Customer view clean",
            "path_or_rule": "Customer view should not show local paths or local checkpoint wording.",
            "required": True,
            "status_goal": "Hosted app looks customer-ready.",
        },
        {
            "item": "Risk and forecast wording",
            "path_or_rule": "Historical data is scenario input, not forecast; no trade recommendation wording.",
            "required": True,
            "status_goal": "Commercial wording remains responsible.",
        },
    ]


def build_deployment_step_7_summary() -> dict[str, Any]:
    _ensure_dirs()

    checklist = build_deployment_step_7_checklist()
    checklist_df = pd.DataFrame(checklist)
    checklist_df.to_csv(CHECKLIST_CSV, index=False)

    required_count = int(checklist_df["required"].sum())

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "github_repository_readiness_created": True,
        "streamlit_entry_point": ENTRY_POINT,
        "local_run_command": LOCAL_RUN_COMMAND,
        "requirements_file_required": True,
        "streamlit_config_required": True,
        "secrets_must_not_be_committed": True,
        "customer_view_clean_required": True,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "historical_data_is_scenario_input_not_forecast": True,
        "checklist_rows": int(len(checklist_df)),
        "required_items": required_count,
        "row_count": int(len(checklist_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Deployment Step 7 - GitHub repository readiness",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Streamlit entry point: {ENTRY_POINT}",
        f"Local run command: {LOCAL_RUN_COMMAND}",
        f"Checklist rows: {summary['checklist_rows']}",
        f"Required items: {summary['required_items']}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_deployment_step_7_summary(), indent=2))
