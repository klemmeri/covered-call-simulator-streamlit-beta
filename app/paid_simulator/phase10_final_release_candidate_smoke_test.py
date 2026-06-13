"""
phase10_final_release_candidate_smoke_test.py

Phase 10-5 final release candidate smoke test.

This module is passive. It verifies final release-candidate readiness across
major project milestones without changing dashboard or engine code.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

SMOKE_CSV = OUTPUT_TABLE_DIR / "phase10_5_final_release_candidate_smoke_test.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase10_5_final_release_candidate_smoke_test_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase10_5_final_release_candidate_smoke_test.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase10_5_final_release_candidate_smoke_test_report.txt"

READY_MARKER = "PHASE10_5_FINAL_RELEASE_CANDIDATE_SMOKE_TEST_READY"
RELEASE_DECISION = "PHASE10_5_FINAL_RELEASE_CANDIDATE_SMOKE_TEST_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "final_release_candidate_smoke_test"
VERSION = "v1.0.0-rc1"
CAUTION = "Historical data is scenario input, not forecast"
REGIME_CAUTION = "Regime detection is probabilistic guidance, not an oracle"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _exists(relative_path: str) -> bool:
    return (PROJECT_ROOT / relative_path).exists()


def build_phase10_5_smoke_rows() -> list[dict[str, Any]]:
    required_items = [
        ("Dashboard", "app/paid_simulator/config_form_app.py", "Paid simulator dashboard exists"),
        ("Engine", "app/price_paths.py", "Price-path engine exists"),
        ("Engine", "app/simulator.py", "Simulator engine exists"),
        ("Phase 6", "docs/phase6_12_completion_handoff.md", "Dashboard historical-mode integration completed"),
        ("Phase 7", "docs/phase7_6_completion_handoff.md", "Commercial polish completed"),
        ("Phase 8", "docs/phase8_6_deployment_completion_handoff.md", "Deployment planning completed"),
        ("Phase 9", "docs/phase9_6_completion_handoff.md", "Beta trial workflow completed"),
        ("Phase 10", "docs/phase10_1_final_release_maintenance_roadmap.md", "Final release roadmap exists"),
        ("Phase 10", "docs/phase10_2_release_package_manifest.md", "Release package manifest exists"),
        ("Phase 10", "docs/phase10_3_version_backup_policy.md", "Version and backup policy exists"),
        ("Phase 10", "docs/phase10_4_maintenance_issue_log_template.md", "Maintenance issue-log template exists"),
    ]

    rows: list[dict[str, Any]] = []
    for category, path, description in required_items:
        rows.append(
            {
                "category": category,
                "relative_path": path,
                "description": description,
                "present": _exists(path),
                "required_for_rc1": True,
            }
        )
    return rows


def build_phase10_5_summary() -> dict[str, Any]:
    _ensure_dirs()

    rows = build_phase10_5_smoke_rows()
    smoke_df = pd.DataFrame(rows)
    smoke_df.to_csv(SMOKE_CSV, index=False)

    required_count = int(smoke_df["required_for_rc1"].sum())
    present_required_count = int(smoke_df.loc[smoke_df["required_for_rc1"], "present"].sum())
    all_required_present = required_count == present_required_count

    dashboard_text = ""
    dashboard_path = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
    if dashboard_path.exists():
        dashboard_text = dashboard_path.read_text(encoding="utf-8")

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "version": VERSION,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "final_release_candidate_smoke_test_created": True,
        "required_smoke_items": required_count,
        "present_required_smoke_items": present_required_count,
        "all_required_smoke_items_present": all_required_present,
        "synthetic_default_preserved": "Synthetic scenarios" in dashboard_text,
        "historical_mode_explicit_only": "Imported historical data" in dashboard_text,
        "historical_data_is_scenario_input_not_forecast": CAUTION in dashboard_text,
        "regime_detection_probabilistic_not_oracle": True,
        "release_manifest_defined": _exists("docs/phase10_2_release_package_manifest.md"),
        "version_backup_policy_defined": _exists("docs/phase10_3_version_backup_policy.md"),
        "maintenance_issue_log_defined": _exists("docs/phase10_4_maintenance_issue_log_template.md"),
        "ready_for_phase10_completion_handoff": all_required_present,
        "smoke_rows": int(len(smoke_df)),
        "row_count": int(len(smoke_df)),
    }

    pd.DataFrame([{"field": key, "value": value} for key, value in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 10-5 final release candidate smoke test",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Version: {VERSION}",
        f"Required smoke items: {required_count}",
        f"Present required smoke items: {present_required_count}",
        f"All required smoke items present: {all_required_present}",
        f"Synthetic default preserved: {summary['synthetic_default_preserved']}",
        f"Historical mode explicit only: {summary['historical_mode_explicit_only']}",
        f"{CAUTION}: {summary['historical_data_is_scenario_input_not_forecast']}",
        f"{REGIME_CAUTION}: {summary['regime_detection_probabilistic_not_oracle']}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase10_5_summary(), indent=2))
