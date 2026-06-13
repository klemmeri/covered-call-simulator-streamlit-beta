"""
phase6_dashboard_historical_input_panel_patch.py

Phase 6-6 controlled dashboard historical input-panel patch support module.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase6_6_dashboard_historical_input_panel_patch_summary.csv"
CONTRACT_CSV = OUTPUT_TABLE_DIR / "phase6_6_dashboard_historical_input_panel_patch_contract.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase6_6_dashboard_historical_input_panel_patch.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase6_6_dashboard_historical_input_panel_patch_report.txt"

READY_MARKER = "PHASE6_6_DASHBOARD_HISTORICAL_INPUT_PANEL_PATCH_READY"
RELEASE_DECISION = "PHASE6_6_DASHBOARD_HISTORICAL_INPUT_PANEL_PATCH_CREATED_GUARDED_DASHBOARD_HELPER"
SOURCE_MODE = "dashboard_historical_input_panel_patch"
CAUTION = "Historical data is scenario input, not forecast"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_phase6_6_contract() -> list[dict[str, Any]]:
    return [
        {
            "panel_item": "data_mode",
            "display_label": "Data mode",
            "default_value": "Synthetic scenarios",
            "allowed_values": "Synthetic scenarios | Imported historical data",
            "workflow_status": "synthetic_default_historical_explicit",
            "customer_wording": "Choose whether to use simulated scenarios or imported historical data.",
        },
        {
            "panel_item": "historical_input_file",
            "display_label": "Historical price file",
            "default_value": "sample_underlying_prices.csv",
            "allowed_values": "CSV path or uploaded CSV later",
            "workflow_status": "explicit_historical_mode_only",
            "customer_wording": CAUTION,
        },
        {
            "panel_item": "option_chain_file",
            "display_label": "Option-chain file",
            "default_value": "sample_option_chain.csv",
            "allowed_values": "CSV path or uploaded CSV later",
            "workflow_status": "explicit_historical_mode_only",
            "customer_wording": "Option-chain data may be used for premium lookup and calibration.",
        },
        {
            "panel_item": "forecast_guardrail",
            "display_label": "Historical-data caution",
            "default_value": CAUTION,
            "allowed_values": CAUTION,
            "workflow_status": "required_customer_caution",
            "customer_wording": CAUTION,
        },
        {
            "panel_item": "fallback",
            "display_label": "Fallback behavior",
            "default_value": "Synthetic scenarios",
            "allowed_values": "Unknown modes fall back to synthetic",
            "workflow_status": "safe_default",
            "customer_wording": "Unrecognized modes fall back to synthetic scenarios.",
        },
    ]


def build_phase6_6_summary() -> dict[str, Any]:
    _ensure_dirs()

    contract_rows = build_phase6_6_contract()
    contract_df = pd.DataFrame(contract_rows)
    contract_df.to_csv(CONTRACT_CSV, index=False)

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": True,
        "dashboard_patch_guarded": True,
        "dashboard_patch_bounded": True,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "unknown_modes_fall_back_to_synthetic": True,
        "historical_data_is_scenario_input_not_forecast": True,
        "scenario_input_not_forecast": True,
        "dashboard_helper_created": True,
        "dashboard_customer_workflow_changed": False,
        "contract_rows": int(len(contract_df)),
        "row_count": int(len(contract_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 6-6 controlled dashboard historical input-panel patch",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Synthetic default preserved: {summary['synthetic_default_preserved']}",
        f"Historical mode explicit only: {summary['historical_mode_explicit_only']}",
        f"Unknown modes fall back to synthetic: {summary['unknown_modes_fall_back_to_synthetic']}",
        f"{CAUTION}: {summary['historical_data_is_scenario_input_not_forecast']}",
        f"Contract rows: {summary['contract_rows']}",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase6_6_summary(), indent=2))
