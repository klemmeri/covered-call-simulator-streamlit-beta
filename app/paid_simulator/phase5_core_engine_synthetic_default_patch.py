"""
phase5_core_engine_synthetic_default_patch.py

Phase 5-9 checkpoint for the Covered Call Simulator paid simulator workflow.

Purpose
-------
Create a guarded core-engine integration contract for supporting historical
path input while preserving the existing synthetic-path workflow as the default.

This checkpoint intentionally does not expose historical mode in the dashboard.
It also does not make historical mode the default. The module produces a patch
readiness report and a small engine-mode resolver contract that can be used by
future engine patches.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


READY_MARKER = "PHASE5_9_CORE_ENGINE_SYNTHETIC_DEFAULT_PATCH_READY"
RELEASE_DECISION = "PHASE5_9_CORE_ENGINE_SYNTHETIC_DEFAULT_PATCH_CREATED_SYNTHETIC_DEFAULT_PROTECTED"
SOURCE_MODE = "core_engine_synthetic_default_guard"
DEFAULT_ENGINE_MODE = "synthetic"
HISTORICAL_ENGINE_MODE = "historical_import"

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]
APP_DIR = PROJECT_ROOT / "app"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

ENGINE_FILES = [
    "app/price_paths.py",
    "app/simulator.py",
    "app/strategy.py",
    "app/portfolio.py",
    "app/config.py",
]

PRIOR_ARTIFACTS = [
    "app/paid_simulator/phase5_synthetic_default_regression_guard.py",
    "app/paid_simulator/phase5_controlled_core_engine_patch.py",
    "outputs/tables/paid_simulator/phase5_5_historical_mode_smoke_test_rows.csv",
    "outputs/reports/paid_simulator/phase5_5_historical_mode_smoke_test.json",
]


def _ensure_output_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def resolve_engine_mode(requested_mode: str | None = None) -> str:
    """
    Resolve the engine mode while preserving synthetic mode as the default.

    Parameters
    ----------
    requested_mode:
        Optional requested mode. Supported values are "synthetic" and
        "historical_import". Missing, blank, or unrecognized values are treated
        as synthetic to avoid accidental historical-mode activation.
    """

    if requested_mode is None:
        return DEFAULT_ENGINE_MODE

    normalized = str(requested_mode).strip().lower()
    if normalized == HISTORICAL_ENGINE_MODE:
        return HISTORICAL_ENGINE_MODE
    if normalized == DEFAULT_ENGINE_MODE:
        return DEFAULT_ENGINE_MODE
    return DEFAULT_ENGINE_MODE


def build_engine_file_status() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for relative_path in ENGINE_FILES:
        path = PROJECT_ROOT / relative_path
        rows.append(
            {
                "relative_path": relative_path,
                "exists": path.exists(),
                "planned_phase5_role": _planned_role(relative_path),
                "patch_status": "not_replaced_by_phase5_9",
            }
        )
    return pd.DataFrame(rows)


def _planned_role(relative_path: str) -> str:
    mapping = {
        "app/price_paths.py": "first integration target; add optional imported-path provider while preserving synthetic generation",
        "app/simulator.py": "consume path provider selection after price_paths.py contract is stable",
        "app/strategy.py": "preserve covered-call rule behavior; no immediate historical-mode change",
        "app/portfolio.py": "preserve path-level accounting; later consume historical path rows if supplied",
        "app/config.py": "eventually add explicit data_source field with synthetic default",
    }
    return mapping.get(relative_path, "supporting engine file")


def build_prior_artifact_status() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for relative_path in PRIOR_ARTIFACTS:
        path = PROJECT_ROOT / relative_path
        rows.append(
            {
                "relative_path": relative_path,
                "exists": path.exists(),
                "required_before_actual_engine_patch": True,
            }
        )
    return pd.DataFrame(rows)


def build_engine_mode_contract() -> pd.DataFrame:
    rows = [
        {
            "contract_item": "default_mode",
            "value": DEFAULT_ENGINE_MODE,
            "requirement": "Synthetic mode must remain the default when no mode is requested.",
            "status": "PASS" if resolve_engine_mode(None) == DEFAULT_ENGINE_MODE else "FAIL",
        },
        {
            "contract_item": "explicit_historical_mode",
            "value": HISTORICAL_ENGINE_MODE,
            "requirement": "Historical mode must be selected only by explicit request.",
            "status": "PASS" if resolve_engine_mode(HISTORICAL_ENGINE_MODE) == HISTORICAL_ENGINE_MODE else "FAIL",
        },
        {
            "contract_item": "unknown_mode_fallback",
            "value": resolve_engine_mode("unknown_mode"),
            "requirement": "Unknown requested modes must fall back to synthetic mode.",
            "status": "PASS" if resolve_engine_mode("unknown_mode") == DEFAULT_ENGINE_MODE else "FAIL",
        },
        {
            "contract_item": "dashboard_change_required",
            "value": False,
            "requirement": "No dashboard change is required in Phase 5-9.",
            "status": "PASS",
        },
        {
            "contract_item": "customer_workflow_change_required",
            "value": False,
            "requirement": "No public customer workflow change is required in Phase 5-9.",
            "status": "PASS",
        },
    ]
    return pd.DataFrame(rows)


def build_patch_readiness_table() -> pd.DataFrame:
    rows = [
        {
            "step": 1,
            "patch_target": "app/price_paths.py",
            "action": "Add optional imported historical path provider behind explicit mode flag.",
            "guardrail": "Default behavior must remain synthetic path generation.",
            "status": "planned_not_applied_by_phase5_9",
        },
        {
            "step": 2,
            "patch_target": "app/config.py",
            "action": "Later add data_source or path_source configuration with synthetic default.",
            "guardrail": "Existing config construction must remain backward compatible.",
            "status": "future_phase",
        },
        {
            "step": 3,
            "patch_target": "app/simulator.py",
            "action": "Later route through selected path provider.",
            "guardrail": "Current synthetic regression check must continue to pass.",
            "status": "future_phase",
        },
    ]
    return pd.DataFrame(rows)


def build_phase5_9_summary(requested_mode: str | None = None) -> dict[str, Any]:
    _ensure_output_dirs()

    selected_mode = resolve_engine_mode(requested_mode)
    engine_status_df = build_engine_file_status()
    prior_status_df = build_prior_artifact_status()
    contract_df = build_engine_mode_contract()
    readiness_df = build_patch_readiness_table()

    engine_status_csv = OUTPUT_TABLE_DIR / "phase5_9_engine_file_status.csv"
    prior_status_csv = OUTPUT_TABLE_DIR / "phase5_9_prior_artifact_status.csv"
    contract_csv = OUTPUT_TABLE_DIR / "phase5_9_engine_mode_contract.csv"
    readiness_csv = OUTPUT_TABLE_DIR / "phase5_9_core_engine_patch_readiness.csv"
    summary_csv = OUTPUT_TABLE_DIR / "phase5_9_core_engine_synthetic_default_patch_summary.csv"
    json_path = OUTPUT_REPORT_DIR / "phase5_9_core_engine_synthetic_default_patch.json"
    report_path = OUTPUT_REPORT_DIR / "phase5_9_core_engine_synthetic_default_patch_report.txt"

    engine_status_df.to_csv(engine_status_csv, index=False)
    prior_status_df.to_csv(prior_status_csv, index=False)
    contract_df.to_csv(contract_csv, index=False)
    readiness_df.to_csv(readiness_csv, index=False)

    core_engine_files_found = int(engine_status_df["exists"].sum())
    prior_artifacts_found = int(prior_status_df["exists"].sum())
    contract_pass_count = int((contract_df["status"] == "PASS").sum())
    contract_row_count = int(len(contract_df))
    synthetic_default_preserved = resolve_engine_mode(None) == DEFAULT_ENGINE_MODE
    historical_mode_explicit_only = resolve_engine_mode(HISTORICAL_ENGINE_MODE) == HISTORICAL_ENGINE_MODE and resolve_engine_mode(None) != HISTORICAL_ENGINE_MODE
    unknown_mode_falls_back_to_synthetic = resolve_engine_mode("unknown") == DEFAULT_ENGINE_MODE

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "requested_mode": requested_mode if requested_mode is not None else "not_requested",
        "selected_mode": selected_mode,
        "default_engine_mode": DEFAULT_ENGINE_MODE,
        "dashboard_change_required": False,
        "customer_workflow_change_required": False,
        "core_engine_patch_contract_created": True,
        "actual_core_engine_files_replaced": False,
        "synthetic_default_preserved": synthetic_default_preserved,
        "historical_mode_explicit_only": historical_mode_explicit_only,
        "unknown_mode_falls_back_to_synthetic": unknown_mode_falls_back_to_synthetic,
        "engine_file_rows": int(len(engine_status_df)),
        "core_engine_files_found": core_engine_files_found,
        "prior_artifact_rows": int(len(prior_status_df)),
        "prior_artifacts_found": prior_artifacts_found,
        "engine_mode_contract_rows": contract_row_count,
        "engine_mode_contract_pass_count": contract_pass_count,
        "patch_readiness_rows": int(len(readiness_df)),
        "first_patch_target": "app/price_paths.py",
        "overall_status": "PASS" if synthetic_default_preserved and historical_mode_explicit_only and contract_pass_count == contract_row_count else "FAIL",
        "outputs": {
            "engine_file_status_csv": str(engine_status_csv),
            "prior_artifact_status_csv": str(prior_status_csv),
            "engine_mode_contract_csv": str(contract_csv),
            "patch_readiness_csv": str(readiness_csv),
            "summary_csv": str(summary_csv),
            "json": str(json_path),
            "report": str(report_path),
        },
    }

    pd.DataFrame([summary]).to_csv(summary_csv, index=False)
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    report_path.write_text(_build_report_text(summary), encoding="utf-8")
    return summary


def _build_report_text(summary: dict[str, Any]) -> str:
    lines = [
        "Phase 5-9 Core Engine Synthetic-Default Patch",
        "=" * 70,
        f"Ready marker: {summary['ready_marker']}",
        f"Release decision: {summary['release_decision']}",
        f"Source mode: {summary['source_mode']}",
        f"Selected mode: {summary['selected_mode']}",
        f"Synthetic default preserved: {summary['synthetic_default_preserved']}",
        f"Historical mode explicit only: {summary['historical_mode_explicit_only']}",
        f"Actual core engine files replaced: {summary['actual_core_engine_files_replaced']}",
        f"Dashboard change required: {summary['dashboard_change_required']}",
        f"First patch target: {summary['first_patch_target']}",
        f"Overall status: {summary['overall_status']}",
        "",
        "Phase 5-9 creates the guarded contract for the first true engine patch.",
        "It deliberately preserves synthetic mode as the default and does not expose",
        "historical mode in the dashboard.",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    build_phase5_9_summary()
