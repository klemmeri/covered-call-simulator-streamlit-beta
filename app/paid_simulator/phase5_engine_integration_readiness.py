"""
phase5_engine_integration_readiness.py

Phase 5-1 checkpoint for the Covered Call Simulator paid workflow.

Purpose
-------
Phase 4 created imported-data scaffolds:

1. Historical underlying price path adapter.
2. Option-chain premium lookup scaffold.
3. Premium-model calibration report.
4. Imported-data strategy comparison report.

Phase 5 begins the transition from scaffolded reports to actual simulator-engine
integration. This module does not modify the production simulator, dashboard, or
configuration files. It creates a readiness map describing which engine files are
expected to receive imported-data hooks in later Phase 5 steps.

Design rule
-----------
This checkpoint is intentionally add-only. It is a planning and validation layer,
not a runtime engine patch.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


READY_MARKER = "PHASE5_1_ENGINE_INTEGRATION_READINESS_READY"
RELEASE_DECISION = "PHASE5_1_READY_TO_BEGIN_ENGINE_HARDENING_NO_DASHBOARD_CHANGE"
SOURCE_MODE = "phase5_engine_integration_planning"
DASHBOARD_CHANGE_REQUIRED = False


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]
APP_DIR = PROJECT_ROOT / "app"
PAID_SIMULATOR_DIR = APP_DIR / "paid_simulator"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"


ENGINE_TOUCHPOINTS = [
    {
        "touchpoint_id": "engine_config_mode",
        "likely_file": "config/paid_simulator_config.json",
        "purpose": "Add a future simulation data-mode field such as synthetic or imported_historical.",
        "phase5_action": "plan_only",
        "dashboard_change_required_now": False,
        "risk_level": "low",
    },
    {
        "touchpoint_id": "historical_path_adapter",
        "likely_file": "app/paid_simulator/phase4_historical_price_path_adapter.py",
        "purpose": "Provide normalized imported price paths created from market-data CSV input.",
        "phase5_action": "reuse_existing_artifact",
        "dashboard_change_required_now": False,
        "risk_level": "low",
    },
    {
        "touchpoint_id": "option_chain_premium_source",
        "likely_file": "app/paid_simulator/phase4_option_chain_premium_lookup.py",
        "purpose": "Provide observed option premium candidates for covered-call selection and calibration.",
        "phase5_action": "reuse_existing_artifact",
        "dashboard_change_required_now": False,
        "risk_level": "low",
    },
    {
        "touchpoint_id": "simulator_price_path_input",
        "likely_file": "app/simulator.py",
        "purpose": "Allow the simulator to consume imported historical paths while preserving synthetic fallback.",
        "phase5_action": "future_patch",
        "dashboard_change_required_now": False,
        "risk_level": "medium",
    },
    {
        "touchpoint_id": "strategy_premium_input",
        "likely_file": "app/strategy.py",
        "purpose": "Allow covered-call sale logic to optionally use observed option-chain premium data instead of only modeled premium.",
        "phase5_action": "future_patch",
        "dashboard_change_required_now": False,
        "risk_level": "medium",
    },
    {
        "touchpoint_id": "portfolio_cycle_accounting",
        "likely_file": "app/portfolio.py",
        "purpose": "Ensure cycle-level P/L remains stable when price and premium sources are imported rather than synthetic.",
        "phase5_action": "future_validation",
        "dashboard_change_required_now": False,
        "risk_level": "medium",
    },
    {
        "touchpoint_id": "paid_dashboard_mode_selector",
        "likely_file": "app/paid_simulator/config_form_app.py",
        "purpose": "Expose imported-data mode only after engine integration is validated.",
        "phase5_action": "defer_to_phase6",
        "dashboard_change_required_now": False,
        "risk_level": "high_if_done_too_early",
    },
]


PHASE5_SEQUENCE = [
    {
        "checkpoint": "Phase 5-1",
        "name": "Engine integration readiness map",
        "status": "current",
        "dashboard_change": False,
    },
    {
        "checkpoint": "Phase 5-2",
        "name": "Imported historical path engine adapter",
        "status": "recommended_next",
        "dashboard_change": False,
    },
    {
        "checkpoint": "Phase 5-3",
        "name": "Synthetic fallback preservation check",
        "status": "planned",
        "dashboard_change": False,
    },
    {
        "checkpoint": "Phase 5-4",
        "name": "Option-chain premium source adapter for strategy logic",
        "status": "planned",
        "dashboard_change": False,
    },
    {
        "checkpoint": "Phase 5-5",
        "name": "Integrated engine comparison: synthetic vs imported data",
        "status": "planned",
        "dashboard_change": False,
    },
    {
        "checkpoint": "Phase 5-6",
        "name": "Phase 5 completion handoff for Phase 6 dashboard integration",
        "status": "planned",
        "dashboard_change": False,
    },
]


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _path_exists(relative_path: str) -> bool:
    return (PROJECT_ROOT / relative_path).exists()


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_key_value_csv(path: Path, summary: dict[str, Any]) -> None:
    rows = [{"metric": key, "value": value} for key, value in summary.items()]
    _write_csv(path, rows)


def _build_artifact_status() -> list[dict[str, Any]]:
    artifacts = [
        "app/simulator.py",
        "app/strategy.py",
        "app/portfolio.py",
        "app/paid_simulator/config_form_app.py",
        "app/paid_simulator/phase4_historical_price_path_adapter.py",
        "app/paid_simulator/phase4_option_chain_premium_lookup.py",
        "outputs/tables/paid_simulator/phase4_4_historical_price_path.csv",
        "outputs/tables/paid_simulator/phase4_5_best_covered_call_candidate.csv",
        "outputs/reports/paid_simulator/phase4_completion_handoff_report.txt",
    ]
    return [
        {
            "artifact": artifact,
            "exists": _path_exists(artifact),
            "role": _artifact_role(artifact),
        }
        for artifact in artifacts
    ]


def _artifact_role(artifact: str) -> str:
    if artifact.endswith("simulator.py"):
        return "future historical price-path input hook"
    if artifact.endswith("strategy.py"):
        return "future option-chain premium input hook"
    if artifact.endswith("portfolio.py"):
        return "future cycle-level accounting validation"
    if artifact.endswith("config_form_app.py"):
        return "dashboard integration deferred to Phase 6"
    if "phase4_historical" in artifact:
        return "existing imported historical path source"
    if "phase4_option_chain" in artifact or "best_covered_call_candidate" in artifact:
        return "existing option-chain premium source"
    if "phase4_completion" in artifact:
        return "Phase 4 closeout evidence"
    return "supporting artifact"


def build_phase5_1_summary() -> dict[str, Any]:
    """Build the Phase 5-1 readiness summary and write report artifacts."""
    _ensure_dirs()

    artifact_status = _build_artifact_status()
    existing_artifact_count = sum(1 for row in artifact_status if row["exists"])
    missing_artifact_count = len(artifact_status) - existing_artifact_count

    touchpoint_rows = []
    for row in ENGINE_TOUCHPOINTS:
        enriched = dict(row)
        enriched["file_exists_now"] = _path_exists(row["likely_file"])
        touchpoint_rows.append(enriched)

    phase_sequence_rows = list(PHASE5_SEQUENCE)

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "overall_status": "PASS",
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": DASHBOARD_CHANGE_REQUIRED,
        "touchpoint_count": len(touchpoint_rows),
        "phase5_checkpoint_count": len(phase_sequence_rows),
        "artifact_count": len(artifact_status),
        "existing_artifact_count": existing_artifact_count,
        "missing_artifact_count": missing_artifact_count,
        "recommended_next_checkpoint": "Phase 5-2 - Imported historical path engine adapter",
        "phase5_scope": "engine_hardening_before_dashboard_integration",
    }

    touchpoint_csv = OUTPUT_TABLE_DIR / "phase5_1_engine_integration_touchpoints.csv"
    artifact_csv = OUTPUT_TABLE_DIR / "phase5_1_engine_integration_artifact_status.csv"
    sequence_csv = OUTPUT_TABLE_DIR / "phase5_1_engine_integration_sequence.csv"
    summary_csv = OUTPUT_TABLE_DIR / "phase5_1_engine_integration_readiness_summary.csv"
    json_path = OUTPUT_REPORT_DIR / "phase5_1_engine_integration_readiness.json"
    report_path = OUTPUT_REPORT_DIR / "phase5_1_engine_integration_readiness_report.txt"

    _write_csv(touchpoint_csv, touchpoint_rows)
    _write_csv(artifact_csv, artifact_status)
    _write_csv(sequence_csv, phase_sequence_rows)
    _write_key_value_csv(summary_csv, summary)

    payload = {
        "summary": summary,
        "touchpoints": touchpoint_rows,
        "artifact_status": artifact_status,
        "phase5_sequence": phase_sequence_rows,
        "outputs": {
            "touchpoint_csv": str(touchpoint_csv),
            "artifact_csv": str(artifact_csv),
            "sequence_csv": str(sequence_csv),
            "summary_csv": str(summary_csv),
            "json": str(json_path),
            "report": str(report_path),
        },
    }

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    report_path.write_text(_build_report_text(payload), encoding="utf-8")

    return summary


def _build_report_text(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "Phase 5-1 Engine Integration Readiness Report",
        "=" * 70,
        "",
        f"Status: {summary['overall_status']}",
        f"Ready marker: {summary['ready_marker']}",
        f"Release decision: {summary['release_decision']}",
        f"Dashboard change required: {summary['dashboard_change_required']}",
        f"Recommended next checkpoint: {summary['recommended_next_checkpoint']}",
        "",
        "Purpose:",
        "  Begin Phase 5 by mapping where imported historical paths and option-chain premiums",
        "  should enter the simulator engine. This checkpoint deliberately avoids dashboard",
        "  changes and avoids patching production engine logic.",
        "",
        "Engine touchpoints:",
    ]
    for row in payload["touchpoints"]:
        lines.append(
            f"  - {row['touchpoint_id']}: {row['likely_file']} | action={row['phase5_action']} | risk={row['risk_level']}"
        )
    lines.extend([
        "",
        "Phase 5 sequence:",
    ])
    for row in payload["phase5_sequence"]:
        lines.append(f"  - {row['checkpoint']}: {row['name']} [{row['status']}]")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    result = build_phase5_1_summary()
    print(json.dumps(result, indent=2))
