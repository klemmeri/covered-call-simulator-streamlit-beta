"""
phase10_final_release_maintenance_roadmap.py

Phase 10-1 final release package and maintenance roadmap.

This module is passive. It defines the final phase roadmap for converting the
Covered Call Simulator from beta-ready to release-ready, including packaging,
versioning, backup, and maintenance controls.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

ROADMAP_CSV = OUTPUT_TABLE_DIR / "phase10_1_final_release_maintenance_roadmap.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase10_1_final_release_maintenance_roadmap_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase10_1_final_release_maintenance_roadmap.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase10_1_final_release_maintenance_roadmap_report.txt"

READY_MARKER = "PHASE10_1_FINAL_RELEASE_MAINTENANCE_ROADMAP_READY"
RELEASE_DECISION = "PHASE10_1_FINAL_RELEASE_MAINTENANCE_ROADMAP_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "final_release_maintenance_roadmap"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_phase10_1_roadmap() -> list[dict[str, Any]]:
    return [
        {
            "phase_step": "Phase 10-1",
            "title": "Final release and maintenance roadmap",
            "purpose": "Define final release sequence and keep Phase 10 finite.",
            "required_for_release": True,
        },
        {
            "phase_step": "Phase 10-2",
            "title": "Release package manifest",
            "purpose": "List required app files, docs, inputs, outputs, and backup artifacts.",
            "required_for_release": True,
        },
        {
            "phase_step": "Phase 10-3",
            "title": "Version and backup policy",
            "purpose": "Define naming, zip backup, Google Drive backup, and restore expectations.",
            "required_for_release": True,
        },
        {
            "phase_step": "Phase 10-4",
            "title": "Maintenance and issue-log template",
            "purpose": "Create a lightweight process for bug reports, fixes, releases, and future enhancements.",
            "required_for_release": True,
        },
        {
            "phase_step": "Phase 10-5",
            "title": "Final release candidate smoke test",
            "purpose": "Verify local app, synthetic default, historical opt-in, reports, and disclaimers before release.",
            "required_for_release": True,
        },
        {
            "phase_step": "Phase 10-6",
            "title": "Phase 10 completion handoff",
            "purpose": "Close the build sequence and identify post-release maintenance only.",
            "required_for_release": True,
        },
    ]


def build_phase10_1_summary() -> dict[str, Any]:
    _ensure_dirs()

    roadmap = build_phase10_1_roadmap()
    roadmap_df = pd.DataFrame(roadmap)
    roadmap_df.to_csv(ROADMAP_CSV, index=False)

    required_count = int(roadmap_df["required_for_release"].sum())

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "final_phase_started": True,
        "phase_10_is_final_build_phase": True,
        "post_phase_10_scope": "maintenance only unless a new product requirement is approved",
        "planned_phase10_steps": int(len(roadmap_df)),
        "required_release_steps": required_count,
        "release_package_manifest_planned": True,
        "version_backup_policy_planned": True,
        "maintenance_issue_log_planned": True,
        "final_release_candidate_smoke_test_planned": True,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "historical_data_is_scenario_input_not_forecast": True,
        "regime_detection_probabilistic_not_oracle": True,
        "row_count": int(len(roadmap_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 10-1 final release and maintenance roadmap",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Planned Phase 10 steps: {summary['planned_phase10_steps']}",
        f"Required release steps: {summary['required_release_steps']}",
        "Phase 10 is the final build phase: True",
        "Post Phase 10 scope: maintenance only unless a new product requirement is approved",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase10_1_summary(), indent=2))
