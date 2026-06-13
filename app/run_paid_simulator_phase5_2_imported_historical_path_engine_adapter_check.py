"""
run_paid_simulator_phase5_2_imported_historical_path_engine_adapter_check.py

Checkpoint script for Phase 5-2: Imported historical path engine adapter.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
import traceback
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
PHASE4_COMPLETION_REPORT = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase4_completion_handoff_checkpoint_report.txt"
PHASE5_1_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase5_engine_integration_readiness.py"
PHASE5_2_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase5_imported_historical_path_engine_adapter.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase5_2_imported_historical_path_engine_adapter.md"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase5_2_imported_historical_path_engine_adapter_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase5_2_imported_historical_path_engine_adapter_checkpoint.json"

EXPECTED_OUTPUTS = {
    "engine_ready_path_csv": OUTPUT_TABLE_DIR / "phase5_2_engine_ready_historical_path.csv",
    "summary_csv": OUTPUT_TABLE_DIR / "phase5_2_engine_ready_historical_path_summary.csv",
    "json": OUTPUT_REPORT_DIR / "phase5_2_imported_historical_path_engine_adapter.json",
    "report": OUTPUT_REPORT_DIR / "phase5_2_imported_historical_path_engine_adapter_report.txt",
}


def _print_header(title: str) -> None:
    print("=" * 100)
    print(title)
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()


def _record(results: list[dict[str, Any]], status: bool, label: str, detail: Any = "") -> None:
    row = {"status": "PASS" if status else "FAIL", "label": label, "detail": str(detail)}
    results.append(row)
    print(f"{row['status']:<10} {label:<70} {row['detail']}")


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
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    _print_header("Phase 5-2 imported historical path engine adapter check")

    _record(results, DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    _record(results, PHASE4_COMPLETION_REPORT.exists(), "Phase 4 completion checkpoint report exists", PHASE4_COMPLETION_REPORT)
    _record(results, PHASE5_1_FILE.exists(), "Prior Phase 5-1 readiness module exists", PHASE5_1_FILE)
    _record(results, PHASE5_2_FILE.exists(), "Phase 5-2 engine adapter module exists", PHASE5_2_FILE)
    _record(results, DOC_FILE.exists(), "Phase 5-2 documentation exists", DOC_FILE)

    if DASHBOARD_FILE.exists():
        ok, detail = _syntax_valid(DASHBOARD_FILE)
        _record(results, ok, "Dashboard syntax remains valid", detail)

    if PHASE5_2_FILE.exists():
        ok, detail = _syntax_valid(PHASE5_2_FILE)
        _record(results, ok, "Phase 5-2 module syntax valid", detail)

    summary: dict[str, Any] | None = None
    if PHASE5_2_FILE.exists():
        try:
            module = _import_module(PHASE5_2_FILE, "phase5_imported_historical_path_engine_adapter")
            summary = module.build_phase5_2_summary()
            _record(results, isinstance(summary, dict), "Phase 5-2 module imports and builds engine-ready path", type(summary).__name__)
        except Exception as exc:
            _record(results, False, "Phase 5-2 module imports and builds engine-ready path", exc)
            traceback.print_exc()

    if isinstance(summary, dict):
        _record(results, summary.get("ready_marker") == "PHASE5_2_IMPORTED_HISTORICAL_PATH_ENGINE_ADAPTER_READY", "Engine adapter has ready marker", summary.get("ready_marker"))
        _record(results, summary.get("release_decision") == "PHASE5_2_IMPORTED_HISTORICAL_PATH_ENGINE_ADAPTER_CREATED_NO_DASHBOARD_CHANGE", "Engine adapter has release decision", summary.get("release_decision"))
        _record(results, summary.get("dashboard_change_required") is False, "Engine adapter confirms no dashboard change", summary.get("dashboard_change_required"))
        _record(results, summary.get("source_mode") == "historical_import", "Engine adapter uses historical-import mode", summary.get("source_mode"))
        _record(results, summary.get("engine_adapter_mode") == "engine_ready_historical_path", "Engine adapter mode is engine-ready historical path", summary.get("engine_adapter_mode"))
        _record(results, summary.get("synthetic_mode_preserved") is True, "Synthetic mode is preserved", summary.get("synthetic_mode_preserved"))
        _record(results, summary.get("overall_status") == "PASS", "Engine adapter overall status is PASS", summary.get("overall_status"))
        _record(results, (summary.get("engine_ready_path_rows") or 0) > 0, "Engine-ready path output has rows", summary.get("engine_ready_path_rows"))
        _record(results, bool(summary.get("path_id")), "Engine-ready path ID is present", summary.get("path_id"))
        _record(results, (summary.get("first_price") or 0) > 0, "Engine-ready first price is positive", summary.get("first_price"))
        _record(results, (summary.get("last_price") or 0) > 0, "Engine-ready last price is positive", summary.get("last_price"))
    else:
        _record(results, False, "Phase 5-2 summary produced", "summary was not a dict")

    for name, path in EXPECTED_OUTPUTS.items():
        _record(results, path.exists(), f"Output written: {name}", path)

    engine_path = EXPECTED_OUTPUTS["engine_ready_path_csv"]
    if engine_path.exists():
        try:
            df = pd.read_csv(engine_path)
            required_cols = {"path_id", "engine_step", "source_date", "underlying_price", "simple_return", "usable_by_engine"}
            _record(results, required_cols.issubset(set(df.columns)), "Engine-ready CSV has required columns", sorted(set(df.columns)))
            _record(results, len(df) > 0, "Engine-ready CSV has expected content", f"rows={len(df)}")
        except Exception as exc:
            _record(results, False, "Engine-ready CSV can be read", exc)

    overall_pass = all(row["status"] == "PASS" for row in results)

    print()
    print("=" * 100)
    print(f"Overall Phase 5-2 checkpoint status: {'PASS' if overall_pass else 'FAIL'}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join([f"{row['status']:<10} {row['label']:<70} {row['detail']}" for row in results])
        + f"\n\nOverall Phase 5-2 checkpoint status: {'PASS' if overall_pass else 'FAIL'}\n",
        encoding="utf-8",
    )
    CHECKPOINT_JSON.write_text(json.dumps({"overall_status": "PASS" if overall_pass else "FAIL", "results": results}, indent=2), encoding="utf-8")

    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
