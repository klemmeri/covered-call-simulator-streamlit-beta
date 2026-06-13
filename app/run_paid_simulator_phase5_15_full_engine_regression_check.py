"""
run_paid_simulator_phase5_15_full_engine_regression_check.py

Checkpoint runner for Phase 5-15: full engine regression after simulator promotion.
"""

from __future__ import annotations

import importlib.util
import json
import py_compile
import sys
import traceback
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
DASHBOARD_FILE = APP_DIR / "paid_simulator" / "config_form_app.py"
PHASE_FILE = APP_DIR / "paid_simulator" / "phase5_full_engine_regression_after_simulator_promotion.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase5_15_full_engine_regression_after_simulator_promotion.md"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

EXPECTED_OUTPUTS = {
    "file_status_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase5_15_engine_regression_file_status.csv",
    "contract_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase5_15_engine_regression_contract.csv",
    "summary_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase5_15_engine_regression_summary.csv",
    "json": PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase5_15_engine_regression_after_simulator_promotion.json",
    "report": PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase5_15_engine_regression_after_simulator_promotion_report.txt",
}


class CheckRecorder:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(self, label: str, passed: bool, detail: Any = "") -> None:
        status = "PASS" if passed else "FAIL"
        print(f"{status:<10} {label:<70} {detail}")
        self.rows.append({"status": status, "label": label, "detail": str(detail)})

    @property
    def passed(self) -> bool:
        return all(row["status"] == "PASS" for row in self.rows)


def _compile(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
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
    print("=" * 100)
    print("Phase 5-15 full engine regression after simulator promotion check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    recorder = CheckRecorder()
    summary: dict[str, Any] | None = None

    recorder.add("Dashboard file exists", DASHBOARD_FILE.exists(), DASHBOARD_FILE)
    recorder.add("Phase 5-15 regression module exists", PHASE_FILE.exists(), PHASE_FILE)
    recorder.add("Phase 5-15 documentation exists", DOC_FILE.exists(), DOC_FILE)
    recorder.add("Live price_paths.py exists", (APP_DIR / "price_paths.py").exists(), APP_DIR / "price_paths.py")
    recorder.add("Live simulator.py exists", (APP_DIR / "simulator.py").exists(), APP_DIR / "simulator.py")

    if DASHBOARD_FILE.exists():
        ok, detail = _compile(DASHBOARD_FILE)
        recorder.add("Dashboard syntax remains valid", ok, detail)
    if PHASE_FILE.exists():
        ok, detail = _compile(PHASE_FILE)
        recorder.add("Phase 5-15 module syntax valid", ok, detail)

    try:
        module = _import_module(PHASE_FILE, "phase5_full_engine_regression_after_simulator_promotion")
        summary = module.build_phase5_15_summary()
        recorder.add("Phase 5-15 module imports and builds summary", isinstance(summary, dict), type(summary).__name__)
    except Exception as exc:
        recorder.add("Phase 5-15 module imports and builds summary", False, exc)
        traceback.print_exc()

    if isinstance(summary, dict):
        recorder.add("Regression has ready marker", summary.get("ready_marker") == "PHASE5_15_FULL_ENGINE_REGRESSION_AFTER_SIMULATOR_PROMOTION_READY", summary.get("ready_marker"))
        recorder.add("Regression has release decision", summary.get("release_decision") == "PHASE5_15_ENGINE_REGRESSION_AFTER_SIMULATOR_PROMOTION_CREATED_NO_DASHBOARD_CHANGE", summary.get("release_decision"))
        recorder.add("Regression confirms no dashboard change", summary.get("dashboard_change_required") is False, summary.get("dashboard_change_required"))
        recorder.add("Regression confirms no customer workflow change", summary.get("customer_workflow_change_required") is False, summary.get("customer_workflow_change_required"))
        recorder.add("Synthetic default remains preserved", summary.get("synthetic_default_preserved") is True, summary.get("synthetic_default_preserved"))
        recorder.add("Historical import remains explicit only", summary.get("historical_import_explicit_only") is True, summary.get("historical_import_explicit_only"))
        recorder.add("Unknown mode fallback remains safe", summary.get("unknown_mode_safe_fallback") is True, summary.get("unknown_mode_safe_fallback"))
        recorder.add("No additional core patch applied by this checkpoint", summary.get("additional_core_engine_patch_applied") is False, summary.get("additional_core_engine_patch_applied"))
        recorder.add("Core engine files are present", summary.get("core_engine_files_present") is True, summary.get("core_engine_files_present"))
        recorder.add("Regression contract has rows", (summary.get("contract_row_count") or 0) >= 5, summary.get("contract_row_count"))
        recorder.add("Regression overall status is PASS", summary.get("overall_status") == "PASS", summary.get("overall_status"))
    else:
        for label in [
            "Regression has ready marker",
            "Regression has release decision",
            "Regression confirms no dashboard change",
            "Synthetic default remains preserved",
            "Historical import remains explicit only",
            "Regression overall status is PASS",
        ]:
            recorder.add(label, False, "summary was not a dict")

    for name, path in EXPECTED_OUTPUTS.items():
        recorder.add(f"Output written: {name}", path.exists(), path)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / "phase5_15_full_engine_regression_checkpoint_report.txt"
    json_path = REPORT_DIR / "phase5_15_full_engine_regression_checkpoint.json"
    report_path.write_text("\n".join(f"{row['status']:<10} {row['label']:<70} {row['detail']}" for row in recorder.rows) + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(recorder.rows, indent=2), encoding="utf-8")

    print()
    print("=" * 100)
    if recorder.passed:
        print("Overall Phase 5-15 checkpoint status: PASS")
        status_code = 0
    else:
        print("Overall Phase 5-15 checkpoint status: FAIL")
        status_code = 1
    print("=" * 100)
    print(f"Saved checkpoint report: {report_path}")
    print(f"Saved checkpoint JSON:   {json_path}")
    return status_code


if __name__ == "__main__":
    raise SystemExit(main())
