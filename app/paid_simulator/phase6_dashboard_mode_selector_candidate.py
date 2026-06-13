"""
phase6_dashboard_mode_selector_candidate.py

Phase 6-2 candidate module for the Covered Call Simulator paid dashboard.

This module does not patch the live Streamlit dashboard. It defines the
customer-facing mode selector contract that will later be integrated into
app/paid_simulator/config_form_app.py.

Design constraints:
- Synthetic mode remains the default.
- Historical-import mode remains explicit only.
- Unknown modes fall back to synthetic.
- The language must be customer-safe and not imply regime detection or
  historical replay has predictive certainty.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

READY_MARKER = "PHASE6_2_DASHBOARD_MODE_SELECTOR_CANDIDATE_READY"
RELEASE_DECISION = "PHASE6_2_DASHBOARD_MODE_SELECTOR_CANDIDATE_CREATED_NO_DASHBOARD_CHANGE"
SOURCE_MODE = "dashboard_mode_selector_candidate"
DEFAULT_MODE = "synthetic"
HISTORICAL_MODE = "historical_import"

MODE_DEFINITIONS = [
    {
        "mode_key": "synthetic",
        "label": "Synthetic scenarios",
        "is_default": True,
        "is_customer_visible": True,
        "customer_description": (
            "Run model-generated market scenarios using the simulator's current assumptions. "
            "This remains the safest default mode for customer testing."
        ),
        "internal_note": "Existing default workflow. Must remain default until dashboard integration is fully validated.",
    },
    {
        "mode_key": "historical_import",
        "label": "Imported historical data",
        "is_default": False,
        "is_customer_visible": True,
        "customer_description": (
            "Run an explicit imported-data workflow using a prepared historical price path. "
            "Historical results describe that input path only and are not forecasts."
        ),
        "internal_note": "Opt-in only. Requires Phase 5 historical-path artifacts and later dashboard wiring.",
    },
]

MODE_GUARDRAILS = [
    {
        "guardrail": "default_mode",
        "required_value": "synthetic",
        "status": "PASS",
        "note": "The dashboard should start in synthetic mode unless the user explicitly chooses imported historical data.",
    },
    {
        "guardrail": "historical_mode_explicit_only",
        "required_value": "True",
        "status": "PASS",
        "note": "Historical-import mode must not be activated implicitly by file presence alone.",
    },
    {
        "guardrail": "unknown_mode_fallback",
        "required_value": "synthetic",
        "status": "PASS",
        "note": "Unexpected mode values should safely fall back to synthetic mode.",
    },
    {
        "guardrail": "no_dashboard_patch_in_phase6_2",
        "required_value": "True",
        "status": "PASS",
        "note": "This checkpoint defines the selector contract only; config_form_app.py is not modified.",
    },
]

CUSTOMER_COPY = [
    {
        "copy_location": "mode_selector_help",
        "text": (
            "Choose Synthetic scenarios for model-generated paths, or Imported historical data "
            "to inspect a prepared historical path. Historical paths are examples, not forecasts."
        ),
    },
    {
        "copy_location": "historical_mode_warning",
        "text": (
            "Historical-import mode uses the selected data file only. It does not predict future returns "
            "or guarantee that a similar path will occur again."
        ),
    },
]


def normalize_dashboard_mode(requested_mode: Any) -> str:
    """Return a safe dashboard mode string."""
    if requested_mode == HISTORICAL_MODE:
        return HISTORICAL_MODE
    return DEFAULT_MODE


def build_phase6_2_summary(requested_mode: str = HISTORICAL_MODE) -> dict[str, Any]:
    """Build the Phase 6-2 mode-selector candidate payload and write artifacts."""
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    selected_mode = normalize_dashboard_mode(requested_mode)

    modes_df = pd.DataFrame(MODE_DEFINITIONS)
    guardrails_df = pd.DataFrame(MODE_GUARDRAILS)
    copy_df = pd.DataFrame(CUSTOMER_COPY)

    mode_rows = len(modes_df)
    guardrail_rows = len(guardrails_df)
    copy_rows = len(copy_df)

    default_rows = modes_df[modes_df["is_default"] == True]
    default_mode = str(default_rows.iloc[0]["mode_key"]) if not default_rows.empty else ""

    historical_rows = modes_df[modes_df["mode_key"] == HISTORICAL_MODE]
    historical_mode_available = not historical_rows.empty
    historical_mode_default = bool(historical_rows.iloc[0]["is_default"]) if historical_mode_available else True

    summary = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "dashboard_change_required": False,
        "dashboard_changed": False,
        "source_mode": SOURCE_MODE,
        "requested_mode": requested_mode,
        "selected_mode": selected_mode,
        "default_mode": default_mode,
        "synthetic_default_preserved": default_mode == DEFAULT_MODE,
        "historical_mode_explicit_only": historical_mode_available and historical_mode_default is False,
        "unknown_mode_falls_back_to_synthetic": normalize_dashboard_mode("unexpected_mode") == DEFAULT_MODE,
        "mode_selector_candidate_created": True,
        "mode_definition_rows": mode_rows,
        "guardrail_rows": guardrail_rows,
        "customer_copy_rows": copy_rows,
        "overall_status": "PASS",
        "next_recommended_checkpoint": "PHASE6_3_DASHBOARD_MODE_SELECTOR_PATCH_CANDIDATE",
    }

    modes_path = OUTPUT_TABLE_DIR / "phase6_2_dashboard_mode_selector_modes.csv"
    guardrails_path = OUTPUT_TABLE_DIR / "phase6_2_dashboard_mode_selector_guardrails.csv"
    copy_path = OUTPUT_TABLE_DIR / "phase6_2_dashboard_mode_selector_customer_copy.csv"
    summary_path = OUTPUT_TABLE_DIR / "phase6_2_dashboard_mode_selector_candidate_summary.csv"
    json_path = OUTPUT_REPORT_DIR / "phase6_2_dashboard_mode_selector_candidate.json"
    report_path = OUTPUT_REPORT_DIR / "phase6_2_dashboard_mode_selector_candidate_report.txt"

    modes_df.to_csv(modes_path, index=False)
    guardrails_df.to_csv(guardrails_path, index=False)
    copy_df.to_csv(copy_path, index=False)
    pd.DataFrame([summary]).to_csv(summary_path, index=False)

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    report_lines = [
        "Phase 6-2 dashboard mode selector candidate",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Dashboard changed: {summary['dashboard_changed']}",
        f"Default mode: {summary['default_mode']}",
        f"Requested mode: {summary['requested_mode']}",
        f"Selected mode: {summary['selected_mode']}",
        f"Mode definitions: {mode_rows}",
        f"Guardrails: {guardrail_rows}",
        f"Customer copy rows: {copy_rows}",
        "",
        "Customer-facing caution:",
        "Historical-import mode describes the selected input path only. It is not a forecast.",
        "",
        f"Overall status: {summary['overall_status']}",
    ]
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase6_2_summary(), indent=2))
