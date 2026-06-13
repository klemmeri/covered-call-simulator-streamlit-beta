"""
phase8_deployment_customer_access_roadmap.py

Phase 8-1 deployment and customer-access roadmap.

This module is passive. It makes no dashboard or engine change. It defines a
finite Phase 8 roadmap for turning the local paid simulator into a deployed
customer-access product.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

ROADMAP_CSV = OUTPUT_TABLE_DIR / "phase8_1_deployment_customer_access_roadmap.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase8_1_deployment_customer_access_roadmap_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase8_1_deployment_customer_access_roadmap.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase8_1_deployment_customer_access_roadmap_report.txt"

READY_MARKER = "PHASE8_1_DEPLOYMENT_CUSTOMER_ACCESS_ROADMAP_READY"
RELEASE_DECISION = "PHASE8_1_DEPLOYMENT_CUSTOMER_ACCESS_ROADMAP_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "deployment_customer_access_roadmap"
CAUTION = "Historical data is scenario input, not forecast"
REGIME_WORDING = "Regime detection is probabilistic guidance, not an oracle"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_phase8_1_roadmap_rows() -> list[dict[str, Any]]:
    return [
        {
            "phase": "Phase 8-1",
            "checkpoint": "Deployment and customer-access roadmap",
            "purpose": "Define the deployment sequence before changing infrastructure.",
            "change_type": "add_only",
            "required_for_launch": True,
        },
        {
            "phase": "Phase 8-2",
            "checkpoint": "Deployment target decision",
            "purpose": "Choose the initial hosting path for the paid simulator.",
            "change_type": "planning",
            "required_for_launch": True,
        },
        {
            "phase": "Phase 8-3",
            "checkpoint": "Environment and dependency audit",
            "purpose": "Confirm Python, package, data, output, and Streamlit requirements.",
            "change_type": "audit",
            "required_for_launch": True,
        },
        {
            "phase": "Phase 8-4",
            "checkpoint": "Customer access model",
            "purpose": "Define access control, payment linkage, and customer workflow boundaries.",
            "change_type": "planning",
            "required_for_launch": True,
        },
        {
            "phase": "Phase 8-5",
            "checkpoint": "Hosted smoke-test plan",
            "purpose": "Define a controlled test before public/customer access.",
            "change_type": "test_plan",
            "required_for_launch": True,
        },
        {
            "phase": "Phase 8-6",
            "checkpoint": "Deployment completion handoff",
            "purpose": "Close Phase 8 and confirm readiness for implementation work.",
            "change_type": "handoff",
            "required_for_launch": True,
        },
    ]


def build_phase8_1_summary() -> dict[str, Any]:
    _ensure_dirs()

    roadmap_df = pd.DataFrame(build_phase8_1_roadmap_rows())
    roadmap_df.to_csv(ROADMAP_CSV, index=False)

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "roadmap_created": True,
        "phase8_finite_plan_created": True,
        "planned_phase8_checkpoints": int(len(roadmap_df)),
        "row_count": int(len(roadmap_df)),
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "historical_data_is_scenario_input_not_forecast": True,
        "regime_detection_probabilistic_not_oracle": True,
        "customer_access_planning_started": True,
        "deployment_planning_started": True,
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report_lines = [
        "Phase 8-1 deployment and customer-access roadmap",
        "=" * 76,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Planned Phase 8 checkpoints: {summary['planned_phase8_checkpoints']}",
        f"Synthetic default preserved: {summary['synthetic_default_preserved']}",
        f"Historical explicit opt-in only: {summary['historical_mode_explicit_only']}",
        f"{CAUTION}: {summary['historical_data_is_scenario_input_not_forecast']}",
        f"{REGIME_WORDING}: {summary['regime_detection_probabilistic_not_oracle']}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase8_1_summary(), indent=2))
