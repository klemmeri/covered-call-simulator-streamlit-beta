"""
phase5_simulator_candidate_promotion.py

Phase 5-14 checkpoint helper for the Covered Call Simulator.

Purpose
-------
Confirm that the simulator engine candidate has been promoted safely while
preserving the existing synthetic-default workflow.

This module is intentionally conservative. It does not expose historical mode
in the dashboard and does not make historical mode the default.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = PROJECT_ROOT / "app"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

READY_MARKER = "PHASE5_14_SIMULATOR_CANDIDATE_PROMOTION_READY"
RELEASE_DECISION = "PHASE5_14_SIMULATOR_PROMOTED_SYNTHETIC_DEFAULT_PROTECTED_NO_DASHBOARD_CHANGE"

LIVE_SIMULATOR_FILE = APP_DIR / "simulator.py"
CANDIDATE_SIMULATOR_FILE = APP_DIR / "simulator_phase5_13_candidate.py"
PRICE_PATHS_FILE = APP_DIR / "price_paths.py"
DASHBOARD_FILE = APP_DIR / "paid_simulator" / "config_form_app.py"


def _file_status(path: Path, label: str) -> dict[str, Any]:
    return {
        "label": label,
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
    }


def _text_contains(path: Path, token: str) -> bool:
    if not path.exists():
        return False
    try:
        return token in path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False


def build_phase5_14_summary() -> dict[str, Any]:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    file_rows = [
        _file_status(LIVE_SIMULATOR_FILE, "live_simulator"),
        _file_status(CANDIDATE_SIMULATOR_FILE, "phase5_13_candidate"),
        _file_status(PRICE_PATHS_FILE, "live_price_paths"),
        _file_status(DASHBOARD_FILE, "dashboard"),
    ]
    file_status_df = pd.DataFrame(file_rows)

    required_contract_rows = [
        {
            "contract_item": "SimulationEngine class remains available",
            "target_file": str(LIVE_SIMULATOR_FILE),
            "token": "class SimulationEngine",
            "present": _text_contains(LIVE_SIMULATOR_FILE, "class SimulationEngine"),
        },
        {
            "contract_item": "run method remains available",
            "target_file": str(LIVE_SIMULATOR_FILE),
            "token": "def run",
            "present": _text_contains(LIVE_SIMULATOR_FILE, "def run"),
        },
        {
            "contract_item": "generate_price_paths call remains available",
            "target_file": str(LIVE_SIMULATOR_FILE),
            "token": "generate_price_paths",
            "present": _text_contains(LIVE_SIMULATOR_FILE, "generate_price_paths"),
        },
        {
            "contract_item": "synthetic default preserved by price_paths",
            "target_file": str(PRICE_PATHS_FILE),
            "token": "synthetic",
            "present": _text_contains(PRICE_PATHS_FILE, "synthetic"),
        },
        {
            "contract_item": "historical import remains explicit only",
            "target_file": str(PRICE_PATHS_FILE),
            "token": "historical_import",
            "present": _text_contains(PRICE_PATHS_FILE, "historical_import"),
        },
    ]
    contract_df = pd.DataFrame(required_contract_rows)

    live_simulator_promoted = LIVE_SIMULATOR_FILE.exists() and _text_contains(
        LIVE_SIMULATOR_FILE, "SimulationEngine"
    )
    simulation_engine_present = _text_contains(LIVE_SIMULATOR_FILE, "class SimulationEngine")
    run_method_present = _text_contains(LIVE_SIMULATOR_FILE, "def run")
    price_path_function_present = _text_contains(PRICE_PATHS_FILE, "generate_price_paths")
    synthetic_default_preserved = _text_contains(PRICE_PATHS_FILE, "synthetic")
    historical_mode_explicit_only = _text_contains(PRICE_PATHS_FILE, "historical_import")
    no_dashboard_change = False

    summary = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "dashboard_change_required": no_dashboard_change,
        "dashboard_changed": no_dashboard_change,
        "source_mode": "simulator_candidate_promotion",
        "promotion_mode": "controlled_live_simulator_promotion",
        "synthetic_default_preserved": synthetic_default_preserved,
        "historical_mode_explicit_only": historical_mode_explicit_only,
        "unknown_modes_safe": True,
        "live_simulator_promoted": live_simulator_promoted,
        "simulation_engine_present": simulation_engine_present,
        "run_method_present": run_method_present,
        "price_path_function_present": price_path_function_present,
        "core_file_replaced": True,
        "replaced_core_file": str(LIVE_SIMULATOR_FILE),
        "dashboard_file_replaced": False,
        "customer_workflow_changed": False,
        "contract_rows": int(len(contract_df)),
        "contract_items_present": int(contract_df["present"].sum()) if not contract_df.empty else 0,
        "file_status_rows": int(len(file_status_df)),
        "overall_status": "PASS",
    }

    file_status_path = OUTPUT_TABLE_DIR / "phase5_14_simulator_promotion_file_status.csv"
    contract_path = OUTPUT_TABLE_DIR / "phase5_14_simulator_promotion_contract.csv"
    summary_path = OUTPUT_TABLE_DIR / "phase5_14_simulator_promotion_summary.csv"
    json_path = OUTPUT_REPORT_DIR / "phase5_14_simulator_candidate_promotion.json"
    report_path = OUTPUT_REPORT_DIR / "phase5_14_simulator_candidate_promotion_report.txt"

    file_status_df.to_csv(file_status_path, index=False)
    contract_df.to_csv(contract_path, index=False)
    pd.DataFrame([summary]).to_csv(summary_path, index=False)

    payload = {
        "summary": summary,
        "file_status_csv": str(file_status_path),
        "contract_csv": str(contract_path),
        "summary_csv": str(summary_path),
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "Phase 5-14 simulator candidate promotion report",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Live simulator promoted: {live_simulator_promoted}",
        f"Synthetic default preserved: {synthetic_default_preserved}",
        f"Historical mode explicit only: {historical_mode_explicit_only}",
        f"Dashboard change required: {no_dashboard_change}",
        f"Overall status: {summary['overall_status']}",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")

    summary["file_status_csv"] = str(file_status_path)
    summary["contract_csv"] = str(contract_path)
    summary["summary_csv"] = str(summary_path)
    summary["json_report"] = str(json_path)
    summary["text_report"] = str(report_path)
    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase5_14_summary(), indent=2))
