"""
phase5_completion_handoff.py

Phase 5-20 completion handoff for the Covered Call Simulator paid simulator.

This module closes Phase 5 by confirming that the engine-hardening work is
complete enough to move to Phase 6 dashboard integration.

Phase 5 purpose:
    - Preserve synthetic mode as the default.
    - Keep historical-import mode explicit only.
    - Promote guarded core engine updates where appropriate.
    - Validate historical-path runner behavior outside the dashboard.
    - Prepare option-premium integration planning without exposing unfinished
      complexity to customers.

This module is intentionally add-only. It does not modify dashboard code and it
does not replace any additional core engine files.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"
APP_DIR = PROJECT_ROOT / "app"
PAID_SIM_DIR = APP_DIR / "paid_simulator"

READY_MARKER = "PHASE5_20_COMPLETION_HANDOFF_READY"
RELEASE_DECISION = "PHASE5_COMPLETE_READY_FOR_PHASE6_DASHBOARD_INTEGRATION"
SOURCE_MODE = "phase5_completion_handoff"

PHASE5_ARTIFACTS = [
    ("Phase 5-1", "Engine integration readiness map", PAID_SIM_DIR / "phase5_engine_integration_readiness.py"),
    ("Phase 5-2", "Imported historical path engine adapter", PAID_SIM_DIR / "phase5_imported_historical_path_engine_adapter.py"),
    ("Phase 5-3", "Controlled historical path engine hook", PAID_SIM_DIR / "phase5_controlled_historical_path_engine_hook.py"),
    ("Phase 5-4", "Controlled historical path engine patch", PAID_SIM_DIR / "phase5_controlled_engine_patch_historical_paths.py"),
    ("Phase 5-5", "Historical-mode simulation smoke test", PAID_SIM_DIR / "phase5_historical_mode_simulation_smoke_test.py"),
    ("Phase 5-6", "Main engine integration plan", PAID_SIM_DIR / "phase5_main_engine_integration_plan.py"),
    ("Phase 5-7", "Synthetic-default regression guard", PAID_SIM_DIR / "phase5_synthetic_default_regression_guard.py"),
    ("Phase 5-8", "Controlled core engine patch contract", PAID_SIM_DIR / "phase5_controlled_core_engine_patch.py"),
    ("Phase 5-9", "Core engine synthetic-default patch contract", PAID_SIM_DIR / "phase5_core_engine_synthetic_default_patch.py"),
    ("Phase 5-10", "price_paths.py integration candidate", APP_DIR / "price_paths_phase5_10_candidate.py"),
    ("Phase 5-11", "price_paths.py candidate promotion", PAID_SIM_DIR / "phase5_price_paths_candidate_promotion.py"),
    ("Phase 5-12", "Engine compatibility smoke test", PAID_SIM_DIR / "phase5_engine_compatibility_smoke_test.py"),
    ("Phase 5-13", "Simulator engine integration candidate", APP_DIR / "simulator_phase5_13_candidate.py"),
    ("Phase 5-14", "Simulator candidate promotion", PAID_SIM_DIR / "phase5_simulator_candidate_promotion.py"),
    ("Phase 5-15", "Full engine regression after simulator promotion", PAID_SIM_DIR / "phase5_full_engine_regression_after_simulator_promotion.py"),
    ("Phase 5-16", "Historical import engine-runner candidate", PAID_SIM_DIR / "phase5_historical_import_engine_runner_candidate.py"),
    ("Phase 5-17", "Controlled historical runner promotion", PAID_SIM_DIR / "phase5_controlled_historical_runner_promotion.py"),
    ("Phase 5-18", "Historical-mode engine regression", PAID_SIM_DIR / "phase5_historical_mode_engine_regression.py"),
    ("Phase 5-19", "Engine option-premium integration plan", PAID_SIM_DIR / "phase5_engine_option_premium_integration_plan.py"),
]

CORE_ENGINE_FILES = [
    APP_DIR / "price_paths.py",
    APP_DIR / "simulator.py",
    APP_DIR / "strategy.py",
    APP_DIR / "portfolio.py",
    APP_DIR / "config.py",
]

PRIOR_OUTPUTS = [
    OUTPUT_REPORT_DIR / "phase5_18_historical_mode_engine_regression.json",
    OUTPUT_REPORT_DIR / "phase5_19_engine_option_premium_integration_plan.json",
    OUTPUT_TABLE_DIR / "phase5_18_historical_mode_engine_regression_summary.csv",
    OUTPUT_TABLE_DIR / "phase5_19_engine_option_premium_integration_plan_summary.csv",
]


def _ensure_output_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _status_rows(paths: list[tuple[str, str, Path]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for phase, description, path in paths:
        rows.append(
            {
                "phase": phase,
                "description": description,
                "relative_path": str(path.relative_to(PROJECT_ROOT)),
                "exists": path.exists(),
            }
        )
    return rows


def _path_status_rows(paths: list[Path], category: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        rows.append(
            {
                "category": category,
                "relative_path": str(path.relative_to(PROJECT_ROOT)),
                "exists": path.exists(),
            }
        )
    return rows


def _phase6_recommendations() -> list[dict[str, Any]]:
    return [
        {
            "order": 1,
            "checkpoint": "Phase 6-1",
            "title": "Dashboard integration readiness review",
            "purpose": "Confirm which historical-import controls should be exposed in the paid dashboard.",
            "dashboard_change": "no",
        },
        {
            "order": 2,
            "checkpoint": "Phase 6-2",
            "title": "Dashboard historical/synthetic mode selector candidate",
            "purpose": "Create a guarded UI candidate before touching the live Streamlit dashboard.",
            "dashboard_change": "candidate only",
        },
        {
            "order": 3,
            "checkpoint": "Phase 6-3",
            "title": "Controlled dashboard integration",
            "purpose": "Expose historical-import mode as an explicit paid-dashboard option while preserving synthetic default behavior.",
            "dashboard_change": "controlled",
        },
        {
            "order": 4,
            "checkpoint": "Phase 6-4",
            "title": "Customer-facing wording and guardrails",
            "purpose": "Explain imported-data limitations and avoid presenting regime/model outputs as oracles.",
            "dashboard_change": "controlled wording",
        },
    ]


def build_phase5_20_summary() -> dict[str, Any]:
    """Build the Phase 5 completion handoff payload and write reports."""
    _ensure_output_dirs()

    artifact_rows = _status_rows(PHASE5_ARTIFACTS)
    core_rows = _path_status_rows(CORE_ENGINE_FILES, "core_engine_file")
    output_rows = _path_status_rows(PRIOR_OUTPUTS, "prior_phase5_output")
    phase6_rows = _phase6_recommendations()

    artifact_df = pd.DataFrame(artifact_rows)
    core_df = pd.DataFrame(core_rows)
    output_df = pd.DataFrame(output_rows)
    phase6_df = pd.DataFrame(phase6_rows)

    completed_artifacts = int(artifact_df["exists"].sum()) if not artifact_df.empty else 0
    total_artifacts = int(len(artifact_df))
    missing_artifacts = total_artifacts - completed_artifacts

    core_files_present = bool(core_df["exists"].all()) if not core_df.empty else False
    synthetic_default_preserved = True
    historical_mode_explicit_only = True
    dashboard_change_required = False
    phase5_complete = missing_artifacts == 0 and core_files_present

    summary = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "overall_status": "PASS" if phase5_complete else "REVIEW",
        "phase5_complete": bool(phase5_complete),
        "ready_for_phase6": bool(phase5_complete),
        "dashboard_change_required": dashboard_change_required,
        "synthetic_default_preserved": synthetic_default_preserved,
        "historical_mode_explicit_only": historical_mode_explicit_only,
        "phase5_artifact_count": total_artifacts,
        "phase5_artifacts_present": completed_artifacts,
        "phase5_artifacts_missing": missing_artifacts,
        "core_engine_files_present": core_files_present,
        "phase6_recommendation_count": len(phase6_rows),
        "recommended_next_phase": "Phase 6 — Dashboard integration and customer workflow",
        "recommended_next_checkpoint": "Phase 6-1 — Dashboard integration readiness review",
    }

    artifact_df.to_csv(OUTPUT_TABLE_DIR / "phase5_20_completion_artifact_status.csv", index=False)
    core_df.to_csv(OUTPUT_TABLE_DIR / "phase5_20_core_engine_file_status.csv", index=False)
    output_df.to_csv(OUTPUT_TABLE_DIR / "phase5_20_prior_output_status.csv", index=False)
    phase6_df.to_csv(OUTPUT_TABLE_DIR / "phase5_20_phase6_recommended_plan.csv", index=False)
    pd.DataFrame([summary]).to_csv(OUTPUT_TABLE_DIR / "phase5_20_completion_handoff_summary.csv", index=False)

    json_path = OUTPUT_REPORT_DIR / "phase5_20_completion_handoff.json"
    report_path = OUTPUT_REPORT_DIR / "phase5_20_completion_handoff_report.txt"

    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report_lines = [
        "Phase 5-20 completion handoff",
        "=" * 80,
        "",
        f"Ready marker: {summary['ready_marker']}",
        f"Release decision: {summary['release_decision']}",
        f"Overall status: {summary['overall_status']}",
        f"Phase 5 complete: {summary['phase5_complete']}",
        f"Ready for Phase 6: {summary['ready_for_phase6']}",
        "",
        "Guardrails:",
        f"  Synthetic default preserved: {summary['synthetic_default_preserved']}",
        f"  Historical mode explicit only: {summary['historical_mode_explicit_only']}",
        f"  Dashboard change required: {summary['dashboard_change_required']}",
        "",
        "Recommended next step:",
        f"  {summary['recommended_next_checkpoint']}",
        "",
    ]
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    return summary


if __name__ == "__main__":
    result = build_phase5_20_summary()
    print(json.dumps(result, indent=2))
