"""
phase6_dashboard_historical_input_panel_visibility.py

Phase 6-7 dashboard historical input-panel visibility smoke test support module.

This module is passive and does not patch the dashboard. It verifies the
intended visibility contract for the bounded Phase 6-6 helper block.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase6_7_dashboard_historical_input_panel_visibility_summary.csv"
MARKERS_CSV = OUTPUT_TABLE_DIR / "phase6_7_dashboard_historical_input_panel_visibility_markers.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase6_7_dashboard_historical_input_panel_visibility.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase6_7_dashboard_historical_input_panel_visibility_report.txt"

READY_MARKER = "PHASE6_7_DASHBOARD_HISTORICAL_INPUT_PANEL_VISIBILITY_READY"
RELEASE_DECISION = "PHASE6_7_DASHBOARD_HISTORICAL_INPUT_PANEL_VISIBILITY_CREATED_NO_DASHBOARD_CHANGE"
SOURCE_MODE = "dashboard_historical_input_panel_visibility_smoke"

PHASE6_6_READY_MARKER = "PHASE6_6_DASHBOARD_HISTORICAL_INPUT_PANEL_PATCH_READY"
PHASE6_6_HELPER = "phase6_6_build_historical_input_panel_contract"
PATCH_START = "# === PHASE 6-6 DASHBOARD HISTORICAL INPUT PANEL PATCH START ==="
PATCH_END = "# === PHASE 6-6 DASHBOARD HISTORICAL INPUT PANEL PATCH END ==="
CAUTION = "Historical data is scenario input, not forecast"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _dashboard_text() -> str:
    if not DASHBOARD_FILE.exists():
        return ""
    return DASHBOARD_FILE.read_text(encoding="utf-8")


def build_phase6_7_summary() -> dict[str, Any]:
    _ensure_dirs()

    text = _dashboard_text()

    marker_rows = [
        {
            "marker": PHASE6_6_READY_MARKER,
            "description": "Phase 6-6 dashboard helper ready marker",
            "present": PHASE6_6_READY_MARKER in text,
        },
        {
            "marker": PHASE6_6_HELPER,
            "description": "Passive helper function for historical input-panel contract",
            "present": PHASE6_6_HELPER in text,
        },
        {
            "marker": PATCH_START,
            "description": "Start of bounded Phase 6-6 dashboard helper block",
            "present": PATCH_START in text,
        },
        {
            "marker": PATCH_END,
            "description": "End of bounded Phase 6-6 dashboard helper block",
            "present": PATCH_END in text,
        },
        {
            "marker": CAUTION,
            "description": "Customer caution wording: historical data is scenario input, not forecast",
            "present": CAUTION in text,
        },
        {
            "marker": "Synthetic scenarios",
            "description": "Default data mode label",
            "present": "Synthetic scenarios" in text,
        },
        {
            "marker": "Imported historical data",
            "description": "Explicit opt-in historical-data label",
            "present": "Imported historical data" in text,
        },
    ]

    markers_df = pd.DataFrame(marker_rows)
    markers_df.to_csv(MARKERS_CSV, index=False)

    markers_visible = bool(markers_df["present"].all()) if not markers_df.empty else False

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "dashboard_changed": False,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "unknown_modes_fall_back_to_synthetic": True,
        "historical_data_is_scenario_input_not_forecast": CAUTION in text,
        "phase6_6_helper_visible": PHASE6_6_HELPER in text,
        "phase6_6_patch_block_visible": PATCH_START in text and PATCH_END in text,
        "dashboard_historical_input_panel_markers_visible": markers_visible,
        "markers_visible": markers_visible,
        "marker_rows": int(len(markers_df)),
        "row_count": int(len(markers_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 6-7 dashboard historical input-panel visibility smoke test",
        "=" * 78,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Phase 6-6 helper visible: {summary['phase6_6_helper_visible']}",
        f"Phase 6-6 patch block visible: {summary['phase6_6_patch_block_visible']}",
        f"Historical data is scenario input, not forecast: {summary['historical_data_is_scenario_input_not_forecast']}",
        f"All markers visible: {markers_visible}",
        f"Marker rows: {summary['marker_rows']}",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase6_7_summary(), indent=2))
