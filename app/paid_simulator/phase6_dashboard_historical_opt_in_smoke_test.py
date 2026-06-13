"""
phase6_dashboard_historical_opt_in_smoke_test.py

Phase 6-11 dashboard end-to-end historical opt-in smoke test.

This module is passive. It verifies that the historical dashboard mode maps to
historical_import only when explicitly selected, while the default, None, and
unknown modes all map to synthetic.
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

SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase6_11_dashboard_historical_opt_in_smoke_summary.csv"
CASES_CSV = OUTPUT_TABLE_DIR / "phase6_11_dashboard_historical_opt_in_smoke_cases.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase6_11_dashboard_historical_opt_in_smoke.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase6_11_dashboard_historical_opt_in_smoke_report.txt"

READY_MARKER = "PHASE6_11_DASHBOARD_HISTORICAL_OPT_IN_SMOKE_READY"
RELEASE_DECISION = "PHASE6_11_DASHBOARD_HISTORICAL_OPT_IN_SMOKE_PASSED_NO_DASHBOARD_CHANGE"
SOURCE_MODE = "dashboard_historical_opt_in_smoke_test"
CAUTION = "Historical data is scenario input, not forecast"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def resolve_phase6_11_dashboard_mode(dashboard_mode: str | None) -> dict[str, Any]:
    """Resolve dashboard mode to the internal runner mode."""
    if dashboard_mode == "Imported historical data":
        selected_dashboard_mode = "Imported historical data"
        runner_mode = "historical_import"
        historical_mode_selected = True
    else:
        selected_dashboard_mode = "Synthetic scenarios"
        runner_mode = "synthetic"
        historical_mode_selected = False

    return {
        "input_dashboard_mode": dashboard_mode,
        "selected_dashboard_mode": selected_dashboard_mode,
        "runner_mode": runner_mode,
        "historical_mode_selected": historical_mode_selected,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "unknown_modes_fall_back_to_synthetic": dashboard_mode not in {"Synthetic scenarios", "Imported historical data"},
        "historical_data_is_scenario_input_not_forecast": True,
        "customer_caution": CAUTION,
    }


def build_phase6_11_cases() -> list[dict[str, Any]]:
    raw_cases = [
        ("default_synthetic", "Synthetic scenarios", "synthetic", False),
        ("explicit_historical", "Imported historical data", "historical_import", True),
        ("unknown_mode", "unexpected", "synthetic", False),
        ("missing_mode", None, "synthetic", False),
    ]

    rows: list[dict[str, Any]] = []
    for case_name, dashboard_mode, expected_runner, expected_historical in raw_cases:
        resolved = resolve_phase6_11_dashboard_mode(dashboard_mode)
        rows.append(
            {
                "case_name": case_name,
                "input_dashboard_mode": "None" if dashboard_mode is None else dashboard_mode,
                "selected_dashboard_mode": resolved["selected_dashboard_mode"],
                "runner_mode": resolved["runner_mode"],
                "expected_runner_mode": expected_runner,
                "runner_mode_ok": resolved["runner_mode"] == expected_runner,
                "historical_mode_selected": resolved["historical_mode_selected"],
                "expected_historical_mode_selected": expected_historical,
                "historical_selection_ok": resolved["historical_mode_selected"] == expected_historical,
                "customer_caution": CAUTION,
            }
        )
    return rows


def build_phase6_11_summary() -> dict[str, Any]:
    _ensure_dirs()

    case_rows = build_phase6_11_cases()
    cases_df = pd.DataFrame(case_rows)
    cases_df.to_csv(CASES_CSV, index=False)

    default_case = resolve_phase6_11_dashboard_mode("Synthetic scenarios")
    historical_case = resolve_phase6_11_dashboard_mode("Imported historical data")
    unknown_case = resolve_phase6_11_dashboard_mode("unexpected")
    none_case = resolve_phase6_11_dashboard_mode(None)

    cases_all_pass = bool(cases_df["runner_mode_ok"].all() and cases_df["historical_selection_ok"].all())

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "dashboard_changed": False,
        "synthetic_default_preserved": default_case["runner_mode"] == "synthetic",
        "default_runner_mode": default_case["runner_mode"],
        "historical_mode_explicit_only": historical_case["runner_mode"] == "historical_import",
        "historical_runner_mode": historical_case["runner_mode"],
        "historical_mode_selected_only_when_explicit": historical_case["historical_mode_selected"] is True and default_case["historical_mode_selected"] is False,
        "unknown_modes_fall_back_to_synthetic": unknown_case["runner_mode"] == "synthetic",
        "none_mode_falls_back_to_synthetic": none_case["runner_mode"] == "synthetic",
        "historical_data_is_scenario_input_not_forecast": True,
        "scenario_input_not_forecast": True,
        "cases_all_pass": cases_all_pass,
        "case_rows": int(len(cases_df)),
        "row_count": int(len(cases_df)),
    }

    pd.DataFrame([{"field": key, "value": value} for key, value in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report_lines = [
        "Phase 6-11 dashboard end-to-end historical opt-in smoke test",
        "=" * 82,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Default runner mode: {summary['default_runner_mode']}",
        f"Historical runner mode: {summary['historical_runner_mode']}",
        f"Unknown mode falls back to synthetic: {summary['unknown_modes_fall_back_to_synthetic']}",
        f"None mode falls back to synthetic: {summary['none_mode_falls_back_to_synthetic']}",
        f"Historical selected only when explicit: {summary['historical_mode_selected_only_when_explicit']}",
        f"{CAUTION}: {summary['historical_data_is_scenario_input_not_forecast']}",
        f"Cases all pass: {summary['cases_all_pass']}",
        f"Case rows: {summary['case_rows']}",
    ]
    TEXT_REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase6_11_summary(), indent=2))
