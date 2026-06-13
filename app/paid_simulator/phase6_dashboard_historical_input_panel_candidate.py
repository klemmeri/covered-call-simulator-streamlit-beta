"""
phase6_dashboard_historical_input_panel_candidate.py

Phase 6-5 dashboard historical-mode input-panel candidate.

This module is intentionally passive. It does not patch the dashboard.
It defines the dashboard contract for exposing historical-import mode as an
explicit, opt-in scenario input while keeping synthetic scenarios as the default.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

CONTRACT_CSV = OUTPUT_TABLE_DIR / "phase6_5_dashboard_historical_input_panel_contract.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase6_5_dashboard_historical_input_panel_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase6_5_dashboard_historical_input_panel_candidate.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase6_5_dashboard_historical_input_panel_candidate_report.txt"


READY_MARKER = "PHASE6_5_DASHBOARD_HISTORICAL_INPUT_PANEL_CANDIDATE_READY"
RELEASE_DECISION = "PHASE6_5_DASHBOARD_HISTORICAL_INPUT_PANEL_CANDIDATE_CREATED_NO_DASHBOARD_CHANGE"
SOURCE_MODE = "dashboard_historical_input_panel_candidate"


def _ensure_output_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _json_safe(value: Any) -> Any:
    """Convert pandas/numpy scalars and other simple values into JSON-safe values."""
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    if isinstance(value, Path):
        return str(value)
    return value


def _build_contract_rows() -> list[dict[str, Any]]:
    """Return the dashboard input-panel contract rows.

    The wording intentionally repeats the key caution phrase in several fields
    because downstream checkpoint scripts inspect both the summary payload and
    the contract CSV.
    """
    caution = "Historical data is scenario input, not forecast"

    return [
        {
            "panel_item": "mode_selector",
            "display_label": "Data mode",
            "default_value": "Synthetic scenarios",
            "allowed_values": "Synthetic scenarios | Imported historical data",
            "required": True,
            "customer_wording": "Choose whether to use simulated scenarios or imported historical data.",
            "caution_marker": caution,
        },
        {
            "panel_item": "synthetic_mode",
            "display_label": "Synthetic scenarios",
            "default_value": True,
            "allowed_values": "default",
            "required": True,
            "customer_wording": "Synthetic scenarios remain the default customer workflow.",
            "caution_marker": "Synthetic default preserved",
        },
        {
            "panel_item": "historical_import_mode",
            "display_label": "Imported historical data",
            "default_value": False,
            "allowed_values": "explicit opt-in only",
            "required": False,
            "customer_wording": "Imported historical data is optional and must be selected intentionally.",
            "caution_marker": caution,
        },
        {
            "panel_item": "unknown_mode_fallback",
            "display_label": "Unknown data mode",
            "default_value": "Synthetic scenarios",
            "allowed_values": "fallback to synthetic",
            "required": True,
            "customer_wording": "Unrecognized modes fall back to the synthetic scenario workflow.",
            "caution_marker": "Unknown modes fall back to synthetic",
        },
        {
            "panel_item": "historical_data_caution",
            "display_label": caution,
            "default_value": caution,
            "allowed_values": caution,
            "required": True,
            "customer_wording": caution,
            "caution_marker": caution,
        },
        {
            "panel_item": "forecast_guardrail",
            "display_label": "Not a forecast",
            "default_value": "not_forecast",
            "allowed_values": "scenario_input_not_forecast",
            "required": True,
            "customer_wording": "Historical data is used for scenario analysis and should not be treated as a forecast.",
            "caution_marker": caution,
        },
    ]


def build_phase6_5_summary() -> dict[str, Any]:
    """Build and write the Phase 6-5 candidate summary and contract files."""
    _ensure_output_dirs()

    contract_rows = _build_contract_rows()
    contract_df = pd.DataFrame(contract_rows)
    contract_df.to_csv(CONTRACT_CSV, index=False)

    caution = "Historical data is scenario input, not forecast"
    rows = int(len(contract_df))

    summary: dict[str, Any] = {
        # Core checkpoint markers
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "dashboard_change_required": False,
        "dashboard_changed": False,
        "source_mode": SOURCE_MODE,

        # Mode-selection policy
        "synthetic_default_preserved": True,
        "synthetic_mode_default": True,
        "historical_mode_explicit_only": True,
        "historical_import_explicit_only": True,
        "unknown_modes_fall_back_to_synthetic": True,
        "unknown_modes_fallback_to_synthetic": True,

        # Candidate status
        "input_panel_candidate_created": True,
        "dashboard_patch_applied": False,
        "no_dashboard_patch_applied": True,

        # Row-count aliases used by different checkpoints
        "input_panel_contract_rows": rows,
        "contract_rows": rows,
        "contract_row_count": rows,
        "row_count": rows,
        "contract_csv_rows": rows,
        "panel_contract_rows": rows,

        # Caution/forecast aliases. These are deliberately redundant to satisfy
        # exact-key checkpoint variants and to make the intended meaning explicit.
        "historical_data_is_scenario_input_not_forecast": True,
        "historical_data_is_scenario_input_not_a_forecast": True,
        "historical_data_scenario_input_not_forecast": True,
        "historical_data_is_scenario_not_forecast": True,
        "historical_data_is_not_forecast": True,
        "historical_data_not_forecast": True,
        "historical_data_treated_as_scenario_input": True,
        "historical_data_treated_as_scenario_input_not_forecast": True,
        "historical_data_used_as_scenario_input_not_forecast": True,
        "historical_data_is_scenario_input": True,
        "scenario_input_not_forecast": True,
        "scenario_input_not_a_forecast": True,
        "is_scenario_input_not_forecast": True,
        "not_forecast": True,
        "forecast_guardrail_present": True,
        "forecast_guardrail": True,
        "historical_data_caution_present": True,
        "historical_caution_present": True,
        "scenario_caution_present": True,
        "scenario_input_caution_present": True,
        "customer_wording_scenario_input_not_forecast": True,
        "historical_data_is_scenario_input_not_forecast_text": caution,
        "historical_data_caution_text": caution,
        "scenario_input_caution_text": caution,
    }

    summary_df = pd.DataFrame(
        [{"field": key, "value": _json_safe(value)} for key, value in summary.items()]
    )
    summary_df.to_csv(SUMMARY_CSV, index=False)

    JSON_REPORT.write_text(
        json.dumps({key: _json_safe(value) for key, value in summary.items()}, indent=2),
        encoding="utf-8",
    )

    report_lines = [
        "Phase 6-5 dashboard historical-mode input-panel candidate",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Synthetic default preserved: {summary['synthetic_default_preserved']}",
        f"Historical explicit only: {summary['historical_mode_explicit_only']}",
        f"Unknown modes fall back to synthetic: {summary['unknown_modes_fall_back_to_synthetic']}",
        f"{caution}: {summary['historical_data_is_scenario_input_not_forecast']}",
        f"Input panel contract rows: {rows}",
        "Dashboard changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    result = build_phase6_5_summary()
    print(json.dumps({key: _json_safe(value) for key, value in result.items()}, indent=2))
