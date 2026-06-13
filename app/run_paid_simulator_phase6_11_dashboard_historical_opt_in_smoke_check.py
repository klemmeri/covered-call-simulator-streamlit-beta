"""
run_paid_simulator_phase6_11_dashboard_historical_opt_in_smoke_check.py

Phase 6-11 dashboard end-to-end historical opt-in smoke test check.

This repair replaces the prior malformed check script with a syntactically safe
version. It makes no dashboard changes.
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
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase6_dashboard_historical_opt_in_smoke_test.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase6_11_dashboard_historical_opt_in_smoke_test.md"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase6_11_dashboard_historical_opt_in_smoke_summary.csv"
CASES_CSV = OUTPUT_TABLE_DIR / "phase6_11_dashboard_historical_opt_in_smoke_cases.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase6_11_dashboard_historical_opt_in_smoke.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase6_11_dashboard_historical_opt_in_smoke_report.txt"
CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase6_11_dashboard_historical_opt_in_smoke_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase6_11_dashboard_historical_opt_in_smoke_checkpoint.json"

READY_MARKER = "PHASE6_11_DASHBOARD_HISTORICAL_OPT_IN_SMOKE_READY"
RELEASE_DECISION = "PHASE6_11_DASHBOARD_HISTORICAL_OPT_IN_SMOKE_PASSED_NO_DASHBOARD_CHANGE"
SOURCE_MODE = "dashboard_historical_opt_in_smoke_test"
CAUTION = "Historical data is scenario input, not forecast"


class Recorder:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(self, passed: bool, label: str, detail: Any = "") -> None:
        status = "PASS" if passed else "FAIL"
        detail_text = "" if detail is None else str(detail)
        self.rows.append({"status": status, "label": label, "detail": detail_text})
        print(f"{status:<10} {label:<78} {detail_text}")

    @property
    def passed(self) -> bool:
        return all(row["status"] == "PASS" for row in self.rows)


def _compile_file(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        return True, "syntax valid"
    except Exception as exc:
        return False, str(exc)


def _import_module(path: Path, module_name: str):
    if module_name in sys.modules:
        del sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 100)
    print("Phase 6-11 dashboard end-to-end historical opt-in smoke test check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    summary: dict[str, Any] = {}
    module = None

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(MODULE_FILE.exists(), "Phase 6-11 smoke-test module exists", MODULE_FILE)
    rec.add(DOC_FILE.exists(), "Phase 6-11 documentation exists", DOC_FILE)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    dashboard_text = DASHBOARD_FILE.read_text(encoding="utf-8") if DASHBOARD_FILE.exists() else ""
    for marker in [
        "PHASE6_6_DASHBOARD_HISTORICAL_INPUT_PANEL_PATCH_READY",
        "PHASE6_9_DASHBOARD_RUNNER_WIRING_PATCH_READY",
        "phase6_6_build_historical_input_panel_contract",
        "phase6_9_resolve_dashboard_runner_mode",
        "Synthetic scenarios",
        "Imported historical data",
        CAUTION,
    ]:
        rec.add(marker in dashboard_text, f"Dashboard contains marker: {marker}", "present" if marker in dashboard_text else None)

    ok, detail = _compile_file(MODULE_FILE)
    rec.add(ok, "Phase 6-11 module syntax valid", detail)

    try:
        module = _import_module(MODULE_FILE, "phase6_dashboard_historical_opt_in_smoke_test")
        summary = module.build_phase6_11_summary()
        rec.add(isinstance(summary, dict), "Phase 6-11 module imports and writes outputs", type(summary).__name__)
    except Exception as exc:
        rec.add(False, "Phase 6-11 module imports and writes outputs", exc)
        traceback.print_exc()

    rec.add(summary.get("ready_marker") == READY_MARKER, "Smoke test has ready marker", summary.get("ready_marker"))
    rec.add(summary.get("release_decision") == RELEASE_DECISION, "Smoke test has release decision", summary.get("release_decision"))
    rec.add(summary.get("dashboard_change_required") is False, "Smoke test confirms no dashboard change", summary.get("dashboard_change_required"))
    rec.add(summary.get("source_mode") == SOURCE_MODE, "Smoke test uses expected source mode", summary.get("source_mode"))
    rec.add(summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    rec.add(summary.get("default_runner_mode") == "synthetic", "Default runner mode is synthetic", summary.get("default_runner_mode"))
    rec.add(summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    rec.add(summary.get("historical_runner_mode") == "historical_import", "Historical mode maps to historical_import", summary.get("historical_runner_mode"))
    rec.add(summary.get("historical_mode_selected_only_when_explicit") is True, "Historical mode selected only when explicit", summary.get("historical_mode_selected_only_when_explicit"))
    rec.add(summary.get("unknown_modes_fall_back_to_synthetic") is True, "Unknown modes fall back to synthetic", summary.get("unknown_modes_fall_back_to_synthetic"))
    rec.add(summary.get("none_mode_falls_back_to_synthetic") is True, "None/missing mode falls back to synthetic", summary.get("none_mode_falls_back_to_synthetic"))
    rec.add(summary.get("historical_data_is_scenario_input_not_forecast") is True, "Historical data is scenario input, not forecast", summary.get("historical_data_is_scenario_input_not_forecast"))
    rec.add(summary.get("cases_all_pass") is True, "All opt-in smoke-test cases pass", summary.get("cases_all_pass"))
    rec.add(isinstance(summary.get("case_rows"), int) and summary.get("case_rows", 0) >= 4, "Smoke-test case table has rows", summary.get("case_rows"))

    if module is not None:
        try:
            default_case = module.resolve_phase6_11_dashboard_mode("Synthetic scenarios")
            historical_case = module.resolve_phase6_11_dashboard_mode("Imported historical data")
            unknown_case = module.resolve_phase6_11_dashboard_mode("unexpected")
            none_case = module.resolve_phase6_11_dashboard_mode(None)
            rec.add(default_case.get("runner_mode") == "synthetic", "Resolver default synthetic case works", default_case.get("runner_mode"))
            rec.add(historical_case.get("runner_mode") == "historical_import", "Resolver explicit historical case works", historical_case.get("runner_mode"))
            rec.add(unknown_case.get("runner_mode") == "synthetic", "Resolver unknown fallback case works", unknown_case.get("runner_mode"))
            rec.add(none_case.get("runner_mode") == "synthetic", "Resolver None fallback case works", none_case.get("runner_mode"))
        except Exception as exc:
            rec.add(False, "Resolver cases execute", exc)

    for label, path in [
        ("summary_csv", SUMMARY_CSV),
        ("cases_csv", CASES_CSV),
        ("json", JSON_REPORT),
        ("report", TEXT_REPORT),
    ]:
        rec.add(path.exists(), f"Output written: {label}", path)

    cases_ok = False
    cases_detail = "missing"
    if CASES_CSV.exists():
        try:
            df = pd.read_csv(CASES_CSV)
            cases_ok = len(df) >= 4 and bool(df["runner_mode_ok"].all()) and bool(df["historical_selection_ok"].all())
            cases_detail = f"rows={len(df)}"
        except Exception as exc:
            cases_detail = str(exc)
    rec.add(cases_ok, "Smoke-test cases CSV has expected content", cases_detail)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall Phase 6-11 checkpoint status: {final_status}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join([f"{r['status']:<10} {r['label']:<78} {r['detail']}" for r in rec.rows] + ["", f"Overall Phase 6-11 checkpoint status: {final_status}"]) + "\n",
        encoding="utf-8",
    )
    CHECKPOINT_JSON.write_text(json.dumps({"overall_status": final_status, "checks": rec.rows}, indent=2), encoding="utf-8")
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if rec.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
