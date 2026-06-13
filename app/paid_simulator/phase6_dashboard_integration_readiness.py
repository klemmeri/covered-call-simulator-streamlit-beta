"""
phase6_dashboard_integration_readiness.py

Phase 6-1 readiness map for dashboard integration in the Covered Call Simulator.

This module is intentionally add-only. It does not modify the Streamlit dashboard.
It maps how the paid dashboard should eventually expose synthetic mode and
historical-import mode while preserving the current synthetic default.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
PHASE5_HANDOFF_REPORT = OUTPUT_REPORT_DIR / "phase5_20_completion_handoff_report.txt"

READY_MARKER = "PHASE6_1_DASHBOARD_INTEGRATION_READINESS_READY"
RELEASE_DECISION = "PHASE6_1_DASHBOARD_INTEGRATION_READINESS_CREATED_NO_DASHBOARD_CHANGE"


def _ensure_output_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _artifact_status_rows() -> list[dict[str, Any]]:
    artifacts = [
        {
            "artifact": "paid_dashboard",
            "path": str(DASHBOARD_FILE),
            "required_for_phase6": True,
            "purpose": "Existing paid Streamlit dashboard to be integrated in later Phase 6 checkpoints.",
        },
        {
            "artifact": "phase5_completion_handoff_report",
            "path": str(PHASE5_HANDOFF_REPORT),
            "required_for_phase6": True,
            "purpose": "Confirms Phase 5 closed before dashboard integration begins.",
        },
        {
            "artifact": "promoted_price_paths_engine_file",
            "path": str(PROJECT_ROOT / "app" / "price_paths.py"),
            "required_for_phase6": True,
            "purpose": "Live price-path generation file promoted during Phase 5.",
        },
        {
            "artifact": "promoted_simulator_engine_file",
            "path": str(PROJECT_ROOT / "app" / "simulator.py"),
            "required_for_phase6": True,
            "purpose": "Live simulator file promoted during Phase 5.",
        },
        {
            "artifact": "historical_runner_candidate",
            "path": str(PROJECT_ROOT / "app" / "paid_simulator" / "phase5_historical_import_engine_runner_candidate.py"),
            "required_for_phase6": True,
            "purpose": "Historical import runner logic to be exposed later through a controlled dashboard option.",
        },
    ]
    rows: list[dict[str, Any]] = []
    for item in artifacts:
        path = Path(str(item["path"]))
        rows.append(
            {
                **item,
                "exists": path.exists(),
            }
        )
    return rows


def _dashboard_touchpoint_rows() -> list[dict[str, Any]]:
    return [
        {
            "touchpoint_order": 1,
            "dashboard_area": "Mode selection",
            "future_change": "Add explicit Synthetic / Historical import mode selector.",
            "default_behavior": "Synthetic remains default.",
            "phase6_action": "Plan first; do not patch dashboard in Phase 6-1.",
            "customer_risk": "Low if default remains synthetic.",
        },
        {
            "touchpoint_order": 2,
            "dashboard_area": "Historical data inputs",
            "future_change": "Show CSV input status and validation messages for historical mode.",
            "default_behavior": "Hidden or inactive unless historical mode is selected.",
            "phase6_action": "Expose only after runner is validated in dashboard context.",
            "customer_risk": "Medium if validation wording is unclear.",
        },
        {
            "touchpoint_order": 3,
            "dashboard_area": "Option-chain premium source",
            "future_change": "Allow modeled premium vs imported option-chain premium choice.",
            "default_behavior": "Existing model remains available.",
            "phase6_action": "Delay until historical mode dashboard flow is stable.",
            "customer_risk": "Medium because option-chain data can be sparse or stale.",
        },
        {
            "touchpoint_order": 4,
            "dashboard_area": "User-facing explanation",
            "future_change": "Explain that imported historical data is a scenario input, not a forecast.",
            "default_behavior": "Current educational framing remains.",
            "phase6_action": "Add cautious wording before public exposure.",
            "customer_risk": "High if users interpret historical mode as predictive.",
        },
        {
            "touchpoint_order": 5,
            "dashboard_area": "Reports and downloads",
            "future_change": "Tag reports with data source and mode used.",
            "default_behavior": "Existing outputs remain unchanged in synthetic mode.",
            "phase6_action": "Add after mode selector integration.",
            "customer_risk": "Low; improves auditability.",
        },
    ]


def _recommended_phase6_sequence_rows() -> list[dict[str, Any]]:
    return [
        {
            "phase": "Phase 6-1",
            "checkpoint": "Dashboard integration readiness",
            "dashboard_patch": False,
            "description": "Map dashboard touchpoints and confirm Phase 5 artifacts are available.",
        },
        {
            "phase": "Phase 6-2",
            "checkpoint": "Dashboard mode selector candidate",
            "dashboard_patch": False,
            "description": "Create a candidate UI contract for synthetic vs historical mode without touching live dashboard.",
        },
        {
            "phase": "Phase 6-3",
            "checkpoint": "Protected dashboard mode selector patch",
            "dashboard_patch": True,
            "description": "Patch config_form_app.py to add an explicit mode selector with synthetic as default.",
        },
        {
            "phase": "Phase 6-4",
            "checkpoint": "Historical input status panel",
            "dashboard_patch": True,
            "description": "Add read-only historical input status and validation messaging.",
        },
        {
            "phase": "Phase 6-5",
            "checkpoint": "Dashboard historical-mode smoke test",
            "dashboard_patch": False,
            "description": "Verify the dashboard can route historical mode safely while preserving synthetic default behavior.",
        },
    ]


def build_phase6_1_summary() -> dict[str, Any]:
    """Build Phase 6-1 readiness outputs and return checkpoint summary."""
    _ensure_output_dirs()

    artifact_status_df = pd.DataFrame(_artifact_status_rows())
    touchpoints_df = pd.DataFrame(_dashboard_touchpoint_rows())
    sequence_df = pd.DataFrame(_recommended_phase6_sequence_rows())

    required_artifacts = artifact_status_df[artifact_status_df["required_for_phase6"] == True]
    required_missing = int((~required_artifacts["exists"]).sum()) if not required_artifacts.empty else 0

    summary = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "overall_status": "PASS" if required_missing == 0 else "REVIEW",
        "dashboard_change_required": False,
        "dashboard_changed": False,
        "source_mode": "dashboard_integration_readiness",
        "phase5_complete": PHASE5_HANDOFF_REPORT.exists(),
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "dashboard_file_exists": DASHBOARD_FILE.exists(),
        "artifact_status_rows": int(len(artifact_status_df)),
        "dashboard_touchpoint_rows": int(len(touchpoints_df)),
        "recommended_sequence_rows": int(len(sequence_df)),
        "required_artifacts_missing": required_missing,
        "next_checkpoint": "Phase 6-2 — Dashboard mode selector candidate",
    }

    artifact_status_path = OUTPUT_TABLE_DIR / "phase6_1_dashboard_integration_artifact_status.csv"
    touchpoints_path = OUTPUT_TABLE_DIR / "phase6_1_dashboard_integration_touchpoints.csv"
    sequence_path = OUTPUT_TABLE_DIR / "phase6_1_recommended_dashboard_integration_sequence.csv"
    summary_path = OUTPUT_TABLE_DIR / "phase6_1_dashboard_integration_readiness_summary.csv"
    json_path = OUTPUT_REPORT_DIR / "phase6_1_dashboard_integration_readiness.json"
    report_path = OUTPUT_REPORT_DIR / "phase6_1_dashboard_integration_readiness_report.txt"

    artifact_status_df.to_csv(artifact_status_path, index=False)
    touchpoints_df.to_csv(touchpoints_path, index=False)
    sequence_df.to_csv(sequence_path, index=False)
    pd.DataFrame([summary]).to_csv(summary_path, index=False)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    report_lines = [
        "Phase 6-1 dashboard integration readiness",
        "=" * 70,
        f"Ready marker: {summary['ready_marker']}",
        f"Release decision: {summary['release_decision']}",
        f"Overall status: {summary['overall_status']}",
        f"Dashboard changed: {summary['dashboard_changed']}",
        f"Synthetic default preserved: {summary['synthetic_default_preserved']}",
        f"Historical mode explicit only: {summary['historical_mode_explicit_only']}",
        f"Dashboard touchpoints mapped: {summary['dashboard_touchpoint_rows']}",
        f"Recommended next checkpoint: {summary['next_checkpoint']}",
    ]
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase6_1_summary(), indent=2))
