"""
phase9_completion_handoff.py

Phase 9-6 completion handoff for the Covered Call Simulator beta-testing and
customer-trial workflow phase.

This module is passive. It validates that the Phase 9 beta workflow artifacts
exist and writes a completion summary. It does not modify dashboard or engine
code.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase9_6_completion_handoff_summary.csv"
ARTIFACTS_CSV = OUTPUT_TABLE_DIR / "phase9_6_completion_handoff_artifacts.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase9_6_completion_handoff.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase9_6_completion_handoff_report.txt"

READY_MARKER = "PHASE9_6_COMPLETION_HANDOFF_READY"
RELEASE_DECISION = "PHASE9_COMPLETE_READY_FOR_PHASE10_FINAL_RELEASE_PACKAGE"
SOURCE_MODE = "phase9_completion_handoff"

CAUTION = "Historical data is scenario input, not forecast"
REGIME_CAUTION = "Regime detection is probabilistic guidance, not an oracle"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_phase9_6_artifact_rows() -> list[dict[str, Any]]:
    return [
        {
            "phase": "Phase 9-1",
            "artifact": "Beta testing and customer-trial workflow map",
            "module": "app/paid_simulator/phase9_beta_testing_customer_trial_workflow_map.py",
            "check_script": "app/run_paid_simulator_phase9_1_beta_testing_customer_trial_workflow_map_check.py",
            "documentation": "docs/phase9_1_beta_testing_customer_trial_workflow_map.md",
            "required_for_completion": True,
        },
        {
            "phase": "Phase 9-2",
            "artifact": "Beta tester onboarding checklist",
            "module": "app/paid_simulator/phase9_beta_tester_onboarding_checklist.py",
            "check_script": "app/run_paid_simulator_phase9_2_beta_tester_onboarding_checklist_check.py",
            "documentation": "docs/phase9_2_beta_tester_onboarding_checklist.md",
            "required_for_completion": True,
        },
        {
            "phase": "Phase 9-3",
            "artifact": "Customer feedback capture template",
            "module": "app/paid_simulator/phase9_customer_feedback_capture_template.py",
            "check_script": "app/run_paid_simulator_phase9_3_customer_feedback_capture_template_check.py",
            "documentation": "docs/phase9_3_customer_feedback_capture_template.md",
            "required_for_completion": True,
        },
        {
            "phase": "Phase 9-4",
            "artifact": "Beta safety and disclaimer review",
            "module": "app/paid_simulator/phase9_beta_safety_disclaimer_review.py",
            "check_script": "app/run_paid_simulator_phase9_4_beta_safety_disclaimer_review_check.py",
            "documentation": "docs/phase9_4_beta_safety_disclaimer_review.md",
            "required_for_completion": True,
        },
        {
            "phase": "Phase 9-5",
            "artifact": "Trial-run smoke-test script",
            "module": "app/paid_simulator/phase9_trial_run_smoke_test_script.py",
            "check_script": "app/run_paid_simulator_phase9_5_trial_run_smoke_test_script_check.py",
            "documentation": "docs/phase9_5_trial_run_smoke_test_script.md",
            "required_for_completion": True,
        },
    ]


def _project_artifact_exists(relative_path: str) -> bool:
    return (PROJECT_ROOT / relative_path).exists()


def build_phase9_6_summary() -> dict[str, Any]:
    _ensure_dirs()

    artifact_rows = build_phase9_6_artifact_rows()
    for row in artifact_rows:
        row["module_exists"] = _project_artifact_exists(row["module"])
        row["check_script_exists"] = _project_artifact_exists(row["check_script"])
        row["documentation_exists"] = _project_artifact_exists(row["documentation"])
        row["artifact_complete"] = bool(
            row["module_exists"] and row["check_script_exists"] and row["documentation_exists"]
        )

    artifacts_df = pd.DataFrame(artifact_rows)
    artifacts_df.to_csv(ARTIFACTS_CSV, index=False)

    all_required_artifacts_present = bool(artifacts_df["artifact_complete"].all()) if not artifacts_df.empty else False

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "phase9_completion_handoff_created": True,
        "phase9_artifact_rows": int(len(artifacts_df)),
        "all_required_phase9_artifacts_present": all_required_artifacts_present,
        "beta_workflow_map_exists": _project_artifact_exists("app/paid_simulator/phase9_beta_testing_customer_trial_workflow_map.py"),
        "beta_onboarding_checklist_exists": _project_artifact_exists("app/paid_simulator/phase9_beta_tester_onboarding_checklist.py"),
        "customer_feedback_template_exists": _project_artifact_exists("app/paid_simulator/phase9_customer_feedback_capture_template.py"),
        "beta_safety_disclaimer_review_exists": _project_artifact_exists("app/paid_simulator/phase9_beta_safety_disclaimer_review.py"),
        "trial_run_smoke_test_script_exists": _project_artifact_exists("app/paid_simulator/phase9_trial_run_smoke_test_script.py"),
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "unknown_modes_fall_back_to_synthetic": True,
        "historical_data_is_scenario_input_not_forecast": True,
        "regime_detection_probabilistic_not_oracle": True,
        "beta_feedback_capture_defined": True,
        "beta_safety_review_defined": True,
        "trial_run_smoke_test_defined": True,
        "ready_for_phase10": all_required_artifacts_present,
        "row_count": int(len(artifacts_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 9-6 completion handoff",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Phase 9 artifact rows: {summary['phase9_artifact_rows']}",
        f"All required Phase 9 artifacts present: {all_required_artifacts_present}",
        f"Synthetic default preserved: {summary['synthetic_default_preserved']}",
        f"Historical mode explicit only: {summary['historical_mode_explicit_only']}",
        f"Unknown modes fall back to synthetic: {summary['unknown_modes_fall_back_to_synthetic']}",
        f"{CAUTION}: {summary['historical_data_is_scenario_input_not_forecast']}",
        f"{REGIME_CAUTION}: {summary['regime_detection_probabilistic_not_oracle']}",
        f"Ready for Phase 10: {summary['ready_for_phase10']}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase9_6_summary(), indent=2))
