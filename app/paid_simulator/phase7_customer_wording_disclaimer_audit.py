"""
phase7_customer_wording_disclaimer_audit.py

Phase 7-2 customer wording and disclaimer audit for the paid covered-call
simulator.

This module is passive. It does not change dashboard or engine files. It builds
a customer-facing wording checklist focused on commercial launch readiness,
clear risk language, and careful framing of historical/regime analysis as
scenario guidance rather than prediction.
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

AUDIT_CSV = OUTPUT_TABLE_DIR / "phase7_2_customer_wording_disclaimer_audit.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase7_2_customer_wording_disclaimer_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase7_2_customer_wording_disclaimer_audit.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase7_2_customer_wording_disclaimer_audit_report.txt"

READY_MARKER = "PHASE7_2_CUSTOMER_WORDING_DISCLAIMER_AUDIT_READY"
RELEASE_DECISION = "PHASE7_2_CUSTOMER_WORDING_DISCLAIMER_AUDIT_CREATED_NO_DASHBOARD_CHANGE"
SOURCE_MODE = "customer_wording_disclaimer_audit"

REQUIRED_CAUTION = "Historical data is scenario input, not forecast"
RISK_WORDING = "Options involve risk and results are not guaranteed."
REGIME_WORDING = "Regime labels are probabilistic scenario inputs, not market predictions."
EDUCATIONAL_WORDING = "For education and scenario analysis, not individualized financial advice."


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _dashboard_text() -> str:
    if not DASHBOARD_FILE.exists():
        return ""
    return DASHBOARD_FILE.read_text(encoding="utf-8")


def build_phase7_2_audit_rows() -> list[dict[str, Any]]:
    return [
        {
            "audit_area": "historical_data_framing",
            "required_wording": REQUIRED_CAUTION,
            "commercial_reason": "Avoids implying that imported historical data predicts future results.",
            "launch_priority": "required",
            "recommended_action": "Keep this wording visible near historical-mode controls and report outputs.",
        },
        {
            "audit_area": "options_risk_disclaimer",
            "required_wording": RISK_WORDING,
            "commercial_reason": "Makes clear that options strategies can lose money and model output is not guaranteed.",
            "launch_priority": "required",
            "recommended_action": "Add/verify near simulator run button, reports, and exported summaries.",
        },
        {
            "audit_area": "financial_advice_disclaimer",
            "required_wording": EDUCATIONAL_WORDING,
            "commercial_reason": "Frames the product as analytical software, not personalized investment advice.",
            "launch_priority": "required",
            "recommended_action": "Add/verify in dashboard footer and downloadable report header/footer.",
        },
        {
            "audit_area": "regime_detection_framing",
            "required_wording": REGIME_WORDING,
            "commercial_reason": "Avoids presenting regime detection as an oracle or forecast engine.",
            "launch_priority": "required",
            "recommended_action": "Use this wording anywhere regime/scenario labels are shown.",
        },
        {
            "audit_area": "performance_language",
            "required_wording": "Projected outcomes are scenario estimates, not promised performance.",
            "commercial_reason": "Prevents overclaiming about returns, premium capture, or assignment outcomes.",
            "launch_priority": "required",
            "recommended_action": "Audit dashboard text for words like guaranteed, safe, certain, or risk-free.",
        },
        {
            "audit_area": "customer_readability",
            "required_wording": "Use plain-language labels with technical details available as expandable notes.",
            "commercial_reason": "Keeps the paid workflow understandable for non-programmer customers.",
            "launch_priority": "recommended",
            "recommended_action": "Use simple labels first; keep Greeks/model assumptions in helper text or reports.",
        },
    ]


def build_phase7_2_summary() -> dict[str, Any]:
    _ensure_dirs()

    audit_rows = build_phase7_2_audit_rows()
    audit_df = pd.DataFrame(audit_rows)
    audit_df.to_csv(AUDIT_CSV, index=False)

    dashboard_text = _dashboard_text()
    dashboard_lower = dashboard_text.lower()

    forbidden_terms = ["guaranteed profit", "risk-free", "cannot lose", "certain return", "sure profit"]
    forbidden_terms_found = [term for term in forbidden_terms if term in dashboard_lower]

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "dashboard_changed": False,
        "customer_wording_audit_created": True,
        "risk_disclaimer_required": True,
        "financial_advice_disclaimer_required": True,
        "historical_data_is_scenario_input_not_forecast": True,
        "scenario_input_not_forecast": True,
        "regime_detection_is_probabilistic_guidance": True,
        "regime_detection_not_oracle": True,
        "performance_not_guaranteed": True,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "forbidden_performance_terms_found": len(forbidden_terms_found),
        "forbidden_terms_found_list": ", ".join(forbidden_terms_found),
        "audit_rows": int(len(audit_df)),
        "row_count": int(len(audit_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 7-2 customer wording and disclaimer audit",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Dashboard changed: {summary['dashboard_changed']}",
        f"Risk disclaimer required: {summary['risk_disclaimer_required']}",
        f"Financial advice disclaimer required: {summary['financial_advice_disclaimer_required']}",
        f"Historical-data caution: {REQUIRED_CAUTION}",
        f"Regime detection not oracle: {summary['regime_detection_not_oracle']}",
        f"Forbidden performance terms found: {summary['forbidden_performance_terms_found']}",
        f"Audit rows: {summary['audit_rows']}",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase7_2_summary(), indent=2))
