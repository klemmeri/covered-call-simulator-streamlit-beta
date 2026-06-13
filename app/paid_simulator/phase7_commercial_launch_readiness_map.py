"""
phase7_commercial_launch_readiness_map.py

Phase 7-1 commercial launch-readiness map for the Covered Call Simulator.

This module is passive and add-only. It does not patch the dashboard or engine.
It defines the commercial launch-readiness categories for Phase 7.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase7_1_commercial_launch_readiness_map_summary.csv"
READINESS_CSV = OUTPUT_TABLE_DIR / "phase7_1_commercial_launch_readiness_map.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase7_1_commercial_launch_readiness_map.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase7_1_commercial_launch_readiness_map_report.txt"

READY_MARKER = "PHASE7_1_COMMERCIAL_LAUNCH_READINESS_MAP_READY"
RELEASE_DECISION = "PHASE7_1_COMMERCIAL_LAUNCH_READINESS_MAP_CREATED_NO_DASHBOARD_CHANGE"
SOURCE_MODE = "commercial_launch_readiness_map"
CAUTION = "Historical data is scenario input, not forecast"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_phase7_1_readiness_rows() -> list[dict[str, Any]]:
    """Return the Phase 7 commercial launch-readiness checklist."""
    return [
        {
            "phase7_step": "7-1",
            "category": "Launch-readiness map",
            "goal": "Define the customer-facing readiness checklist for the paid simulator.",
            "status": "current_checkpoint",
            "dashboard_change_required": False,
            "risk_control": "No dashboard or engine change in this checkpoint.",
        },
        {
            "phase7_step": "7-2",
            "category": "Customer wording and disclaimer audit",
            "goal": "Audit wording so the simulator is clearly educational/scenario-based and not financial advice.",
            "status": "planned",
            "dashboard_change_required": False,
            "risk_control": CAUTION,
        },
        {
            "phase7_step": "7-3",
            "category": "Dashboard layout polish",
            "goal": "Improve customer readability, section order, and labels without changing calculations.",
            "status": "planned",
            "dashboard_change_required": True,
            "risk_control": "Patch only layout/wording; preserve synthetic default and historical opt-in behavior.",
        },
        {
            "phase7_step": "7-4",
            "category": "Report export polish",
            "goal": "Make exported reports easier for customers to save, read, and compare.",
            "status": "planned",
            "dashboard_change_required": False,
            "risk_control": "Report-only changes; no strategy logic change.",
        },
        {
            "phase7_step": "7-5",
            "category": "Website integration plan",
            "goal": "Define how the paid simulator connects to the commercial website/customer journey.",
            "status": "planned",
            "dashboard_change_required": False,
            "risk_control": "Planning only; no deployment assumptions.",
        },
        {
            "phase7_step": "7-6",
            "category": "Phase 7 completion handoff",
            "goal": "Confirm commercial polish readiness and define the next launch/deployment phase.",
            "status": "planned",
            "dashboard_change_required": False,
            "risk_control": "Close Phase 7 only after regression checks pass.",
        },
    ]


def build_phase7_1_summary() -> dict[str, Any]:
    """Build and write the Phase 7-1 launch-readiness map outputs."""
    _ensure_dirs()

    rows = build_phase7_1_readiness_rows()
    readiness_df = pd.DataFrame(rows)
    readiness_df.to_csv(READINESS_CSV, index=False)

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "phase": "Phase 7",
        "checkpoint": "Phase 7-1",
        "dashboard_change_required": False,
        "dashboard_changed": False,
        "engine_change_required": False,
        "engine_changed": False,
        "commercial_launch_readiness_map_created": True,
        "phase7_steps_planned": int(len(readiness_df)),
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "unknown_modes_fall_back_to_synthetic": True,
        "historical_data_is_scenario_input_not_forecast": True,
        "scenario_input_not_forecast": True,
        "customer_education_not_advice_framing_required": True,
        "row_count": int(len(readiness_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 7-1 commercial launch-readiness map",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Phase 7 steps planned: {summary['phase7_steps_planned']}",
        f"Dashboard changed: {summary['dashboard_changed']}",
        f"Engine changed: {summary['engine_changed']}",
        f"Synthetic default preserved: {summary['synthetic_default_preserved']}",
        f"Historical mode explicit only: {summary['historical_mode_explicit_only']}",
        f"{CAUTION}: {summary['historical_data_is_scenario_input_not_forecast']}",
        "",
        "Planned Phase 7 checkpoints:",
    ]
    for row in rows:
        report.append(f"- Phase {row['phase7_step']}: {row['category']}")

    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase7_1_summary(), indent=2))
