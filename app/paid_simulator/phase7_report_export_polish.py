"""
phase7_report_export_polish.py

Phase 7-4 report export polish.

This module is passive. It does not patch the dashboard or engine. It creates a
launch-readiness checklist for customer-facing report/table exports.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

CHECKLIST_CSV = OUTPUT_TABLE_DIR / "phase7_4_report_export_polish_checklist.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase7_4_report_export_polish_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase7_4_report_export_polish.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase7_4_report_export_polish_report.txt"

READY_MARKER = "PHASE7_4_REPORT_EXPORT_POLISH_READY"
RELEASE_DECISION = "PHASE7_4_REPORT_EXPORT_POLISH_CREATED_NO_DASHBOARD_CHANGE"
SOURCE_MODE = "report_export_polish"
CAUTION = "Historical data is scenario input, not forecast"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_phase7_4_export_checklist() -> list[dict[str, Any]]:
    return [
        {
            "export_area": "Scenario summary report",
            "launch_goal": "Provide a plain-English summary before technical tables.",
            "customer_value": "Customer understands what the run means without reading raw CSVs.",
            "required_for_launch": True,
            "patch_now": False,
        },
        {
            "export_area": "Input echo",
            "launch_goal": "Show the ticker, account size, risk tier, delta, DTE, data mode, and assumptions used.",
            "customer_value": "Customer can verify what was simulated.",
            "required_for_launch": True,
            "patch_now": False,
        },
        {
            "export_area": "Risk disclosure",
            "launch_goal": "Include concise options-risk and no-advice wording in exported reports.",
            "customer_value": "Customer sees risk context outside the app screen.",
            "required_for_launch": True,
            "patch_now": False,
        },
        {
            "export_area": "Historical-data caution",
            "launch_goal": "State that historical data is scenario input, not forecast.",
            "customer_value": "Customer does not misinterpret historical import as prediction.",
            "required_for_launch": True,
            "patch_now": False,
        },
        {
            "export_area": "Regime wording",
            "launch_goal": "Frame regimes as scenario guidance, not an oracle.",
            "customer_value": "Customer sees regime labels as probabilistic context.",
            "required_for_launch": True,
            "patch_now": False,
        },
        {
            "export_area": "Tables",
            "launch_goal": "Use stable column names, readable headers, and consistent units.",
            "customer_value": "Customer can compare runs without decoding internal field names.",
            "required_for_launch": True,
            "patch_now": False,
        },
        {
            "export_area": "Charts",
            "launch_goal": "Export chart-ready table files or image references where available.",
            "customer_value": "Customer can review visuals outside the dashboard.",
            "required_for_launch": False,
            "patch_now": False,
        },
        {
            "export_area": "File naming",
            "launch_goal": "Use predictable filenames under outputs/reports/paid_simulator and outputs/tables/paid_simulator.",
            "customer_value": "Customer and developer can find outputs reliably.",
            "required_for_launch": True,
            "patch_now": False,
        },
        {
            "export_area": "Commercial safety",
            "launch_goal": "Avoid guaranteed-profit, risk-free, advisory, or oracle-like language.",
            "customer_value": "Product remains commercially responsible.",
            "required_for_launch": True,
            "patch_now": False,
        },
    ]


def build_phase7_4_summary() -> dict[str, Any]:
    _ensure_dirs()

    checklist_rows = build_phase7_4_export_checklist()
    checklist_df = pd.DataFrame(checklist_rows)
    checklist_df.to_csv(CHECKLIST_CSV, index=False)

    total_rows = int(len(checklist_df))
    required_rows = int(checklist_df["required_for_launch"].sum())

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "report_export_polish_created": True,
        "checklist_rows": total_rows,
        "required_export_items": required_rows,
        "options_risk_wording_required": True,
        "financial_advice_disclaimer_required": True,
        "historical_data_is_scenario_input_not_forecast": True,
        "regime_detection_probabilistic_not_oracle": True,
        "no_guaranteed_profit_wording": True,
        "customer_readable_exports_required": True,
        "patch_now": False,
        "row_count": total_rows,
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report_lines = [
        "Phase 7-4 report export polish",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Checklist rows: {total_rows}",
        f"Required export items: {required_rows}",
        f"{CAUTION}: {summary['historical_data_is_scenario_input_not_forecast']}",
        f"Regime detection probabilistic, not oracle: {summary['regime_detection_probabilistic_not_oracle']}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase7_4_summary(), indent=2))
