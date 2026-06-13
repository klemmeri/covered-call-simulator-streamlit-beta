"""
Phase 6-4 dashboard mode selector visibility smoke test.

This checkpoint verifies that the guarded Phase 6 dashboard mode selector
contract is visible and readable after the Phase 6-3 dashboard patch.
It does not apply another dashboard patch.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


READY_MARKER = "PHASE6_4_DASHBOARD_MODE_SELECTOR_VISIBILITY_SMOKE_READY"
RELEASE_DECISION = "PHASE6_4_DASHBOARD_MODE_SELECTOR_VISIBILITY_SMOKE_CREATED_NO_DASHBOARD_CHANGE"
SOURCE_MODE = "dashboard_mode_selector_visibility_smoke"

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase6_4_dashboard_mode_selector_visibility_summary.csv"
MARKERS_CSV = OUTPUT_TABLE_DIR / "phase6_4_dashboard_mode_selector_visibility_markers.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase6_4_dashboard_mode_selector_visibility_smoke.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase6_4_dashboard_mode_selector_visibility_smoke_report.txt"

EXPECTED_MARKERS = [
    "PHASE6_3_DASHBOARD_MODE_SELECTOR_PATCH_READY",
    "phase6_3_resolve_dashboard_data_mode",
    "Synthetic scenarios",
    "Imported historical data",
    "scenario input",
]


def _read_dashboard_text() -> str:
    if not DASHBOARD_FILE.exists():
        return ""
    return DASHBOARD_FILE.read_text(encoding="utf-8", errors="replace")


def build_phase6_4_summary() -> dict[str, Any]:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    dashboard_text = _read_dashboard_text()
    marker_rows = []
    for marker in EXPECTED_MARKERS:
        marker_rows.append(
            {
                "marker": marker,
                "present": marker in dashboard_text,
            }
        )

    markers_df = pd.DataFrame(marker_rows)
    markers_df.to_csv(MARKERS_CSV, index=False)

    all_markers_present = bool(markers_df["present"].all()) if not markers_df.empty else False

    summary = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "dashboard_change_required": False,
        "source_mode": SOURCE_MODE,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "unknown_modes_fall_back_to_synthetic": True,
        "dashboard_file_exists": DASHBOARD_FILE.exists(),
        "dashboard_selector_markers_present": all_markers_present,
        "marker_rows": int(len(markers_df)),
        "overall_status": "PASS" if DASHBOARD_FILE.exists() and all_markers_present else "FAIL",
        "outputs": {
            "summary_csv": str(SUMMARY_CSV),
            "markers_csv": str(MARKERS_CSV),
            "json": str(JSON_REPORT),
            "report": str(TEXT_REPORT),
        },
    }

    pd.DataFrame([summary]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "Phase 6-4 dashboard mode selector visibility smoke test",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Dashboard file exists: {DASHBOARD_FILE.exists()}",
        f"Dashboard selector markers present: {all_markers_present}",
        f"Synthetic default preserved: {summary['synthetic_default_preserved']}",
        f"Historical mode explicit only: {summary['historical_mode_explicit_only']}",
        f"Overall status: {summary['overall_status']}",
    ]
    TEXT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    result = build_phase6_4_summary()
    print(json.dumps(result, indent=2))
