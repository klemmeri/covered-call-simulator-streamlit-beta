"""
phase8_customer_access_model.py

Phase 8-4 customer access model.

This module is passive. It defines access-control options for the paid Covered
Call Simulator before any live authentication or payment integration is added.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

ACCESS_MODEL_CSV = OUTPUT_TABLE_DIR / "phase8_4_customer_access_model_options.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase8_4_customer_access_model_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase8_4_customer_access_model.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase8_4_customer_access_model_report.txt"

READY_MARKER = "PHASE8_4_CUSTOMER_ACCESS_MODEL_READY"
RELEASE_DECISION = "PHASE8_4_CUSTOMER_ACCESS_MODEL_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "customer_access_model"

RECOMMENDED_ACCESS_MODEL = "private beta access first; paid access integration later"
RECOMMENDED_BETA_MODEL = "manual invite list or password-gated hosted Streamlit MVP"
PAYMENT_STATUS = "not implemented in this checkpoint"



def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)



def build_phase8_4_access_options() -> list[dict[str, Any]]:
    return [
        {
            "access_model": "manual private beta list",
            "fit_for_mvp": "High",
            "complexity": "Low",
            "payment_ready": False,
            "customer_control": "Invite selected beta users manually",
            "advantages": "Fastest path; simplest support; useful for first feedback",
            "risks": "Not automated; not scalable for many customers",
            "recommended_first_step": True,
        },
        {
            "access_model": "password-gated hosted app",
            "fit_for_mvp": "High",
            "complexity": "Low/Medium",
            "payment_ready": False,
            "customer_control": "Share app URL and password with approved users",
            "advantages": "Simple access gate while keeping deployment lightweight",
            "risks": "Password sharing; limited account management",
            "recommended_first_step": True,
        },
        {
            "access_model": "Stripe payment link plus manual approval",
            "fit_for_mvp": "Medium/High",
            "complexity": "Medium",
            "payment_ready": True,
            "customer_control": "Customer pays externally; access enabled manually",
            "advantages": "Adds payment without a full account system",
            "risks": "Manual workflow; refund/support tracking needed",
            "recommended_first_step": False,
        },
        {
            "access_model": "full login and subscription system",
            "fit_for_mvp": "Medium",
            "complexity": "High",
            "payment_ready": True,
            "customer_control": "Automated account and subscription access",
            "advantages": "Best long-term SaaS model",
            "risks": "Large implementation burden before product validation",
            "recommended_first_step": False,
        },
        {
            "access_model": "local downloadable paid package",
            "fit_for_mvp": "Low/Medium",
            "complexity": "Medium",
            "payment_ready": True,
            "customer_control": "Customer downloads and runs locally",
            "advantages": "Avoids hosting account management",
            "risks": "Installation support burden; harder to protect paid access",
            "recommended_first_step": False,
        },
    ]



def build_phase8_4_summary() -> dict[str, Any]:
    _ensure_dirs()

    options = build_phase8_4_access_options()
    options_df = pd.DataFrame(options)
    options_df.to_csv(ACCESS_MODEL_CSV, index=False)

    recommended_count = int(options_df["recommended_first_step"].sum())

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "customer_access_model_created": True,
        "recommended_access_model": RECOMMENDED_ACCESS_MODEL,
        "recommended_beta_model": RECOMMENDED_BETA_MODEL,
        "payment_status": PAYMENT_STATUS,
        "payment_integration_not_implemented": True,
        "access_control_not_implemented": True,
        "manual_private_beta_supported": True,
        "password_gated_mvp_supported": True,
        "full_subscription_system_deferred": True,
        "streamlit_mvp_path_supported": True,
        "access_option_rows": int(len(options_df)),
        "recommended_first_step_count": recommended_count,
        "row_count": int(len(options_df)),
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "historical_data_is_scenario_input_not_forecast": True,
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "Phase 8-4 customer access model",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Recommended access model: {RECOMMENDED_ACCESS_MODEL}",
        f"Recommended beta model: {RECOMMENDED_BETA_MODEL}",
        f"Payment status: {PAYMENT_STATUS}",
        f"Access option rows: {len(options_df)}",
        f"Recommended first-step count: {recommended_count}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase8_4_summary(), indent=2))
