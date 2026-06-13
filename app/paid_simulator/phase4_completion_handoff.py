"""
phase4_completion_handoff.py

Phase 4 completion and Phase 5 planning checkpoint for the Covered Call Simulator.

This module does not modify the dashboard. It verifies that the Phase 4 data/modeling
foundation artifacts exist and writes a concise handoff report for the next development
phase.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


READY_MARKER = "PHASE4_COMPLETION_HANDOFF_READY"
RELEASE_DECISION = "PHASE4_COMPLETE_READY_FOR_PHASE5_INTEGRATION_OR_ENGINE_UPGRADE"
SOURCE_MODE = "phase4_completion_handoff"
DASHBOARD_CHANGE_REQUIRED = False


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _exists_status(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "exists": path.exists(),
    }


def _safe_row_count(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        return int(len(pd.read_csv(path)))
    except Exception:
        return None


def build_phase4_completion_summary() -> dict[str, Any]:
    """Build the Phase 4 completion handoff summary and write output artifacts."""
    root = _project_root()

    reports_dir = root / "outputs" / "reports" / "paid_simulator"
    tables_dir = root / "outputs" / "tables" / "paid_simulator"
    reports_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    expected_artifacts = {
        "phase4_2_market_data_scaffold_report": reports_dir / "phase4_2_market_data_input_scaffold_report.txt",
        "phase4_3_loader_validator_report": reports_dir / "phase4_3_market_data_loader_validator_report.txt",
        "phase4_4_historical_path_report": reports_dir / "phase4_4_historical_price_path_adapter_report.txt",
        "phase4_5_option_chain_lookup_report": reports_dir / "phase4_5_option_chain_premium_lookup_report.txt",
        "phase4_6_calibration_report": reports_dir / "phase4_6_premium_model_calibration_report.txt",
        "phase4_7_strategy_comparison_report": reports_dir / "phase4_7_imported_data_strategy_comparison_report.txt",
        "sample_underlying_prices": root / "inputs" / "market_data" / "sample_underlying_prices.csv",
        "sample_option_chain": root / "inputs" / "market_data" / "sample_option_chain.csv",
        "historical_price_path": tables_dir / "phase4_4_historical_price_path.csv",
        "best_option_candidate": tables_dir / "phase4_5_best_covered_call_candidate.csv",
        "calibration_summary": tables_dir / "phase4_6_premium_model_calibration_summary.csv",
        "imported_data_strategy_comparison": tables_dir / "phase4_7_imported_data_strategy_comparison_summary.csv",
    }

    artifact_status = {
        key: _exists_status(path)
        for key, path in expected_artifacts.items()
    }

    required_keys = [
        "sample_underlying_prices",
        "sample_option_chain",
        "historical_price_path",
        "best_option_candidate",
        "calibration_summary",
        "imported_data_strategy_comparison",
    ]
    required_artifacts_present = all(artifact_status[key]["exists"] for key in required_keys)

    row_counts = {
        "sample_underlying_price_rows": _safe_row_count(expected_artifacts["sample_underlying_prices"]),
        "sample_option_chain_rows": _safe_row_count(expected_artifacts["sample_option_chain"]),
        "historical_price_path_rows": _safe_row_count(expected_artifacts["historical_price_path"]),
        "best_option_candidate_rows": _safe_row_count(expected_artifacts["best_option_candidate"]),
        "calibration_summary_rows": _safe_row_count(expected_artifacts["calibration_summary"]),
        "imported_data_strategy_comparison_rows": _safe_row_count(expected_artifacts["imported_data_strategy_comparison"]),
    }

    phase4_completed = required_artifacts_present
    status = "PASS" if phase4_completed else "FAIL"

    next_phase_recommendations = [
        {
            "phase": "Phase 5A",
            "title": "Dashboard integration for imported data mode",
            "description": "Add a controlled dashboard selector for synthetic sample mode versus imported market-data mode.",
            "dashboard_change_required": True,
        },
        {
            "phase": "Phase 5B",
            "title": "Simulation-engine adapter for historical paths",
            "description": "Route imported historical paths into the existing simulator while preserving synthetic fallback.",
            "dashboard_change_required": False,
        },
        {
            "phase": "Phase 5C",
            "title": "Option-chain-informed covered-call selection",
            "description": "Use imported option-chain candidates to choose strike, DTE, premium, and delta assumptions instead of pure model estimates.",
            "dashboard_change_required": False,
        },
    ]

    summary = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION if phase4_completed else "PHASE4_COMPLETION_BLOCKED_REVIEW_REQUIRED",
        "status": status,
        "overall_status": status,
        "phase4_completed": phase4_completed,
        "dashboard_change_required": DASHBOARD_CHANGE_REQUIRED,
        "source_mode": SOURCE_MODE,
        "required_artifacts_present": required_artifacts_present,
        "artifact_status": artifact_status,
        "row_counts": row_counts,
        "recommended_next_step": "Start Phase 5 with dashboard integration only if you want users to access imported-data mode; otherwise first harden the engine adapter.",
        "next_phase_recommendations": next_phase_recommendations,
        "modeling_caution": "Regime labels and scenario classifications should remain probabilistic guidance, not deterministic market forecasts.",
    }

    summary_rows = []
    for key, item in artifact_status.items():
        summary_rows.append({
            "artifact": key,
            "exists": item["exists"],
            "path": item["path"],
            "row_count": row_counts.get(f"{key}_rows"),
        })
    pd.DataFrame(summary_rows).to_csv(tables_dir / "phase4_completion_handoff_artifact_status.csv", index=False)

    decision_rows = [
        {"field": "ready_marker", "value": READY_MARKER},
        {"field": "release_decision", "value": summary["release_decision"]},
        {"field": "overall_status", "value": status},
        {"field": "phase4_completed", "value": phase4_completed},
        {"field": "dashboard_change_required", "value": DASHBOARD_CHANGE_REQUIRED},
        {"field": "source_mode", "value": SOURCE_MODE},
    ]
    pd.DataFrame(decision_rows).to_csv(tables_dir / "phase4_completion_handoff_summary.csv", index=False)

    json_path = reports_dir / "phase4_completion_handoff.json"
    report_path = reports_dir / "phase4_completion_handoff_report.txt"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "Phase 4 completion handoff",
        "=" * 80,
        f"Status: {status}",
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {summary['release_decision']}",
        f"Dashboard change required: {DASHBOARD_CHANGE_REQUIRED}",
        "",
        "Required artifacts:",
    ]
    for key in required_keys:
        item = artifact_status[key]
        lines.append(f"- {key}: {'FOUND' if item['exists'] else 'MISSING'} | {item['path']}")
    lines.extend([
        "",
        "Recommended next step:",
        summary["recommended_next_step"],
        "",
        "Modeling caution:",
        summary["modeling_caution"],
    ])
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    result = build_phase4_completion_summary()
    print(json.dumps(result, indent=2))
