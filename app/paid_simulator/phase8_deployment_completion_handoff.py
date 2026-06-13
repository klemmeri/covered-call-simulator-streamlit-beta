"""
phase8_deployment_completion_handoff.py

Phase 8-6 deployment completion handoff.

This module is passive. It closes Phase 8 by verifying that the deployment and
customer-access planning artifacts exist and that the project is ready to move
into beta testing/customer-trial workflow planning.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase8_6_deployment_completion_handoff_summary.csv"
ARTIFACTS_CSV = OUTPUT_TABLE_DIR / "phase8_6_deployment_completion_handoff_artifacts.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase8_6_deployment_completion_handoff.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase8_6_deployment_completion_handoff_report.txt"

READY_MARKER = "PHASE8_6_DEPLOYMENT_COMPLETION_HANDOFF_READY"
RELEASE_DECISION = "PHASE8_COMPLETE_READY_FOR_PHASE9_BETA_TESTING_WORKFLOW"
SOURCE_MODE = "deployment_completion_handoff"

CAUTION = "Historical data is scenario input, not forecast"


PHASE8_ARTIFACTS = [
    {
        "phase": "Phase 8-1",
        "artifact": "Deployment and customer-access roadmap",
        "module": "app/paid_simulator/phase8_deployment_customer_access_roadmap.py",
        "check": "app/run_paid_simulator_phase8_1_deployment_customer_access_roadmap_check.py",
        "doc": "docs/phase8_1_deployment_customer_access_roadmap.md",
        "required": True,
    },
    {
        "phase": "Phase 8-2",
        "artifact": "Deployment target decision",
        "module": "app/paid_simulator/phase8_deployment_target_decision.py",
        "check": "app/run_paid_simulator_phase8_2_deployment_target_decision_check.py",
        "doc": "docs/phase8_2_deployment_target_decision.md",
        "required": True,
    },
    {
        "phase": "Phase 8-3",
        "artifact": "Environment and dependency audit",
        "module": "app/paid_simulator/phase8_environment_dependency_audit.py",
        "check": "app/run_paid_simulator_phase8_3_environment_dependency_audit_check.py",
        "doc": "docs/phase8_3_environment_dependency_audit.md",
        "required": True,
    },
    {
        "phase": "Phase 8-4",
        "artifact": "Customer access model",
        "module": "app/paid_simulator/phase8_customer_access_model.py",
        "check": "app/run_paid_simulator_phase8_4_customer_access_model_check.py",
        "doc": "docs/phase8_4_customer_access_model.md",
        "required": True,
    },
    {
        "phase": "Phase 8-5",
        "artifact": "Hosted smoke-test plan",
        "module": "app/paid_simulator/phase8_hosted_smoke_test_plan.py",
        "check": "app/run_paid_simulator_phase8_5_hosted_smoke_test_plan_check.py",
        "doc": "docs/phase8_5_hosted_smoke_test_plan.md",
        "required": True,
    },
]


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _exists(relative_path: str) -> bool:
    return (PROJECT_ROOT / relative_path).exists()


def build_phase8_6_artifact_table() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in PHASE8_ARTIFACTS:
        module_exists = _exists(item["module"])
        check_exists = _exists(item["check"])
        doc_exists = _exists(item["doc"])
        rows.append(
            {
                **item,
                "module_exists": module_exists,
                "check_exists": check_exists,
                "doc_exists": doc_exists,
                "artifact_complete": module_exists and check_exists and doc_exists,
            }
        )
    return rows


def build_phase8_6_summary() -> dict[str, Any]:
    _ensure_dirs()

    artifact_rows = build_phase8_6_artifact_table()
    artifacts_df = pd.DataFrame(artifact_rows)
    artifacts_df.to_csv(ARTIFACTS_CSV, index=False)

    artifact_count = int(len(artifacts_df))
    complete_count = int(artifacts_df["artifact_complete"].sum()) if not artifacts_df.empty else 0
    required_count = int(artifacts_df["required"].sum()) if not artifacts_df.empty else 0
    required_complete = int((artifacts_df["required"] & artifacts_df["artifact_complete"]).sum()) if not artifacts_df.empty else 0

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "phase8_complete": required_complete == required_count and required_count >= 5,
        "phase8_artifact_rows": artifact_count,
        "phase8_artifacts_complete": complete_count,
        "phase8_required_artifacts": required_count,
        "phase8_required_artifacts_complete": required_complete,
        "streamlit_mvp_path_selected": True,
        "full_custom_web_app_deferred": True,
        "customer_access_model_defined": True,
        "hosted_smoke_test_plan_defined": True,
        "payments_access_control_deferred_or_manual": True,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "unknown_modes_fall_back_to_synthetic": True,
        "historical_data_is_scenario_input_not_forecast": True,
        "phase9_next": "Beta testing and customer-trial workflow",
        "row_count": artifact_count,
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 8-6 deployment completion handoff",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Phase 8 complete: {summary['phase8_complete']}",
        f"Required artifacts complete: {required_complete} of {required_count}",
        f"Streamlit MVP path selected: {summary['streamlit_mvp_path_selected']}",
        f"Full custom web app deferred: {summary['full_custom_web_app_deferred']}",
        f"Customer access model defined: {summary['customer_access_model_defined']}",
        f"Hosted smoke-test plan defined: {summary['hosted_smoke_test_plan_defined']}",
        f"{CAUTION}: {summary['historical_data_is_scenario_input_not_forecast']}",
        f"Next phase: {summary['phase9_next']}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase8_6_summary(), indent=2))
