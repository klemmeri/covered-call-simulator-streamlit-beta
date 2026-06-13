"""
deployment_step_4_streamlit_cloud_deployment_checklist.py

Deployment Step 4 - Streamlit Cloud deployment checklist.

This module is passive. It creates a checklist for preparing the Covered Call
Simulator repository for a Streamlit-compatible hosted deployment.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

CHECKLIST_CSV = OUTPUT_TABLE_DIR / "deployment_step_4_streamlit_cloud_deployment_checklist.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "deployment_step_4_streamlit_cloud_deployment_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "deployment_step_4_streamlit_cloud_deployment_checklist.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "deployment_step_4_streamlit_cloud_deployment_checklist_report.txt"

READY_MARKER = "DEPLOYMENT_STEP_4_STREAMLIT_CLOUD_DEPLOYMENT_CHECKLIST_READY"
RELEASE_DECISION = "DEPLOYMENT_STEP_4_CHECKLIST_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "streamlit_cloud_deployment_checklist"
ENTRYPOINT = "app/paid_simulator/config_form_app.py"
RUN_COMMAND = "streamlit run app/paid_simulator/config_form_app.py"
CAUTION = "Historical data is scenario input, not forecast"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_deployment_step_4_checklist() -> list[dict[str, Any]]:
    return [
        {
            "item": "Git repository ready",
            "purpose": "Host platforms usually deploy from a Git repository.",
            "expected_state": "Project files committed except caches, outputs, secrets, and local backups.",
            "required_for_streamlit_cloud": True,
        },
        {
            "item": "Streamlit entry point selected",
            "purpose": "The hosted service needs the main app file.",
            "expected_state": ENTRYPOINT,
            "required_for_streamlit_cloud": True,
        },
        {
            "item": "requirements.txt present",
            "purpose": "The hosted service needs package dependencies.",
            "expected_state": "requirements.txt exists at project root.",
            "required_for_streamlit_cloud": True,
        },
        {
            "item": "Streamlit config present",
            "purpose": "Keep hosted behavior predictable.",
            "expected_state": ".streamlit/config.toml exists.",
            "required_for_streamlit_cloud": True,
        },
        {
            "item": "No secrets committed",
            "purpose": "Avoid exposing credentials or payment/deployment tokens.",
            "expected_state": "No API keys, tokens, passwords, or broker credentials in repository.",
            "required_for_streamlit_cloud": True,
        },
        {
            "item": "Sample data included",
            "purpose": "The app should run a basic demo without private data.",
            "expected_state": "inputs/market_data sample files are present or app handles missing files safely.",
            "required_for_streamlit_cloud": True,
        },
        {
            "item": "Synthetic default preserved",
            "purpose": "Hosted app should open in the safe default mode.",
            "expected_state": "Synthetic scenarios remain the default.",
            "required_for_streamlit_cloud": True,
        },
        {
            "item": "Historical opt-in preserved",
            "purpose": "Historical mode should not activate accidentally.",
            "expected_state": "Imported historical data remains explicit opt-in only.",
            "required_for_streamlit_cloud": True,
        },
        {
            "item": "Customer caution preserved",
            "purpose": "Historical-data interpretation must remain cautious.",
            "expected_state": CAUTION,
            "required_for_streamlit_cloud": True,
        },
        {
            "item": "Hosted smoke-test instructions ready",
            "purpose": "Deployment should be verified after publishing.",
            "expected_state": "Run the Step 5 hosted smoke-test checklist after deployment.",
            "required_for_streamlit_cloud": True,
        },
    ]


def build_deployment_step_4_summary() -> dict[str, Any]:
    _ensure_dirs()

    checklist = build_deployment_step_4_checklist()
    checklist_df = pd.DataFrame(checklist)
    checklist_df.to_csv(CHECKLIST_CSV, index=False)

    dashboard_file = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
    requirements_file = PROJECT_ROOT / "requirements.txt"
    streamlit_config = PROJECT_ROOT / ".streamlit" / "config.toml"

    dashboard_text = dashboard_file.read_text(encoding="utf-8") if dashboard_file.exists() else ""

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "streamlit_entrypoint": ENTRYPOINT,
        "local_run_command": RUN_COMMAND,
        "requirements_txt_exists": requirements_file.exists(),
        "streamlit_config_exists": streamlit_config.exists(),
        "dashboard_exists": dashboard_file.exists(),
        "synthetic_default_preserved": "Synthetic scenarios" in dashboard_text,
        "historical_mode_explicit_only": "Imported historical data" in dashboard_text,
        "historical_data_is_scenario_input_not_forecast": CAUTION in dashboard_text,
        "no_secrets_committed_required": True,
        "git_repository_required": True,
        "hosted_smoke_test_next": True,
        "checklist_rows": int(len(checklist_df)),
        "required_items": int(checklist_df["required_for_streamlit_cloud"].sum()),
        "row_count": int(len(checklist_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Deployment Step 4 - Streamlit Cloud deployment checklist",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Entrypoint: {ENTRYPOINT}",
        f"Run command: {RUN_COMMAND}",
        f"Checklist rows: {summary['checklist_rows']}",
        f"Required items: {summary['required_items']}",
        f"requirements.txt exists: {summary['requirements_txt_exists']}",
        f".streamlit/config.toml exists: {summary['streamlit_config_exists']}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_deployment_step_4_summary(), indent=2))
