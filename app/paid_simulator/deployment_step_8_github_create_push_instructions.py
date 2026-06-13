"""
deployment_step_8_github_create_push_instructions.py

Deployment Step 8: GitHub create/push instructions.

This module is passive. It creates a checklist for creating or updating the
GitHub repository used by Streamlit Cloud. It does not modify dashboard or
engine code.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

CHECKLIST_CSV = OUTPUT_TABLE_DIR / "deployment_step_8_github_create_push_instructions.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "deployment_step_8_github_create_push_instructions_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "deployment_step_8_github_create_push_instructions.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "deployment_step_8_github_create_push_instructions_report.txt"

READY_MARKER = "DEPLOYMENT_STEP_8_GITHUB_CREATE_PUSH_INSTRUCTIONS_READY"
RELEASE_DECISION = "DEPLOYMENT_STEP_8_GITHUB_INSTRUCTIONS_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "github_create_push_instructions"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_deployment_step_8_checklist() -> list[dict[str, Any]]:
    return [
        {
            "step": 1,
            "task": "Confirm final local backup exists",
            "detail": "Create or confirm CoveredCallSimulator_Phase10_Complete_v1_0_0_YYYY-MM-DD.zip before pushing.",
            "required": True,
        },
        {
            "step": 2,
            "task": "Create GitHub repository",
            "detail": "Use a private repository first unless you intentionally want public source visibility.",
            "required": True,
        },
        {
            "step": 3,
            "task": "Initialize git in project root if needed",
            "detail": "Run git init from C:\\Users\\ctran\\OneDrive\\Documents\\Coveredcallsimulator only if the folder is not already a repository.",
            "required": True,
        },
        {
            "step": 4,
            "task": "Add safe project files",
            "detail": "Include app, config, docs, inputs/sample data, requirements.txt, and .streamlit/config.toml.",
            "required": True,
        },
        {
            "step": 5,
            "task": "Exclude generated or private files",
            "detail": "Do not commit secrets, credentials, tokens, local caches, __pycache__, or unnecessary generated outputs.",
            "required": True,
        },
        {
            "step": 6,
            "task": "Commit release candidate",
            "detail": "Suggested message: v1.0.0-rc1 Streamlit MVP release candidate.",
            "required": True,
        },
        {
            "step": 7,
            "task": "Push to GitHub",
            "detail": "Push main branch to the GitHub repository that Streamlit Cloud will read.",
            "required": True,
        },
        {
            "step": 8,
            "task": "Use Streamlit entry point",
            "detail": "Streamlit app file: app/paid_simulator/config_form_app.py",
            "required": True,
        },
    ]


def build_deployment_step_8_summary() -> dict[str, Any]:
    _ensure_dirs()

    checklist = build_deployment_step_8_checklist()
    checklist_df = pd.DataFrame(checklist)
    checklist_df.to_csv(CHECKLIST_CSV, index=False)

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "github_create_push_instructions_created": True,
        "private_repository_recommended_first": True,
        "streamlit_entrypoint": "app/paid_simulator/config_form_app.py",
        "release_candidate_version": "v1.0.0-rc1",
        "final_backup_recommended_before_push": True,
        "secrets_exclusion_required": True,
        "checklist_rows": int(len(checklist_df)),
        "required_rows": int(checklist_df["required"].sum()),
        "row_count": int(len(checklist_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Deployment Step 8 - GitHub create/push instructions",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Streamlit entry point: {summary['streamlit_entrypoint']}",
        f"Release candidate version: {summary['release_candidate_version']}",
        f"Checklist rows: {summary['checklist_rows']}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_deployment_step_8_summary(), indent=2))
