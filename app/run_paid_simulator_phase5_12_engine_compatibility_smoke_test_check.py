"""
run_paid_simulator_phase5_12_engine_compatibility_smoke_test_check.py

Checkpoint runner for Phase 5-12.
"""

from __future__ import annotations

import importlib.util
import json
import py_compile
import sys
import traceback
from pathlib import Path
from typing import Any

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent
PAID_DIR = APP_DIR / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

MODULE_FILE = PAID_DIR / "phase5_engine_compatibility_smoke_test.py"
DOC_FILE = DOCS_DIR / "phase5_12_engine_compatibility_smoke_test.md"
DASHBOARD_FILE = PAID_DIR / "config_form_app.py"
LIVE_PRICE_PATHS_FILE = APP_DIR / "price_paths.py"

CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase5_12_engine_compatibility_smoke_test_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase5_12_engine_compatibility_smoke_test_checkpoint.json"

EXPECTED_OUTPUTS = {
    "rows_csv": OUTPUT_TABLE_DIR / "phase5_12_engine_compatibility_smoke_test_rows.csv",
    "summary_csv": OUTPUT_TABLE_DIR / "phase5_12_engine_compatibility_smoke_test_summary.csv",
    "json": OUTPUT_REPORT_DIR / "phase5_12_engine_compatibility_smoke_test.json",
    "report": OUTPUT_REPORT_DIR / "phase5_12_engine_compatibility_smoke_test_report.txt",
}


def _print_header(title: str) -> None:
    print("=" * 100)
    print(title)
    print("=" * 100)


def _record(results: list[dict[str, Any]], passed: bool, label: str, detail: Any = "") -> None:
    status = "PASS" if passed else "FAIL"
    print(f"{status:<10} {label:<70} {detail}")
    results.append({"passed": bool(passed), "label": label, "detail": str(detail)})


def _compile_file(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "syntax valid"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def _import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not build import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    if str(APP_DIR) not in sys.path:
        sys.path.insert(0, str(APP_DIR))
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    _print_header("Phase 5-12 engine compatibility smoke test check")
    print(f"Project root: {PROJECT_ROOT}")
    print()

    results: list[dict[str, Any]] = []
    summary: dict[str, Any] | None = None

    _record(results, DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    _record(results, LIVE_PRICE_PATHS_FILE.exists(), "Live promoted price_paths.py exists", LIVE_PRICE_PATHS_FILE)
    _record(results, MODULE_FILE.exists(), "Phase 5-12 smoke-test module exists", MODULE_FILE)
    _record(results, DOC_FILE.exists(), "Phase 5-12 documentation exists", DOC_FILE)

    if DASHBOARD_FILE.exists():
        ok, detail = _compile_file(DASHBOARD_FILE)
        _record(results, ok, "Dashboard syntax remains valid", detail)

    if LIVE_PRICE_PATHS_FILE.exists():
        ok, detail = _compile_file(LIVE_PRICE_PATHS_FILE)
        _record(results, ok, "Live price_paths.py syntax valid", detail)

    if MODULE_FILE.exists():
        ok, detail = _compile_file(MODULE_FILE)
        _record(results, ok, "Phase 5-12 module syntax valid", detail)

    try:
        module = _import_module(MODULE_FILE, "phase5_engine_compatibility_smoke_test")
        summary = module.build_phase5_12_summary()
        _record(results, isinstance(summary, dict), "Phase 5-12 module imports and builds smoke test", type(summary).__name__)
    except Exception as exc:
        _record(results, False, "Phase 5-12 module imports and builds smoke test", exc)
        traceback.print_exc()

    if isinstance(summary, dict):
        _record(results, summary.get("ready_marker") == "PHASE5_12_ENGINE_COMPATIBILITY_SMOKE_TEST_READY", "Smoke test has ready marker", summary.get("ready_marker"))
        _record(results, summary.get("release_decision") == "PHASE5_12_ENGINE_COMPATIBILITY_SMOKE_TEST_CREATED_NO_DASHBOARD_CHANGE", "Smoke test has release decision", summary.get("release_decision"))
        _record(results, summary.get("dashboard_change_required") is False, "Smoke test confirms no dashboard change", summary.get("dashboard_change_required"))
        _record(results, summary.get("source_mode") == "engine_compatibility_smoke_test", "Smoke test uses compatibility mode", summary.get("source_mode"))
        _record(results, summary.get("selected_mode") == "synthetic", "Smoke test preserves selected synthetic mode", summary.get("selected_mode"))
        _record(results, summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
        _record(results, summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
        _record(results, summary.get("module_imported") is True, "Live price_paths module imports", summary.get("module_imported"))
        _record(results, summary.get("generate_price_paths_present") is True, "generate_price_paths remains present", summary.get("generate_price_paths_present"))
        _record(results, summary.get("synthetic_smoke_test_passed") is True, "Synthetic smoke test passed", summary.get("synthetic_smoke_test_passed"))
        _record(results, summary.get("unknown_mode_falls_back_or_remains_safe") is True, "Unknown mode remains safe", summary.get("unknown_mode_falls_back_or_remains_safe"))
        _record(results, int(summary.get("row_count", 0) or 0) >= 2, "Smoke-test rows exist", summary.get("row_count"))
        _record(results, summary.get("overall_status") == "PASS", "Smoke-test overall status is PASS", summary.get("overall_status"))

    for label, path in EXPECTED_OUTPUTS.items():
        _record(results, path.exists(), f"Output written: {label}", path)

    rows_path = EXPECTED_OUTPUTS["rows_csv"]
    if rows_path.exists():
        try:
            rows_df = pd.read_csv(rows_path)
            _record(results, len(rows_df) >= 2, "Smoke-test rows CSV has expected content", f"rows={len(rows_df)}")
        except Exception as exc:
            _record(results, False, "Smoke-test rows CSV has expected content", exc)

    all_passed = all(item["passed"] for item in results)

    print()
    _print_header(f"Overall Phase 5-12 checkpoint status: {'PASS' if all_passed else 'FAIL'}")

    report_lines = [
        "Phase 5-12 engine compatibility smoke test checkpoint report",
        "=" * 100,
        f"Project root: {PROJECT_ROOT}",
        f"Overall status: {'PASS' if all_passed else 'FAIL'}",
        "",
    ]
    for item in results:
        status = "PASS" if item["passed"] else "FAIL"
        report_lines.append(f"{status:<8} {item['label']:<70} {item['detail']}")
    CHECKPOINT_REPORT.write_text("\n".join(report_lines), encoding="utf-8")
    CHECKPOINT_JSON.write_text(json.dumps({"overall_status": "PASS" if all_passed else "FAIL", "results": results, "summary": summary}, indent=2), encoding="utf-8")

    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
