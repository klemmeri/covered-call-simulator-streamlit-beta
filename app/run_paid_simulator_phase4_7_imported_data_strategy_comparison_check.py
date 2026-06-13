"""
run_paid_simulator_phase4_7_imported_data_strategy_comparison_check.py

Checkpoint script for Phase 4-7 of the Covered Call Simulator paid workflow.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import traceback
from pathlib import Path
from typing import Any

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]

DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
PHASE4_4_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase4_historical_price_path_adapter.py"
PHASE4_5_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase4_option_chain_premium_lookup.py"
PHASE4_6_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase4_premium_model_calibration_report.py"
PHASE4_7_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase4_strategy_comparison_imported_data.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase4_7_strategy_comparison_imported_data.md"

OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase4_7_imported_data_strategy_comparison_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase4_7_imported_data_strategy_comparison_checkpoint.json"

EXPECTED_OUTPUTS = {
    "comparison_rows_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase4_7_imported_data_strategy_comparison_rows.csv",
    "summary_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase4_7_imported_data_strategy_comparison_summary.csv",
    "json_report": PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase4_7_imported_data_strategy_comparison.json",
    "text_report": PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase4_7_imported_data_strategy_comparison_report.txt",
}


def _print_header(title: str) -> None:
    print("=" * 100)
    print(title)
    print("=" * 100)


def _record(checks: list[dict[str, Any]], passed: bool, label: str, detail: Any = "") -> None:
    status = "PASS" if passed else "FAIL"
    detail_text = "" if detail is None else str(detail)
    print(f"{status:<10} {label:<72} {detail_text}")
    checks.append({"status": status, "label": label, "detail": detail_text})


def _syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:
        return False, str(exc)


def _import_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    checks: list[dict[str, Any]] = []
    summary: dict[str, Any] | None = None

    _print_header("Phase 4-7 imported-data strategy comparison check")
    print(f"Project root: {PROJECT_ROOT}")
    print()

    _record(checks, DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    _record(checks, PHASE4_4_FILE.exists(), "Prior Phase 4-4 historical-path adapter module exists", PHASE4_4_FILE)
    _record(checks, PHASE4_5_FILE.exists(), "Prior Phase 4-5 option-chain lookup module exists", PHASE4_5_FILE)
    _record(checks, PHASE4_6_FILE.exists(), "Prior Phase 4-6 calibration module exists", PHASE4_6_FILE)
    _record(checks, PHASE4_7_FILE.exists(), "Phase 4-7 imported-data comparison module exists", PHASE4_7_FILE)
    _record(checks, DOC_FILE.exists(), "Phase 4-7 documentation exists", DOC_FILE)

    if DASHBOARD_FILE.exists():
        ok, detail = _syntax_valid(DASHBOARD_FILE)
        _record(checks, ok, "Dashboard syntax remains valid", detail)

    if PHASE4_7_FILE.exists():
        ok, detail = _syntax_valid(PHASE4_7_FILE)
        _record(checks, ok, "Phase 4-7 module syntax valid", detail)
        if ok:
            try:
                module = _import_module(PHASE4_7_FILE, "phase4_strategy_comparison_imported_data")
                summary = module.build_phase4_7_summary()
                _record(checks, isinstance(summary, dict), "Phase 4-7 module imports and builds comparison", type(summary).__name__)
            except Exception as exc:
                _record(checks, False, "Phase 4-7 module imports and builds comparison", exc)
                traceback.print_exc()

    if isinstance(summary, dict):
        _record(checks, summary.get("ready_marker") == "PHASE4_7_IMPORTED_DATA_STRATEGY_COMPARISON_READY", "Imported-data comparison has ready marker", summary.get("ready_marker"))
        _record(checks, summary.get("release_decision") == "PHASE4_7_IMPORTED_DATA_STRATEGY_COMPARISON_SCAFFOLD_CREATED_NO_DASHBOARD_CHANGE", "Imported-data comparison has release decision", summary.get("release_decision"))
        _record(checks, summary.get("dashboard_change_required") is False, "Imported-data comparison confirms no dashboard change", summary.get("dashboard_change_required"))
        _record(checks, summary.get("source_mode") == "imported_historical_data", "Imported-data comparison uses imported-historical mode", summary.get("source_mode"))
        _record(checks, summary.get("overall_status") == "PASS", "Imported-data comparison overall status is PASS", summary.get("overall_status"))
        _record(checks, (summary.get("historical_path_rows") or 0) > 0, "Historical path has rows", summary.get("historical_path_rows"))
        _record(checks, (summary.get("best_candidate_rows") or 0) > 0, "Best option-chain candidate has rows", summary.get("best_candidate_rows"))
        _record(checks, (summary.get("comparison_row_count") or 0) >= 2, "Strategy comparison has at least two rows", summary.get("comparison_row_count"))
        _record(checks, summary.get("start_price", 0) > 0, "Start price is positive", summary.get("start_price"))
        _record(checks, summary.get("end_price", 0) > 0, "End price is positive", summary.get("end_price"))
        _record(checks, "buy_hold_pl" in summary, "Buy-and-hold P/L is reported", summary.get("buy_hold_pl"))
        _record(checks, "covered_call_pl" in summary, "Covered-call P/L is reported", summary.get("covered_call_pl"))
        _record(checks, "covered_call_vs_buy_hold" in summary, "Covered-call relative P/L is reported", summary.get("covered_call_vs_buy_hold"))
    else:
        _record(checks, False, "Imported-data comparison summary produced", "summary was not a dict")

    for label, path in EXPECTED_OUTPUTS.items():
        _record(checks, path.exists(), f"Output written: {label}", path)

    comparison_csv = EXPECTED_OUTPUTS["comparison_rows_csv"]
    if comparison_csv.exists():
        try:
            comparison_df = pd.read_csv(comparison_csv)
            _record(checks, len(comparison_df) >= 2, "Comparison CSV has expected content", f"rows={len(comparison_df)}")
            strategies = set(comparison_df.get("strategy", []))
            _record(checks, "buy_and_hold" in strategies, "Comparison CSV includes buy-and-hold", strategies)
            _record(checks, "covered_call_imported_candidate" in strategies, "Comparison CSV includes covered-call scaffold", strategies)
        except Exception as exc:
            _record(checks, False, "Comparison CSV has expected content", exc)

    passed_all = all(item["status"] == "PASS" for item in checks)
    final_status = "PASS" if passed_all else "FAIL"

    print()
    _print_header(f"Overall Phase 4-7 checkpoint status: {final_status}")

    CHECKPOINT_REPORT.write_text(
        "\n".join([f"{item['status']:<10} {item['label']:<72} {item['detail']}" for item in checks])
        + f"\n\nOverall Phase 4-7 checkpoint status: {final_status}\n",
        encoding="utf-8",
    )
    CHECKPOINT_JSON.write_text(
        json.dumps({"overall_status": final_status, "checks": checks}, indent=2),
        encoding="utf-8",
    )

    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if passed_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
