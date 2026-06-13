"""
phase7_website_integration_plan.py

Phase 7-5 website integration plan.

This module is passive. It creates a commercial website integration checklist
for the Covered Call Simulator without changing the dashboard or engine.
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

CHECKLIST_CSV = OUTPUT_TABLE_DIR / "phase7_5_website_integration_plan_checklist.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase7_5_website_integration_plan_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase7_5_website_integration_plan.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase7_5_website_integration_plan_report.txt"

READY_MARKER = "PHASE7_5_WEBSITE_INTEGRATION_PLAN_READY"
RELEASE_DECISION = "PHASE7_5_WEBSITE_INTEGRATION_PLAN_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "website_integration_plan"

CAUTION = "Historical data is scenario input, not forecast"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _dashboard_text() -> str:
    if not DASHBOARD_FILE.exists():
        return ""
    return DASHBOARD_FILE.read_text(encoding="utf-8")


def build_phase7_5_website_checklist() -> list[dict[str, Any]]:
    return [
        {
            "area": "Landing page",
            "integration_goal": "Explain the product in plain language before asking for payment.",
            "customer_requirement": "Customer understands that this is a covered-call scenario simulator.",
            "launch_required": True,
            "implementation_phase": "Phase 8 or website build",
        },
        {
            "area": "Product positioning",
            "integration_goal": "Present the tool as decision support, not financial advice.",
            "customer_requirement": "No implied recommendation, guarantee, or risk-free claim.",
            "launch_required": True,
            "implementation_phase": "Phase 8 or website build",
        },
        {
            "area": "Dashboard embedding",
            "integration_goal": "Decide whether the Streamlit dashboard is embedded, linked, or rebuilt in a web framework.",
            "customer_requirement": "Customer can reach the simulator with minimal friction.",
            "launch_required": True,
            "implementation_phase": "Phase 8 or website build",
        },
        {
            "area": "Access control",
            "integration_goal": "Define free preview versus paid simulator access.",
            "customer_requirement": "Customer gets the right version after purchase or login.",
            "launch_required": True,
            "implementation_phase": "Phase 8 or payment/auth build",
        },
        {
            "area": "Payments",
            "integration_goal": "Choose subscription, one-time purchase, or gated member access.",
            "customer_requirement": "Payment flow is simple and commercially appropriate.",
            "launch_required": True,
            "implementation_phase": "Phase 8 or payment/auth build",
        },
        {
            "area": "Disclaimers",
            "integration_goal": "Keep options-risk and no-advice language visible on the website and inside reports.",
            "customer_requirement": "Customer sees responsible risk language before using results.",
            "launch_required": True,
            "implementation_phase": "Phase 7 wording plus website build",
        },
        {
            "area": "Historical data wording",
            "integration_goal": "Keep historical data framed as scenario input, not a forecast.",
            "customer_requirement": "Customer does not treat imported history as predictive certainty.",
            "launch_required": True,
            "implementation_phase": "Phase 7 wording plus website build",
        },
        {
            "area": "Regime wording",
            "integration_goal": "Frame regime detection as probabilistic guidance, not an oracle.",
            "customer_requirement": "Customer understands regime labels are scenario assumptions or diagnostics.",
            "launch_required": True,
            "implementation_phase": "Phase 7 wording plus website build",
        },
        {
            "area": "Support and documentation",
            "integration_goal": "Provide a simple getting-started page and sample interpretation guide.",
            "customer_requirement": "Customer knows what inputs to enter and how to interpret outputs.",
            "launch_required": False,
            "implementation_phase": "Phase 8 or documentation build",
        },
        {
            "area": "Backup and release management",
            "integration_goal": "Keep milestone zip backups before website deployment.",
            "customer_requirement": "Stable rollback point exists if launch work breaks the app.",
            "launch_required": True,
            "implementation_phase": "Before Phase 8 implementation",
        },
    ]


def build_phase7_5_summary() -> dict[str, Any]:
    _ensure_dirs()

    dashboard_text = _dashboard_text()
    checklist_rows = build_phase7_5_website_checklist()
    checklist_df = pd.DataFrame(checklist_rows)
    checklist_df.to_csv(CHECKLIST_CSV, index=False)

    required_items = int(checklist_df["launch_required"].sum())
    total_items = int(len(checklist_df))

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "dashboard_changed": False,
        "engine_changed": False,
        "website_integration_plan_created": True,
        "checklist_rows": total_items,
        "launch_required_items": required_items,
        "synthetic_default_preserved": "Synthetic scenarios" in dashboard_text,
        "historical_mode_explicit_only": "Imported historical data" in dashboard_text,
        "historical_data_is_scenario_input_not_forecast": CAUTION in dashboard_text,
        "regime_detection_not_oracle_required": True,
        "no_financial_advice_language_required": True,
        "options_risk_language_required": True,
        "next_phase_recommendation": "Phase 7-6 completion handoff, then Phase 8 website/build implementation",
        "row_count": total_items,
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 7-5 website integration plan",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Checklist rows: {total_items}",
        f"Launch-required items: {required_items}",
        f"Synthetic default preserved: {summary['synthetic_default_preserved']}",
        f"Historical explicit opt-in visible: {summary['historical_mode_explicit_only']}",
        f"{CAUTION}: {summary['historical_data_is_scenario_input_not_forecast']}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase7_5_summary(), indent=2))
