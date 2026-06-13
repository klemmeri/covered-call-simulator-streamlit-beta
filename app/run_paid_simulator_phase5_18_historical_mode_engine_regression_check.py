"""
run_paid_simulator_phase5_18_historical_mode_engine_regression_check.py

Checkpoint script for Phase 5-18.
"""

from __future__ import annotations

import importlib.util
import json
import py_compile
import traceback
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
PRIOR_PHASE5_17_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase5_controlled_historical_runner_promotion.py"
PHASE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase5_historical_mode_engine_regression.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase5_18_historical_mode_engine_regression.md"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

EXPECTED_OUTPUTS = {
    "rows_csv": OUTPUT_TABLE_DIR / "phase5_18_historical_mode_engine_regression_rows.csv",
    "summary_csv": OUTPUT_TABLE_DIR / "phase5_18_historical_mode_engine_regression_summary.csv",
    "json": OUTPUT_REPORT_DIR / "phase5_18_historical_mode_engine_regression.json",
    "report": OUTPUT_REPORT_DIR / "phase5_18_historical_mode_engine_regression_report.txt",
}

CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase5_18_historical_mode_engine_regression_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase5_18_historical_mode_engine_regression_checkpoint.json"


def _print_header(title: str) -> None:
    print("=" * 100)
    print(title)
    print("=" * 100)


def _record(results: list[dict[str, Any]], passed: bool, label: str, detail: Any = "") -> None:
    status = "PASS" if passed else "FAIL"
    results.append({"status": status, "label": label, "detail": str(detail)})
    print(f"{status:<10} {label:<70} {detail}")


def _compile(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "syntax valid"
    except Exception as exc:
        return False, str(exc)


def _import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_csv_rows(path: Path) -> int | None:
    try:
        if not path.exists():
            return None
        return len(pd.read_csv(path))
    except Exception:
        return None


def main() -> int:
    results: list[dict[str, Any]] = []
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    _print_header("Phase 5-18 historical-mode engine regression check")
    print(f"Project root: {PROJECT_ROOT}")
    print()

    _record(results, DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    _record(results, PRIOR_PHASE5_17_FILE.exists(), "Prior Phase 5-17 runner promotion module exists", PRIOR_PHASE5_17_FILE)
    _record(results, PHASE_FILE.exists(), "Phase 5-18 regression module exists", PHASE_FILE)
    _record(results, DOC_FILE.exists(), "Phase 5-18 documentation exists", DOC_FILE)

    ok, detail = _compile(DASHBOARD_FILE)
    _record(results, ok, "Dashboard syntax remains valid", detail)

    ok, detail = _compile(PHASE_FILE)
    _record(results, ok, "Phase 5-18 module syntax valid", detail)

    summary: dict[str, Any] | None = None
    try:
        module = _import_module(PHASE_FILE, "phase5_historical_mode_engine_regression")
        summary = module.build_phase5_18_summary()
        _record(results, isinstance(summary, dict), "Phase 5-18 module imports and builds regression", type(summary).__name__)
    except Exception as exc:
        _record(results, False, "Phase 5-18 module imports and builds regression", exc)
        traceback.print_exc()

    if summary is None:
        summary = {}

    _record(results, summary.get("ready_marker") == "PHASE5_18_HISTORICAL_MODE_ENGINE_REGRESSION_READY", "Regression has ready marker", summary.get("ready_marker"))
    _record(results, summary.get("release_decision") == "PHASE5_18_HISTORICAL_MODE_ENGINE_REGRESSION_CREATED_NO_DASHBOARD_CHANGE", "Regression has release decision", summary.get("release_decision"))
    _record(results, summary.get("dashboard_change_required") is False, "Regression confirms no dashboard change", summary.get("dashboard_change_required"))
    _record(results, summary.get("source_mode") == "historical_mode_engine_regression", "Regression uses expected source mode", summary.get("source_mode"))
    _record(results, summary.get("requested_mode") == "historical_import", "Regression requested historical import", summary.get("requested_mode"))
    _record(results, summary.get("selected_mode") == "historical_import", "Regression selected historical import", summary.get("selected_mode"))
    _record(results, summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    _record(results, summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    _record(results, summary.get("engine_regression_created") is True, "Engine regression created", summary.get("engine_regression_created"))
    _record(results, summary.get("live_core_engine_replaced") is False, "No live core engine replacement in this checkpoint", summary.get("live_core_engine_replaced"))
    _record(results, (summary.get("historical_path_rows") or 0) >= 1, "Historical path has rows", summary.get("historical_path_rows"))
    _record(results, (summary.get("regression_rows") or 0) >= 6, "Regression rows created", summary.get("regression_rows"))
    _record(results, (summary.get("start_price") or 0) > 0, "Start price is positive", summary.get("start_price"))
    _record(results, (summary.get("end_price") or 0) > 0, "End price is positive", summary.get("end_price"))
    _record(results, summary.get("overall_status") == "PASS", "Regression overall status is PASS", summary.get("overall_status"))

    for name, path in EXPECTED_OUTPUTS.items():
        _record(results, path.exists(), f"Output written: {name}", path)

    rows = _read_csv_rows(EXPECTED_OUTPUTS["rows_csv"])
    _record(results, rows is not None and rows >= 6, "Regression rows CSV has expected content", f"rows={rows}")

    overall_pass = all(item["status"] == "PASS" for item in results)
    print()
    _print_header(f"Overall Phase 5-18 checkpoint status: {'PASS' if overall_pass else 'FAIL'}")

    CHECKPOINT_REPORT.write_text("\n".join(f"{r['status']:<10} {r['label']:<70} {r['detail']}" for r in results) + "\n", encoding="utf-8")
    CHECKPOINT_JSON.write_text(json.dumps({"overall_status": "PASS" if overall_pass else "FAIL", "results": results}, indent=2), encoding="utf-8")
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
