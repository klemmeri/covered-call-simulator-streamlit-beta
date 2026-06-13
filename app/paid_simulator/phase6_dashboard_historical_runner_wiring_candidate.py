"""
phase6_dashboard_historical_runner_wiring_candidate.py

Phase 6-8 dashboard historical-mode runner wiring candidate.

This module is passive. It defines and validates the future dashboard-to-runner
wiring contract before patching the live dashboard runner path.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase6_8_dashboard_historical_runner_wiring_candidate_summary.csv"
CONTRACT_CSV = OUTPUT_TABLE_DIR / "phase6_8_dashboard_historical_runner_wiring_candidate_contract.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase6_8_dashboard_historical_runner_wiring_candidate.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase6_8_dashboard_historical_runner_wiring_candidate_report.txt"

READY_MARKER = "PHASE6_8_DASHBOARD_HISTORICAL_RUNNER_WIRING_CANDIDATE_READY"
RELEASE_DECISION = "PHASE6_8_DASHBOARD_HISTORICAL_RUNNER_WIRING_CANDIDATE_CREATED_NO_DASHBOARD_CHANGE"
SOURCE_MODE = "dashboard_historical_runner_wiring_candidate"
CAUTION = "Historical data is scenario input, not forecast"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_phase6_8_contract() -> list[dict[str, Any]]:
    return [
        {
            "wire": "dashboard_data_mode_to_engine_mode",
            "dashboard_input": "Synthetic scenarios",
            "runner_value": "synthetic",
            "default": True,
            "guardrail": "Synthetic mode remains the default.",
        },
        {
            "wire": "dashboard_data_mode_to_engine_mode",
            "dashboard_input": "Imported historical data",
            "runner_value": "historical_import",
            "default": False,
            "guardrail": "Historical mode is explicit opt-in only.",
        },
        {
            "wire": "unknown_mode_fallback",
            "dashboard_input": "unknown",
            "runner_value": "synthetic",
            "default": True,
            "guardrail": "Unknown modes fall back to synthetic.",
        },
        {
            "wire": "historical_price_source",
            "dashboard_input": "Historical price file",
            "runner_value": "inputs/market_data/sample_underlying_prices.csv",
            "default": False,
            "guardrail": CAUTION,
        },
        {
            "wire": "option_chain_source",
            "dashboard_input": "Option-chain file",
            "runner_value": "inputs/market_data/sample_option_chain.csv",
            "default": False,
            "guardrail": "Option-chain input is used as premium lookup/calibration input.",
        },
        {
            "wire": "customer_caution",
            "dashboard_input": "Historical-data caution",
            "runner_value": CAUTION,
            "default": True,
            "guardrail": CAUTION,
        },
    ]


def resolve_phase6_8_runner_mode(dashboard_mode: str | None) -> dict[str, Any]:
    """Resolve a dashboard mode label into a guarded runner contract."""
    if dashboard_mode == "Imported historical data":
        selected = "historical_import"
        label = "Imported historical data"
    else:
        selected = "synthetic"
        label = "Synthetic scenarios"

    return {
        "dashboard_mode": label,
        "runner_mode": selected,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "unknown_modes_fall_back_to_synthetic": dashboard_mode not in {"Synthetic scenarios", "Imported historical data"},
        "historical_data_is_scenario_input_not_forecast": True,
        "customer_caution": CAUTION,
    }


def build_phase6_8_summary() -> dict[str, Any]:
    _ensure_dirs()

    contract_rows = build_phase6_8_contract()
    contract_df = pd.DataFrame(contract_rows)
    contract_df.to_csv(CONTRACT_CSV, index=False)

    synthetic_resolution = resolve_phase6_8_runner_mode("Synthetic scenarios")
    historical_resolution = resolve_phase6_8_runner_mode("Imported historical data")
    unknown_resolution = resolve_phase6_8_runner_mode("bad_mode")

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "dashboard_changed": False,
        "dashboard_runner_wiring_candidate_created": True,
        "synthetic_default_preserved": synthetic_resolution["runner_mode"] == "synthetic",
        "historical_mode_explicit_only": historical_resolution["runner_mode"] == "historical_import",
        "unknown_modes_fall_back_to_synthetic": unknown_resolution["runner_mode"] == "synthetic",
        "historical_data_is_scenario_input_not_forecast": True,
        "scenario_input_not_forecast": True,
        "synthetic_runner_mode": synthetic_resolution["runner_mode"],
        "historical_runner_mode": historical_resolution["runner_mode"],
        "unknown_runner_mode": unknown_resolution["runner_mode"],
        "contract_rows": int(len(contract_df)),
        "row_count": int(len(contract_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 6-8 dashboard historical-mode runner wiring candidate",
        "=" * 76,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Synthetic runner mode: {summary['synthetic_runner_mode']}",
        f"Historical runner mode: {summary['historical_runner_mode']}",
        f"Unknown runner mode: {summary['unknown_runner_mode']}",
        f"{CAUTION}: {summary['historical_data_is_scenario_input_not_forecast']}",
        f"Contract rows: {summary['contract_rows']}",
        "Dashboard changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase6_8_summary(), indent=2))
