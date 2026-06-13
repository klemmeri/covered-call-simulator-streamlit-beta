"""
phase6_dashboard_runner_wiring_patch.py

Phase 6-9 controlled dashboard runner wiring patch support module.

This module supports a guarded dashboard helper that maps customer-facing
dashboard data-mode labels to internal runner modes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase6_9_dashboard_runner_wiring_patch_summary.csv"
CONTRACT_CSV = OUTPUT_TABLE_DIR / "phase6_9_dashboard_runner_wiring_patch_contract.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase6_9_dashboard_runner_wiring_patch.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase6_9_dashboard_runner_wiring_patch_report.txt"

READY_MARKER = "PHASE6_9_DASHBOARD_RUNNER_WIRING_PATCH_READY"
RELEASE_DECISION = "PHASE6_9_DASHBOARD_RUNNER_WIRING_PATCH_CREATED_GUARDED_DASHBOARD_HELPER"
SOURCE_MODE = "dashboard_runner_wiring_patch"
CAUTION = "Historical data is scenario input, not forecast"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def resolve_phase6_9_dashboard_runner_mode(dashboard_mode: str | None) -> dict[str, Any]:
    if dashboard_mode == "Imported historical data":
        selected_dashboard_mode = "Imported historical data"
        runner_mode = "historical_import"
    else:
        selected_dashboard_mode = "Synthetic scenarios"
        runner_mode = "synthetic"

    return {
        "selected_dashboard_mode": selected_dashboard_mode,
        "runner_mode": runner_mode,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "unknown_modes_fall_back_to_synthetic": dashboard_mode not in {"Synthetic scenarios", "Imported historical data"},
        "historical_data_is_scenario_input_not_forecast": True,
        "customer_caution": CAUTION,
    }


def build_phase6_9_contract() -> list[dict[str, Any]]:
    cases = [
        ("Synthetic scenarios", "synthetic", True, "Default customer workflow."),
        ("Imported historical data", "historical_import", False, CAUTION),
        ("unknown", "synthetic", True, "Unknown modes fall back to synthetic."),
    ]
    rows: list[dict[str, Any]] = []
    for dashboard_mode, runner_mode, is_default, guardrail in cases:
        rows.append(
            {
                "dashboard_mode": dashboard_mode,
                "runner_mode": runner_mode,
                "synthetic_default": is_default,
                "historical_explicit_only": dashboard_mode == "Imported historical data",
                "guardrail": guardrail,
            }
        )
    return rows


def build_phase6_9_summary() -> dict[str, Any]:
    _ensure_dirs()

    contract_rows = build_phase6_9_contract()
    contract_df = pd.DataFrame(contract_rows)
    contract_df.to_csv(CONTRACT_CSV, index=False)

    synthetic_case = resolve_phase6_9_dashboard_runner_mode("Synthetic scenarios")
    historical_case = resolve_phase6_9_dashboard_runner_mode("Imported historical data")
    unknown_case = resolve_phase6_9_dashboard_runner_mode("bad_mode")

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": True,
        "dashboard_patch_guarded": True,
        "dashboard_patch_bounded": True,
        "dashboard_runner_wiring_helper_created": True,
        "dashboard_customer_workflow_changed": False,
        "synthetic_default_preserved": synthetic_case["runner_mode"] == "synthetic",
        "historical_mode_explicit_only": historical_case["runner_mode"] == "historical_import",
        "unknown_modes_fall_back_to_synthetic": unknown_case["runner_mode"] == "synthetic",
        "historical_data_is_scenario_input_not_forecast": True,
        "scenario_input_not_forecast": True,
        "synthetic_runner_mode": synthetic_case["runner_mode"],
        "historical_runner_mode": historical_case["runner_mode"],
        "unknown_runner_mode": unknown_case["runner_mode"],
        "contract_rows": int(len(contract_df)),
        "row_count": int(len(contract_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 6-9 controlled dashboard runner wiring patch",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Synthetic runner mode: {summary['synthetic_runner_mode']}",
        f"Historical runner mode: {summary['historical_runner_mode']}",
        f"Unknown runner mode: {summary['unknown_runner_mode']}",
        f"{CAUTION}: {summary['historical_data_is_scenario_input_not_forecast']}",
        f"Contract rows: {summary['contract_rows']}",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase6_9_summary(), indent=2))
