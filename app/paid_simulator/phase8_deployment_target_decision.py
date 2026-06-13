"""
phase8_deployment_target_decision.py

Phase 8-2 deployment target decision.

This module is passive. It compares realistic deployment targets for the paid
Covered Call Simulator and produces a decision table for the next implementation
step.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

TARGETS_CSV = OUTPUT_TABLE_DIR / "phase8_2_deployment_target_decision_targets.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase8_2_deployment_target_decision_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase8_2_deployment_target_decision.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase8_2_deployment_target_decision_report.txt"

READY_MARKER = "PHASE8_2_DEPLOYMENT_TARGET_DECISION_READY"
RELEASE_DECISION = "PHASE8_2_DEPLOYMENT_TARGET_DECISION_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "deployment_target_decision"

RECOMMENDED_TARGET = "Streamlit Community Cloud or Streamlit-compatible paid hosting for MVP"
SECONDARY_TARGET = "Full web app later if subscription/payment integration requires it"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_phase8_2_targets() -> list[dict[str, Any]]:
    return [
        {
            "target": "Streamlit Community Cloud",
            "fit_for_current_app": "High",
            "setup_complexity": "Low",
            "cost_level": "Low",
            "customer_access": "Limited/simple sharing; may need external payment/access control",
            "advantages": "Fastest MVP path; matches current Streamlit dashboard",
            "risks": "Commercial access control and payments may need separate handling",
            "recommended_for_mvp": True,
        },
        {
            "target": "Streamlit-compatible paid hosting",
            "fit_for_current_app": "High",
            "setup_complexity": "Medium",
            "cost_level": "Medium",
            "customer_access": "Better private access options depending on provider",
            "advantages": "Keeps current code structure; more commercial flexibility",
            "risks": "Requires provider choice and environment configuration",
            "recommended_for_mvp": True,
        },
        {
            "target": "Python web app on cloud VM",
            "fit_for_current_app": "Medium",
            "setup_complexity": "High",
            "cost_level": "Medium",
            "customer_access": "Flexible, but must build authentication and deployment stack",
            "advantages": "More control over app, domain, and access",
            "risks": "More DevOps work and more places to break",
            "recommended_for_mvp": False,
        },
        {
            "target": "Full custom web app",
            "fit_for_current_app": "Medium",
            "setup_complexity": "High",
            "cost_level": "Medium/High",
            "customer_access": "Best long-term subscription/product path",
            "advantages": "Best product polish and payment integration",
            "risks": "Large rewrite; slower launch",
            "recommended_for_mvp": False,
        },
        {
            "target": "Local downloadable app",
            "fit_for_current_app": "Medium",
            "setup_complexity": "Medium",
            "cost_level": "Low",
            "customer_access": "Customer runs locally",
            "advantages": "Avoids hosting complexity",
            "risks": "Harder customer support; harder payment control; environment problems",
            "recommended_for_mvp": False,
        },
    ]


def build_phase8_2_summary() -> dict[str, Any]:
    _ensure_dirs()

    targets = build_phase8_2_targets()
    targets_df = pd.DataFrame(targets)
    targets_df.to_csv(TARGETS_CSV, index=False)

    recommended_count = int(targets_df["recommended_for_mvp"].sum())

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "deployment_target_decision_created": True,
        "recommended_target": RECOMMENDED_TARGET,
        "secondary_target": SECONDARY_TARGET,
        "recommended_for_mvp_count": recommended_count,
        "target_rows": int(len(targets_df)),
        "row_count": int(len(targets_df)),
        "streamlit_mvp_path_supported": True,
        "full_web_app_deferred": True,
        "payments_access_control_not_yet_implemented": True,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "historical_data_is_scenario_input_not_forecast": True,
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 8-2 deployment target decision",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Recommended MVP target: {RECOMMENDED_TARGET}",
        f"Secondary target: {SECONDARY_TARGET}",
        f"Recommended target count: {recommended_count}",
        f"Target rows: {len(targets_df)}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase8_2_summary(), indent=2))
