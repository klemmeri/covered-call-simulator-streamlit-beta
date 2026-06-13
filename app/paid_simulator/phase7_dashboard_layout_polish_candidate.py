"""
phase7_dashboard_layout_polish_candidate.py

Phase 7-3 dashboard layout polish candidate.

This module is passive. It does not patch the dashboard. It creates a
customer-facing layout-polish checklist for the paid simulator.
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

CHECKLIST_CSV = OUTPUT_TABLE_DIR / "phase7_3_dashboard_layout_polish_checklist.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase7_3_dashboard_layout_polish_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase7_3_dashboard_layout_polish_candidate.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase7_3_dashboard_layout_polish_candidate_report.txt"

READY_MARKER = "PHASE7_3_DASHBOARD_LAYOUT_POLISH_CANDIDATE_READY"
RELEASE_DECISION = "PHASE7_3_DASHBOARD_LAYOUT_POLISH_CANDIDATE_CREATED_NO_DASHBOARD_CHANGE"
SOURCE_MODE = "dashboard_layout_polish_candidate"

CAUTION = "Historical data is scenario input, not forecast"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _dashboard_text() -> str:
    if not DASHBOARD_FILE.exists():
        return ""
    return DASHBOARD_FILE.read_text(encoding="utf-8")


def build_phase7_3_layout_checklist() -> list[dict[str, Any]]:
    return [
        {
            "section": "Header",
            "layout_goal": "Clear product title and concise customer promise.",
            "customer_value": "The customer understands this is a covered-call simulator.",
            "required_for_launch": True,
            "patch_now": False,
        },
        {
            "section": "Setup inputs",
            "layout_goal": "Keep ticker, account size, risk tier, target delta, and DTE grouped together.",
            "customer_value": "The customer can configure a scenario without hunting through the page.",
            "required_for_launch": True,
            "patch_now": False,
        },
        {
            "section": "Data mode",
            "layout_goal": "Show synthetic scenarios as the default and historical import as explicit opt-in.",
            "customer_value": "The customer cannot accidentally treat historical data as a forecast.",
            "required_for_launch": True,
            "patch_now": False,
        },
        {
            "section": "Results summary",
            "layout_goal": "Show plain-English interpretation before detailed tables.",
            "customer_value": "The customer understands the practical meaning of the simulation.",
            "required_for_launch": True,
            "patch_now": False,
        },
        {
            "section": "Risk language",
            "layout_goal": "Keep risk/disclaimer language visible but not overwhelming.",
            "customer_value": "The customer sees that covered calls have tradeoffs and risks.",
            "required_for_launch": True,
            "patch_now": False,
        },
        {
            "section": "Charts",
            "layout_goal": "Place payoff/strategy visuals near the relevant scenario summary.",
            "customer_value": "The customer can connect the chart to the setup they entered.",
            "required_for_launch": True,
            "patch_now": False,
        },
        {
            "section": "Exports",
            "layout_goal": "Make report/table exports easy to find after running a scenario.",
            "customer_value": "The customer can save or review the output outside the dashboard.",
            "required_for_launch": False,
            "patch_now": False,
        },
        {
            "section": "Commercial wording",
            "layout_goal": "Avoid guaranteed-profit, risk-free, oracle, or advisory wording.",
            "customer_value": "The product is presented responsibly and commercially safely.",
            "required_for_launch": True,
            "patch_now": False,
        },
    ]


def build_phase7_3_summary() -> dict[str, Any]:
    _ensure_dirs()

    dashboard_text = _dashboard_text()
    checklist_rows = build_phase7_3_layout_checklist()
    checklist_df = pd.DataFrame(checklist_rows)
    checklist_df.to_csv(CHECKLIST_CSV, index=False)

    required_items = int(checklist_df["required_for_launch"].sum())
    total_items = int(len(checklist_df))

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "dashboard_changed": False,
        "layout_polish_candidate_created": True,
        "checklist_rows": total_items,
        "required_layout_items": required_items,
        "synthetic_default_preserved": "Synthetic scenarios" in dashboard_text,
        "historical_mode_explicit_only": "Imported historical data" in dashboard_text,
        "historical_data_is_scenario_input_not_forecast": CAUTION in dashboard_text,
        "phase6_runner_wiring_visible": "phase6_9_resolve_dashboard_runner_mode" in dashboard_text,
        "commercial_wording_audit_continues": True,
        "patch_now": False,
        "row_count": total_items,
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 7-3 dashboard layout polish candidate",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Checklist rows: {total_items}",
        f"Required layout items: {required_items}",
        f"Synthetic default preserved: {summary['synthetic_default_preserved']}",
        f"Historical explicit opt-in visible: {summary['historical_mode_explicit_only']}",
        f"{CAUTION}: {summary['historical_data_is_scenario_input_not_forecast']}",
        "Dashboard changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase7_3_summary(), indent=2))
