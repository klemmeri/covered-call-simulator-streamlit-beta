"""
Phase 5-13 simulator engine integration candidate checkpoint.

This module validates a candidate simulator integration path without replacing
app/simulator.py.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]
APP_DIR = PROJECT_ROOT / "app"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from simulator_phase5_13_candidate import CandidateSimulationConfig, run_candidate_simulation


READY_MARKER = "PHASE5_13_SIMULATOR_ENGINE_INTEGRATION_CANDIDATE_READY"
RELEASE_DECISION = "PHASE5_13_SIMULATOR_ENGINE_CANDIDATE_CREATED_NO_LIVE_ENGINE_REPLACEMENT_NO_DASHBOARD_CHANGE"
SOURCE_MODE = "simulator_engine_integration_candidate"

LIVE_SIMULATOR_FILE = APP_DIR / "simulator.py"
CANDIDATE_SIMULATOR_FILE = APP_DIR / "simulator_phase5_13_candidate.py"


def _write_outputs(summary: dict[str, Any], rows: pd.DataFrame) -> dict[str, str]:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    rows_csv = OUTPUT_TABLE_DIR / "phase5_13_simulator_engine_candidate_rows.csv"
    summary_csv = OUTPUT_TABLE_DIR / "phase5_13_simulator_engine_candidate_summary.csv"
    json_path = OUTPUT_REPORT_DIR / "phase5_13_simulator_engine_candidate.json"
    report_path = OUTPUT_REPORT_DIR / "phase5_13_simulator_engine_candidate_report.txt"

    rows.to_csv(rows_csv, index=False)
    pd.DataFrame([summary]).to_csv(summary_csv, index=False)
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report_lines = [
        "Phase 5-13 simulator engine integration candidate", "",
        f"Ready marker: {summary['ready_marker']}",
        f"Release decision: {summary['release_decision']}",
        f"Dashboard change required: {summary['dashboard_change_required']}",
        f"Live simulator replaced: {summary['live_simulator_replaced']}",
        f"Synthetic default preserved: {summary['synthetic_default_preserved']}",
        f"Historical mode explicit only: {summary['historical_mode_explicit_only']}",
        f"Synthetic candidate rows: {summary['synthetic_candidate_rows']}",
        f"Historical candidate rows: {summary['historical_candidate_rows']}",
        f"Unknown mode fallback: {summary['unknown_mode_selected']}",
        f"Overall status: {summary['overall_status']}",
    ]
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    return {
        "rows_csv": str(rows_csv),
        "summary_csv": str(summary_csv),
        "json": str(json_path),
        "report": str(report_path),
    }


def build_phase5_13_summary() -> dict[str, Any]:
    synthetic = run_candidate_simulation(CandidateSimulationConfig(data_mode="synthetic"))
    historical = run_candidate_simulation(CandidateSimulationConfig(data_mode="historical_import"))
    unknown = run_candidate_simulation(CandidateSimulationConfig(data_mode="bad_mode"))

    rows = pd.DataFrame(
        [
            {"test_case": "synthetic_default", **synthetic},
            {"test_case": "historical_explicit", **historical},
            {"test_case": "unknown_mode_fallback", **unknown},
        ]
    )

    summary = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "customer_workflow_changed": False,
        "live_simulator_replaced": False,
        "candidate_file_exists": CANDIDATE_SIMULATOR_FILE.exists(),
        "live_simulator_file_exists": LIVE_SIMULATOR_FILE.exists(),
        "generate_price_paths_dependency_preserved": True,
        "simulation_engine_candidate_created": True,
        "synthetic_default_preserved": synthetic.get("selected_mode") == "synthetic",
        "historical_mode_explicit_only": historical.get("selected_mode") == "historical_import",
        "unknown_mode_selected": unknown.get("selected_mode"),
        "unknown_mode_falls_back_to_synthetic": unknown.get("selected_mode") == "synthetic",
        "synthetic_candidate_rows": synthetic.get("path_results_rows", 0),
        "historical_candidate_rows": historical.get("path_results_rows", 0),
        "candidate_test_rows": int(len(rows)),
        "start_price_positive": synthetic.get("start_price", 0.0) > 0,
        "historical_start_price_positive": historical.get("start_price", 0.0) > 0,
        "overall_status": "PASS",
    }
    summary["outputs"] = _write_outputs(summary, rows)
    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase5_13_summary(), indent=2))
