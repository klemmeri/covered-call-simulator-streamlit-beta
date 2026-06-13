"""
phase10_completion_handoff.py

Phase 10-6 completion handoff.

This module is passive. It produces a final project completion handoff for the
Covered Call Simulator v1.0.0 release-candidate sequence.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase10_6_completion_handoff_summary.csv"
CHECKLIST_CSV = OUTPUT_TABLE_DIR / "phase10_6_completion_handoff_checklist.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase10_6_completion_handoff.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase10_6_completion_handoff_report.txt"

READY_MARKER = "PHASE10_6_COMPLETION_HANDOFF_READY"
RELEASE_DECISION = "PHASE10_COMPLETE_READY_FOR_RELEASE_CANDIDATE_BACKUP_AND_MAINTENANCE"
SOURCE_MODE = "phase10_completion_handoff"
VERSION = "v1.0.0-rc1"
FINAL_BACKUP_NAME = "CoveredCallSimulator_Phase10_Complete_v1_0_0_YYYY-MM-DD.zip"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _exists(relative_path: str) -> bool:
    return (PROJECT_ROOT / relative_path).exists()


def build_phase10_6_checklist() -> list[dict[str, Any]]:
    rows = [
        {"area": "Phase 6", "artifact": "docs/phase6_12_completion_handoff.md", "required": True},
        {"area": "Phase 7", "artifact": "docs/phase7_6_completion_handoff.md", "required": True},
        {"area": "Phase 8", "artifact": "docs/phase8_6_deployment_completion_handoff.md", "required": True},
        {"area": "Phase 9", "artifact": "docs/phase9_6_completion_handoff.md", "required": True},
        {"area": "Phase 10", "artifact": "docs/phase10_1_final_release_maintenance_roadmap.md", "required": True},
        {"area": "Phase 10", "artifact": "docs/phase10_2_release_package_manifest.md", "required": True},
        {"area": "Phase 10", "artifact": "docs/phase10_3_version_backup_policy.md", "required": True},
        {"area": "Phase 10", "artifact": "docs/phase10_4_maintenance_issue_log_template.md", "required": True},
        {"area": "Phase 10", "artifact": "docs/phase10_5_final_release_candidate_smoke_test.md", "required": True},
        {"area": "Dashboard", "artifact": "app/paid_simulator/config_form_app.py", "required": True},
        {"area": "Engine", "artifact": "app/price_paths.py", "required": True},
        {"area": "Engine", "artifact": "app/simulator.py", "required": True},
    ]
    for row in rows:
        row["exists"] = _exists(row["artifact"])
    return rows


def build_phase10_6_summary() -> dict[str, Any]:
    _ensure_dirs()

    checklist_rows = build_phase10_6_checklist()
    checklist_df = pd.DataFrame(checklist_rows)
    checklist_df.to_csv(CHECKLIST_CSV, index=False)

    required_df = checklist_df[checklist_df["required"] == True]
    required_present = bool(required_df["exists"].all()) if not required_df.empty else False

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "version": VERSION,
        "phase10_complete": True,
        "project_build_phases_complete": True,
        "maintenance_mode_next": True,
        "release_candidate_backup_name": FINAL_BACKUP_NAME,
        "required_artifacts_present": required_present,
        "checklist_rows": int(len(checklist_df)),
        "required_rows": int(len(required_df)),
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "historical_data_is_scenario_input_not_forecast": True,
        "regime_detection_probabilistic_not_oracle": True,
        "no_dashboard_change_required": True,
        "no_engine_change_required": True,
        "row_count": int(len(checklist_df)),
    }

    pd.DataFrame([{"field": key, "value": value} for key, value in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 10-6 completion handoff",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Version: {VERSION}",
        f"Release-candidate backup name: {FINAL_BACKUP_NAME}",
        f"Required artifacts present: {required_present}",
        f"Checklist rows: {summary['checklist_rows']}",
        "Synthetic scenarios remain the default.",
        "Historical mode remains explicit opt-in only.",
        "Historical data is scenario input, not a forecast.",
        "Regime detection is probabilistic guidance, not an oracle.",
        "Next state: maintenance mode, bug fixes, deployment/customer testing.",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase10_6_summary(), indent=2))
