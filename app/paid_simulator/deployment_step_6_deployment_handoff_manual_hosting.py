"""
deployment_step_6_deployment_handoff_manual_hosting.py

Deployment Step 6 deployment handoff and manual hosting instructions.

This module is passive. It creates a final deployment handoff checklist for the
Streamlit-compatible MVP deployment path.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

HANDOFF_CSV = OUTPUT_TABLE_DIR / "deployment_step_6_deployment_handoff_manual_hosting.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "deployment_step_6_deployment_handoff_manual_hosting_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "deployment_step_6_deployment_handoff_manual_hosting.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "deployment_step_6_deployment_handoff_manual_hosting_report.txt"

READY_MARKER = "DEPLOYMENT_STEP_6_HANDOFF_MANUAL_HOSTING_READY"
RELEASE_DECISION = "DEPLOYMENT_STEP_6_HANDOFF_MANUAL_HOSTING_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "deployment_handoff_manual_hosting"
ENTRY_POINT = "app/paid_simulator/config_form_app.py"
LOCAL_COMMAND = "streamlit run app/paid_simulator/config_form_app.py"
CAUTION = "Historical data is scenario input, not forecast"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_deployment_step_6_handoff() -> list[dict[str, Any]]:
    return [
        {
            "step": "Final local backup",
            "action": "Create a final ZIP backup of the project root before hosting work.",
            "expected_result": "A recoverable Google Drive backup exists.",
            "required": True,
        },
        {
            "step": "Repository readiness",
            "action": "Confirm the deployment branch contains app, docs, config, inputs, requirements.txt, and .streamlit/config.toml.",
            "expected_result": "The hosting repository has all needed files and no secrets.",
            "required": True,
        },
        {
            "step": "Streamlit entry point",
            "action": f"Use {ENTRY_POINT} as the hosted app entry point.",
            "expected_result": "Streamlit launches the paid simulator dashboard.",
            "required": True,
        },
        {
            "step": "Local launch command",
            "action": f"Run {LOCAL_COMMAND} before hosting changes.",
            "expected_result": "The local app opens successfully.",
            "required": True,
        },
        {
            "step": "Hosted launch",
            "action": "Deploy to the selected Streamlit-compatible host and open the hosted URL.",
            "expected_result": "The hosted app loads without import errors.",
            "required": True,
        },
        {
            "step": "Synthetic default check",
            "action": "Open the app without selecting historical mode.",
            "expected_result": "Synthetic scenarios remain the default workflow.",
            "required": True,
        },
        {
            "step": "Historical opt-in check",
            "action": "Select imported historical data explicitly.",
            "expected_result": "Historical mode is available only by explicit selection.",
            "required": True,
        },
        {
            "step": "Scenario caution check",
            "action": "Confirm historical-data caution wording remains visible.",
            "expected_result": CAUTION,
            "required": True,
        },
        {
            "step": "Customer access control",
            "action": "Confirm the selected beta/customer access method is active.",
            "expected_result": "Only intended users can access the hosted app.",
            "required": True,
        },
        {
            "step": "Post-hosting smoke test",
            "action": "Run one default scenario and review outputs, charts, tables, and wording.",
            "expected_result": "The hosted workflow is customer-test ready.",
            "required": True,
        },
    ]


def build_deployment_step_6_summary() -> dict[str, Any]:
    _ensure_dirs()

    handoff = build_deployment_step_6_handoff()
    handoff_df = pd.DataFrame(handoff)
    handoff_df.to_csv(HANDOFF_CSV, index=False)

    required_count = int(handoff_df["required"].sum())

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "deployment_handoff_created": True,
        "streamlit_entry_point": ENTRY_POINT,
        "local_streamlit_command": LOCAL_COMMAND,
        "streamlit_mvp_path_supported": True,
        "customer_access_control_required": True,
        "hosted_smoke_test_required": True,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "unknown_modes_fall_back_to_synthetic": True,
        "historical_data_is_scenario_input_not_forecast": True,
        "handoff_rows": int(len(handoff_df)),
        "required_handoff_steps": required_count,
        "row_count": int(len(handoff_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Deployment Step 6 handoff and manual hosting instructions",
        "=" * 76,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Streamlit entry point: {ENTRY_POINT}",
        f"Local command: {LOCAL_COMMAND}",
        f"Handoff rows: {summary['handoff_rows']}",
        f"Required handoff steps: {summary['required_handoff_steps']}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_deployment_step_6_summary(), indent=2))
