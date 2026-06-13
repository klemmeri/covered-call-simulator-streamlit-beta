"""
run_paid_simulator_phase4_6_premium_model_calibration_check.py

Checkpoint script for Phase 4-6: Premium-model calibration report.
"""

from __future__ import annotations

import importlib.util
import py_compile
import sys
import traceback
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
PHASE4_2_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase4_market_data_input_scaffold.py"
PHASE4_3_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase4_market_data_loader_validator.py"
PHASE4_4_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase4_historical_price_path_adapter.py"
PHASE4_5_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase4_option_chain_premium_lookup.py"
PHASE4_6_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase4_premium_model_calibration_report.py"
PHASE4_6_DOC = PROJECT_ROOT / "docs" / "phase4_6_premium_model_calibration_report.md"

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CHECKPOINT_REPORT = REPORT_DIR / "phase4_6_premium_model_calibration_checkpoint_report.txt"
CHECKPOINT_JSON = REPORT_DIR / "phase4_6_premium_model_calibration_checkpoint.json"

EXPECTED_OUTPUTS = {
    "calibration_rows_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase4_6_premium_model_calibration_rows.csv",
    "calibration_summary_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase4_6_premium_model_calibration_summary.csv",
    "json": PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase4_6_premium_model_calibration_report.json",
    "report": PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase4_6_premium_model_calibration_report.txt",
}

results: list[dict[str, Any]] = []


def _print_header(title: str) -> None:
    line = "=" * 100
    print(line)
    print(title)
    print(line)


def _record(status: bool, label: str, detail: Any = "") -> None:
    result = "PASS" if status else "FAIL"
    print(f"{result:<10} {label:<70} {detail}")
    results.append({"status": result, "label": label, "detail": str(detail)})


def _compile_file(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "syntax valid"
    except Exception as exc:  # pragma: no cover - diagnostic path
        return False, str(exc)


def _import_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create module spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    _print_header("Phase 4-6 premium-model calibration report check")
    print(f"Project root: {PROJECT_ROOT}")
    print()

    _record(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    _record(PHASE4_2_FILE.exists(), "Prior Phase 4-2 scaffold module exists", PHASE4_2_FILE)
    _record(PHASE4_3_FILE.exists(), "Prior Phase 4-3 loader-validator module exists", PHASE4_3_FILE)
    _record(PHASE4_4_FILE.exists(), "Prior Phase 4-4 historical-path adapter module exists", PHASE4_4_FILE)
    _record(PHASE4_5_FILE.exists(), "Prior Phase 4-5 option-chain lookup module exists", PHASE4_5_FILE)
    _record(PHASE4_6_FILE.exists(), "Phase 4-6 calibration module exists", PHASE4_6_FILE)
    _record(PHASE4_6_DOC.exists(), "Phase 4-6 documentation exists", PHASE4_6_DOC)

    if DASHBOARD_FILE.exists():
        ok, detail = _compile_file(DASHBOARD_FILE)
        _record(ok, "Dashboard syntax remains valid", detail)

    summary: dict[str, Any] | None = None
    if PHASE4_6_FILE.exists():
        ok, detail = _compile_file(PHASE4_6_FILE)
        _record(ok, "Phase 4-6 module syntax valid", detail)
        if ok:
            try:
                module = _import_module(PHASE4_6_FILE, "phase4_premium_model_calibration_report")
                summary = module.build_phase4_6_summary()
                _record(isinstance(summary, dict), "Phase 4-6 module imports and builds calibration report", type(summary).__name__)
            except Exception as exc:
                _record(False, "Phase 4-6 module imports and builds calibration report", exc)
                traceback.print_exc()

    if not isinstance(summary, dict):
        summary = {}

    _record(summary.get("ready_marker") == "PHASE4_6_PREMIUM_MODEL_CALIBRATION_READY", "Calibration report has ready marker", summary.get("ready_marker"))
    _record(summary.get("release_decision") == "PHASE4_6_PREMIUM_MODEL_CALIBRATION_REPORT_CREATED_NO_DASHBOARD_CHANGE", "Calibration report has release decision", summary.get("release_decision"))
    _record(summary.get("dashboard_change_required") is False, "Calibration report confirms no dashboard change", summary.get("dashboard_change_required"))
    _record(summary.get("source_mode") == "option_chain_calibration", "Calibration report uses option-chain calibration mode", summary.get("source_mode"))
    _record(summary.get("overall_status") == "PASS", "Calibration report overall status is PASS", summary.get("overall_status"))
    _record((summary.get("raw_option_chain_rows") or 0) > 0, "Raw option-chain calibration input has rows", summary.get("raw_option_chain_rows"))
    _record((summary.get("calibration_rows") or 0) > 0, "Calibration output has rows", summary.get("calibration_rows"))
    _record(summary.get("mean_observed_premium", 0) > 0, "Mean observed premium is positive", summary.get("mean_observed_premium"))
    _record(summary.get("mean_model_estimated_premium", 0) > 0, "Mean model estimated premium is positive", summary.get("mean_model_estimated_premium"))
    _record(summary.get("mean_absolute_premium_error", -1) >= 0, "Mean absolute premium error is non-negative", summary.get("mean_absolute_premium_error"))

    for label, path in EXPECTED_OUTPUTS.items():
        _record(path.exists(), f"Output written: {label}", path)

    rows_csv = EXPECTED_OUTPUTS["calibration_rows_csv"]
    if rows_csv.exists():
        try:
            df = pd.read_csv(rows_csv)
            required_cols = {
                "observed_premium",
                "model_estimated_premium",
                "premium_error",
                "absolute_premium_error",
                "percentage_premium_error",
            }
            _record(len(df) > 0 and required_cols.issubset(set(df.columns)), "Calibration rows CSV has expected content", f"rows={len(df)}")
        except Exception as exc:
            _record(False, "Calibration rows CSV has expected content", exc)

    overall_pass = all(item["status"] == "PASS" for item in results)

    print()
    _print_header(f"Overall Phase 4-6 checkpoint status: {'PASS' if overall_pass else 'FAIL'}")

    report_lines = [
        "Phase 4-6 premium-model calibration checkpoint report",
        "=" * 100,
        f"Project root: {PROJECT_ROOT}",
        "",
    ]
    for item in results:
        report_lines.append(f"{item['status']:<10} {item['label']:<70} {item['detail']}")
    report_lines.append("")
    report_lines.append(f"Overall Phase 4-6 checkpoint status: {'PASS' if overall_pass else 'FAIL'}")
    CHECKPOINT_REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    import json

    CHECKPOINT_JSON.write_text(json.dumps({"overall_pass": overall_pass, "results": results}, indent=2), encoding="utf-8")

    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
