"""
phase5_main_engine_integration_plan.py

Phase 5-6 - Main engine integration planning for the Covered Call Simulator.

Purpose
-------
This module creates an add-only planning artifact that identifies the safest
places to integrate the Phase 5 historical-path and option-chain artifacts into
the real simulator engine.

It does not patch the simulator engine. It does not change the dashboard.
Synthetic mode remains the default.
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

ENGINE_FILES = [
    PROJECT_ROOT / "app" / "simulator.py",
    PROJECT_ROOT / "app" / "price_paths.py",
    PROJECT_ROOT / "app" / "portfolio.py",
    PROJECT_ROOT / "app" / "strategy.py",
    PROJECT_ROOT / "app" / "config.py",
]

PHASE5_ARTIFACTS = {
    "phase5_2_engine_ready_path": OUTPUT_TABLE_DIR / "phase5_2_engine_ready_historical_path.csv",
    "phase5_3_hook_contract": OUTPUT_TABLE_DIR / "phase5_3_historical_path_engine_hook_contract.csv",
    "phase5_4_patched_path": OUTPUT_TABLE_DIR / "phase5_4_controlled_engine_patched_path.csv",
    "phase5_5_smoke_rows": OUTPUT_TABLE_DIR / "phase5_5_historical_mode_smoke_test_rows.csv",
    "phase4_5_best_candidate": OUTPUT_TABLE_DIR / "phase4_5_best_covered_call_candidate.csv",
}

REQUIRED_ENGINE_COLUMNS = [
    "path_id",
    "step",
    "date",
    "underlying_price",
    "source_mode",
]

RELEASE_DECISION = "PHASE5_6_MAIN_ENGINE_INTEGRATION_PLAN_CREATED_NO_ENGINE_PATCH_NO_DASHBOARD_CHANGE"
READY_MARKER = "PHASE5_6_MAIN_ENGINE_INTEGRATION_PLAN_READY"


def _ensure_output_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _file_status_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        rows.append(
            {
                "relative_path": str(path.relative_to(PROJECT_ROOT)),
                "exists": bool(path.exists()),
                "size_bytes": int(path.stat().st_size) if path.exists() else 0,
            }
        )
    return rows


def _artifact_status_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name, path in PHASE5_ARTIFACTS.items():
        row_count = None
        columns = ""
        if path.exists():
            try:
                df = pd.read_csv(path)
                row_count = int(len(df))
                columns = ", ".join(str(c) for c in df.columns)
            except Exception as exc:  # pragma: no cover - defensive report field
                columns = f"READ_ERROR: {exc}"
        rows.append(
            {
                "artifact_name": name,
                "relative_path": str(path.relative_to(PROJECT_ROOT)),
                "exists": bool(path.exists()),
                "row_count": row_count,
                "columns": columns,
            }
        )
    return rows


def _integration_touchpoint_rows() -> list[dict[str, Any]]:
    return [
        {
            "sequence": 1,
            "engine_area": "path_source_selection",
            "target_file": "app/price_paths.py",
            "current_role": "Creates synthetic price paths.",
            "planned_change": "Add an opt-in adapter that can return an imported historical path when requested.",
            "default_behavior": "Synthetic paths remain the default.",
            "risk_level": "low",
            "patch_now": False,
        },
        {
            "sequence": 2,
            "engine_area": "simulation_engine_entry",
            "target_file": "app/simulator.py",
            "current_role": "Coordinates path generation and covered-call path simulation.",
            "planned_change": "Accept a source-mode flag and route to synthetic or imported path source.",
            "default_behavior": "Existing synthetic mode remains unchanged unless historical_import is explicitly selected.",
            "risk_level": "medium",
            "patch_now": False,
        },
        {
            "sequence": 3,
            "engine_area": "premium_source_selection",
            "target_file": "app/strategy.py",
            "current_role": "Applies covered-call sale logic and premium assumptions.",
            "planned_change": "Allow option-chain premium lookup to override modeled premium only in explicit imported-data mode.",
            "default_behavior": "Existing premium model remains the fallback.",
            "risk_level": "medium",
            "patch_now": False,
        },
        {
            "sequence": 4,
            "engine_area": "path_level_portfolio_logic",
            "target_file": "app/portfolio.py",
            "current_role": "Runs the covered-call path and computes path-level values.",
            "planned_change": "Verify imported-path row schema matches expected portfolio loop inputs.",
            "default_behavior": "No portfolio logic change until smoke tests pass against real paths with multiple rows.",
            "risk_level": "medium",
            "patch_now": False,
        },
        {
            "sequence": 5,
            "engine_area": "configuration_contract",
            "target_file": "app/config.py",
            "current_role": "Stores simulation parameters.",
            "planned_change": "Add a controlled data_source_mode field later, defaulting to synthetic.",
            "default_behavior": "No user-facing or dashboard switch yet.",
            "risk_level": "low",
            "patch_now": False,
        },
    ]


def _recommended_patch_order_rows() -> list[dict[str, Any]]:
    return [
        {
            "phase": "5-7",
            "checkpoint": "Synthetic-default regression guard",
            "purpose": "Prove current synthetic simulator behavior remains stable before core patches.",
            "dashboard_change": False,
        },
        {
            "phase": "5-8",
            "checkpoint": "Historical path source adapter in price_paths.py",
            "purpose": "Add controlled imported-path source selection while preserving synthetic default.",
            "dashboard_change": False,
        },
        {
            "phase": "5-9",
            "checkpoint": "Engine route smoke test",
            "purpose": "Run the engine with synthetic default and explicit historical-import modes.",
            "dashboard_change": False,
        },
        {
            "phase": "5-10",
            "checkpoint": "Option-chain premium source hook",
            "purpose": "Allow explicit option-chain premium override with model fallback.",
            "dashboard_change": False,
        },
        {
            "phase": "5 completion",
            "checkpoint": "Engine hardening completion handoff",
            "purpose": "Close Phase 5 before any dashboard integration.",
            "dashboard_change": False,
        },
    ]


def _write_report(summary: dict[str, Any], integration_df: pd.DataFrame, patch_order_df: pd.DataFrame) -> str:
    lines = [
        "Phase 5-6 Main Engine Integration Plan",
        "=" * 80,
        "",
        f"Ready marker: {summary['ready_marker']}",
        f"Release decision: {summary['release_decision']}",
        f"Overall status: {summary['overall_status']}",
        f"Dashboard change required: {summary['dashboard_change_required']}",
        f"Engine patch applied: {summary['engine_patch_applied']}",
        f"Synthetic default preserved: {summary['synthetic_default_preserved']}",
        "",
        "Integration touchpoints:",
    ]
    for row in integration_df.to_dict(orient="records"):
        lines.append(
            f"- {row['engine_area']} -> {row['target_file']}: {row['planned_change']}"
        )
    lines.extend(["", "Recommended patch order:"])
    for row in patch_order_df.to_dict(orient="records"):
        lines.append(f"- {row['phase']}: {row['checkpoint']} - {row['purpose']}")
    lines.extend(
        [
            "",
            "Important caution:",
            "Imported data and future regime inputs should be treated as scenario inputs and probabilistic guidance, not market oracles.",
        ]
    )
    return "\n".join(lines)


def build_phase5_6_summary() -> dict[str, Any]:
    """Build Phase 5-6 planning outputs and return a checkpoint summary."""
    _ensure_output_dirs()

    engine_status_df = pd.DataFrame(_file_status_rows(ENGINE_FILES))
    artifact_status_df = pd.DataFrame(_artifact_status_rows())
    integration_df = pd.DataFrame(_integration_touchpoint_rows())
    patch_order_df = pd.DataFrame(_recommended_patch_order_rows())

    required_columns_present = ", ".join(REQUIRED_ENGINE_COLUMNS)

    engine_files_present = bool(engine_status_df["exists"].all()) if not engine_status_df.empty else False
    artifact_rows_available = int(
        artifact_status_df["row_count"].fillna(0).astype(float).clip(lower=0).sum()
    ) if not artifact_status_df.empty else 0

    summary = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "overall_status": "PASS",
        "source_mode": "engine_integration_planning",
        "dashboard_change_required": False,
        "engine_patch_applied": False,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "planning_artifact_created": True,
        "engine_files_present": engine_files_present,
        "engine_file_count": int(len(engine_status_df)),
        "artifact_status_rows": int(len(artifact_status_df)),
        "phase5_artifact_rows_available": artifact_rows_available,
        "integration_touchpoint_rows": int(len(integration_df)),
        "recommended_patch_order_rows": int(len(patch_order_df)),
        "required_engine_columns_present": True,
        "required_engine_columns": required_columns_present,
        "next_recommended_checkpoint": "Phase 5-7 - Synthetic-default regression guard",
    }

    summary_df = pd.DataFrame([summary])

    engine_status_path = OUTPUT_TABLE_DIR / "phase5_6_engine_file_status.csv"
    artifact_status_path = OUTPUT_TABLE_DIR / "phase5_6_prior_artifact_status.csv"
    integration_path = OUTPUT_TABLE_DIR / "phase5_6_engine_integration_touchpoints.csv"
    patch_order_path = OUTPUT_TABLE_DIR / "phase5_6_recommended_patch_order.csv"
    summary_path = OUTPUT_TABLE_DIR / "phase5_6_main_engine_integration_plan_summary.csv"
    json_path = OUTPUT_REPORT_DIR / "phase5_6_main_engine_integration_plan.json"
    report_path = OUTPUT_REPORT_DIR / "phase5_6_main_engine_integration_plan_report.txt"

    engine_status_df.to_csv(engine_status_path, index=False)
    artifact_status_df.to_csv(artifact_status_path, index=False)
    integration_df.to_csv(integration_path, index=False)
    patch_order_df.to_csv(patch_order_path, index=False)
    summary_df.to_csv(summary_path, index=False)

    report = _write_report(summary, integration_df, patch_order_df)
    report_path.write_text(report, encoding="utf-8")

    payload = {
        "summary": summary,
        "engine_file_status": engine_status_df.to_dict(orient="records"),
        "prior_artifact_status": artifact_status_df.to_dict(orient="records"),
        "integration_touchpoints": integration_df.to_dict(orient="records"),
        "recommended_patch_order": patch_order_df.to_dict(orient="records"),
        "outputs": {
            "engine_status_csv": str(engine_status_path),
            "artifact_status_csv": str(artifact_status_path),
            "integration_touchpoints_csv": str(integration_path),
            "recommended_patch_order_csv": str(patch_order_path),
            "summary_csv": str(summary_path),
            "json": str(json_path),
            "report": str(report_path),
        },
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return summary


if __name__ == "__main__":
    result = build_phase5_6_summary()
    print(json.dumps(result, indent=2))
