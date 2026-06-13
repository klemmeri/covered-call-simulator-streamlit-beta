"""
run_paid_simulator_phase5_5_historical_mode_smoke_test_check.py

Checkpoint check for Phase 5-5 historical-mode simulation smoke test.
"""

from __future__ import annotations

import importlib.util
import json
import py_compile
import traceback
from pathlib import Path
from typing import Any

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]

DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
PHASE5_5_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase5_historical_mode_simulation_smoke_test.py"
PHASE5_5_DOC = PROJECT_ROOT / "docs" / "phase5_5_historical_mode_simulation_smoke_test.md"
PRIOR_PHASE5_4_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase5_controlled_engine_patch_historical_paths.py"

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CHECKPOINT_REPORT = REPORT_DIR / "phase5_5_historical_mode_simulation_smoke_test_checkpoint_report.txt"
CHECKPOINT_JSON = REPORT_DIR / "phase5_5_historical_mode_simulation_smoke_test_checkpoint.json"

EXPECTED_OUTPUTS = {
    "rows_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase5_5_historical_mode_smoke_test_rows.csv",
    "summary_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase5_5_historical_mode_smoke_test_summary.csv",
    "json": PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase5_5_historical_mode_smoke_test.json",
    "report": PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase5_5_historical_mode_smoke_test_report.txt",
}


def _compile(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "syntax valid"
    except Exception as exc:
        return False, str(exc)


def _import_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _record(results: list[dict[str, Any]], passed: bool, label: str, detail: Any = "") -> None:
    results.append({"passed": bool(passed), "label": label, "detail": "" if detail is None else str(detail)})


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    summary: dict[str, Any] = {}

    print("=" * 100)
    print("Phase 5-5 historical-mode simulation smoke test check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    _record(results, DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    _record(results, PRIOR_PHASE5_4_FILE.exists(), "Prior Phase 5-4 controlled engine patch module exists", PRIOR_PHASE5_4_FILE)
    _record(results, PHASE5_5_FILE.exists(), "Phase 5-5 smoke-test module exists", PHASE5_5_FILE)
    _record(results, PHASE5_5_DOC.exists(), "Phase 5-5 documentation exists", PHASE5_5_DOC)

    ok, detail = _compile(DASHBOARD_FILE)
    _record(results, ok, "Dashboard syntax remains valid", detail)

    ok, detail = _compile(PHASE5_5_FILE)
    _record(results, ok, "Phase 5-5 module syntax valid", detail)

    try:
        module = _import_module(PHASE5_5_FILE, "phase5_historical_mode_simulation_smoke_test")
        summary = module.build_phase5_5_summary()
        _record(results, isinstance(summary, dict), "Phase 5-5 module imports and builds smoke test", type(summary).__name__)
    except Exception as exc:
        _record(results, False, "Phase 5-5 module imports and builds smoke test", exc)
        traceback.print_exc()

    _record(results, summary.get("ready_marker") == "PHASE5_5_HISTORICAL_MODE_SIMULATION_SMOKE_TEST_READY", "Smoke test has ready marker", summary.get("ready_marker"))
    _record(results, summary.get("release_decision") == "PHASE5_5_HISTORICAL_MODE_SMOKE_TEST_CREATED_NO_DASHBOARD_CHANGE", "Smoke test has release decision", summary.get("release_decision"))
    _record(results, summary.get("dashboard_change_required") is False, "Smoke test confirms no dashboard change", summary.get("dashboard_change_required"))
    _record(results, summary.get("source_mode") == "historical_mode_smoke_test", "Smoke test uses historical smoke-test mode", summary.get("source_mode"))
    _record(results, summary.get("requested_mode") == "historical_import", "Smoke test requested historical import", summary.get("requested_mode"))
    _record(results, summary.get("selected_mode") == "historical_import", "Smoke test selected historical import", summary.get("selected_mode"))
    _record(results, summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    _record(results, summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    _record(results, summary.get("simulation_smoke_test_created") is True, "Simulation smoke test created", summary.get("simulation_smoke_test_created"))
    _record(results, isinstance(summary.get("historical_path_rows"), int) and summary.get("historical_path_rows") >= 1, "Historical path has rows", summary.get("historical_path_rows"))
    _record(results, isinstance(summary.get("comparison_rows"), int) and summary.get("comparison_rows") >= 2, "Strategy comparison has rows", summary.get("comparison_rows"))
    _record(results, summary.get("start_price", 0) > 0, "Start price is positive", summary.get("start_price"))
    _record(results, summary.get("end_price", 0) > 0, "End price is positive", summary.get("end_price"))
    _record(results, summary.get("premium_per_share", -1) >= 0, "Premium per share is non-negative", summary.get("premium_per_share"))
    _record(results, summary.get("overall_status") == "PASS", "Smoke-test overall status is PASS", summary.get("overall_status"))

    for label, path in EXPECTED_OUTPUTS.items():
        _record(results, path.exists(), f"Output written: {label}", path)

    rows_path = EXPECTED_OUTPUTS["rows_csv"]
    try:
        rows_df = pd.read_csv(rows_path)
        _record(results, len(rows_df) >= 2 and "strategy" in rows_df.columns, "Smoke-test rows CSV has expected content", f"rows={len(rows_df)}")
    except Exception as exc:
        _record(results, False, "Smoke-test rows CSV has expected content", exc)

    overall_pass = all(item["passed"] for item in results)

    for item in results:
        status = "PASS" if item["passed"] else "FAIL"
        print(f"{status:<10} {item['label']:<70} {item['detail']}")

    print()
    print("=" * 100)
    final_status = "PASS" if overall_pass else "FAIL"
    print(f"Overall Phase 5-5 checkpoint status: {final_status}")
    print("=" * 100)

    checkpoint_payload = {
        "overall_status": final_status,
        "summary": summary,
        "results": results,
    }
    CHECKPOINT_JSON.write_text(json.dumps(checkpoint_payload, indent=2), encoding="utf-8")

    report_lines = [
        "Phase 5-5 historical-mode simulation smoke test checkpoint report",
        "=" * 100,
        f"Overall status: {final_status}",
        "",
    ]
    for item in results:
        status = "PASS" if item["passed"] else "FAIL"
        report_lines.append(f"{status:<10} {item['label']:<70} {item['detail']}")
    CHECKPOINT_REPORT.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
