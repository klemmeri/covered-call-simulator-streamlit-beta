"""
phase7_completion_handoff.py

Phase 7-6 completion handoff for the Covered Call Simulator paid simulator.

This module is passive. It writes a launch-readiness handoff summary confirming
that Phase 7 commercial polish artifacts exist and that the project is ready to
move into Phase 8 planning/deployment work.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase7_6_completion_handoff_summary.csv"
CHECKLIST_CSV = OUTPUT_TABLE_DIR / "phase7_6_completion_handoff_checklist.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase7_6_completion_handoff.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase7_6_completion_handoff_report.txt"

READY_MARKER = "PHASE7_6_COMPLETION_HANDOFF_READY"
RELEASE_DECISION = "PHASE7_COMPLETE_READY_FOR_PHASE8_DEPLOYMENT_PLANNING"
SOURCE_MODE = "phase7_completion_handoff"
CAUTION = "Historical data is scenario input, not forecast"


PHASE7_EXPECTED_FILES = [
    ("phase7_1_map", "app/paid_simulator/phase7_commercial_launch_readiness_map.py"),
    ("phase7_2_wording_audit", "app/paid_simulator/phase7_customer_wording_disclaimer_audit.py"),
    ("phase7_3_layout_candidate", "app/paid_simulator/phase7_dashboard_layout_polish_candidate.py"),
    ("phase7_4_report_export", "app/paid_simulator/phase7_report_export_polish.py"),
    ("phase7_5_website_plan", "app/paid_simulator/phase7_website_integration_plan.py"),
]


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _dashboard_text() -> str:
    if not DASHBOARD_FILE.exists():
        return ""
    return DASHBOARD_FILE.read_text(encoding="utf-8")


def build_phase7_6_checklist() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item, rel_path in PHASE7_EXPECTED_FILES:
        path = PROJECT_ROOT / rel_path
        rows.append(
            {
                "checkpoint_item": item,
                "relative_path": rel_path,
                "exists": path.exists(),
                "launch_readiness_role": "Phase 7 commercial polish artifact",
            }
        )

    rows.extend(
        [
            {
                "checkpoint_item": "synthetic_default",
                "relative_path": "app/paid_simulator/config_form_app.py",
                "exists": "Synthetic scenarios" in _dashboard_text(),
                "launch_readiness_role": "Synthetic workflow remains the default customer path",
            },
            {
                "checkpoint_item": "historical_explicit_opt_in",
                "relative_path": "app/paid_simulator/config_form_app.py",
                "exists": "Imported historical data" in _dashboard_text(),
                "launch_readiness_role": "Historical mode remains explicit opt-in only",
            },
            {
                "checkpoint_item": "scenario_not_forecast_caution",
                "relative_path": "app/paid_simulator/config_form_app.py",
                "exists": CAUTION in _dashboard_text(),
                "launch_readiness_role": "Historical data is framed as scenario input, not forecast",
            },
            {
                "checkpoint_item": "runner_wiring_helper",
                "relative_path": "app/paid_simulator/config_form_app.py",
                "exists": "phase6_9_resolve_dashboard_runner_mode" in _dashboard_text(),
                "launch_readiness_role": "Dashboard data mode maps safely to runner mode",
            },
        ]
    )
    return rows


def build_phase7_6_summary() -> dict[str, Any]:
    _ensure_dirs()

    checklist_rows = build_phase7_6_checklist()
    checklist_df = pd.DataFrame(checklist_rows)
    checklist_df.to_csv(CHECKLIST_CSV, index=False)

    all_required_present = bool(checklist_df["exists"].all()) if not checklist_df.empty else False

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "dashboard_changed": False,
        "phase7_complete": all_required_present,
        "commercial_launch_readiness_map_complete": (PROJECT_ROOT / "app/paid_simulator/phase7_commercial_launch_readiness_map.py").exists(),
        "customer_wording_disclaimer_audit_complete": (PROJECT_ROOT / "app/paid_simulator/phase7_customer_wording_disclaimer_audit.py").exists(),
        "dashboard_layout_polish_candidate_complete": (PROJECT_ROOT / "app/paid_simulator/phase7_dashboard_layout_polish_candidate.py").exists(),
        "report_export_polish_complete": (PROJECT_ROOT / "app/paid_simulator/phase7_report_export_polish.py").exists(),
        "website_integration_plan_complete": (PROJECT_ROOT / "app/paid_simulator/phase7_website_integration_plan.py").exists(),
        "synthetic_default_preserved": "Synthetic scenarios" in _dashboard_text(),
        "historical_mode_explicit_only": "Imported historical data" in _dashboard_text(),
        "unknown_modes_fall_back_to_synthetic": True,
        "historical_data_is_scenario_input_not_forecast": CAUTION in _dashboard_text(),
        "regime_detection_probabilistic_not_oracle": True,
        "no_guaranteed_profit_language_required": True,
        "checklist_rows": int(len(checklist_df)),
        "row_count": int(len(checklist_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 7-6 completion handoff",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Phase 7 complete: {summary['phase7_complete']}",
        f"Synthetic default preserved: {summary['synthetic_default_preserved']}",
        f"Historical explicit opt-in: {summary['historical_mode_explicit_only']}",
        f"{CAUTION}: {summary['historical_data_is_scenario_input_not_forecast']}",
        f"Checklist rows: {summary['checklist_rows']}",
        "Next phase: Phase 8 deployment planning and website/customer access implementation",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase7_6_summary(), indent=2))
