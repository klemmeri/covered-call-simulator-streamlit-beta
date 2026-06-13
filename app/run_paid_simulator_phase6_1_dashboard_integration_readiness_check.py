"""
run_paid_simulator_phase6_1_dashboard_integration_readiness_check.py

Checkpoint script for Phase 6-1 dashboard integration readiness.
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
PROJECT_ROOT = CURRENT_FILE.parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_DIR = APP_DIR / "paid_simulator"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

DASHBOARD_FILE = PAID_DIR / "config_form_app.py"
PHASE6_1_FILE = PAID_DIR / "phase6_dashboard_integration_readiness.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase6_1_dashboard_integration_readiness.md"

CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase6_1_dashboard_integration_readiness_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase6_1_dashboard_integration_readiness_checkpoint.json"

EXPECTED_OUTPUTS = {
    "artifact_status_csv": OUTPUT_TABLE_DIR / "phase6_1_dashboard_integration_artifact_status.csv",
    "touchpoints_csv": OUTPUT_TABLE_DIR / "phase6_1_dashboard_integration_touchpoints.csv",
    "sequence_csv": OUTPUT_TABLE_DIR / "phase6_1_recommended_dashboard_integration_sequence.csv",
    "summary_csv": OUTPUT_TABLE_DIR / "phase6_1_dashboard_integration_readiness_summary.csv",
    "json": OUTPUT_REPORT_DIR / "phase6_1_dashboard_integration_readiness.json",
    "report": OUTPUT_REPORT_DIR / "phase6_1_dashboard_integration_readiness_report.txt",
}

results: list[dict[str, Any]] = []


def record(name: str, passed: bool, detail: Any = "") -> None:
    status = "PASS" if passed else "FAIL"
    results.append({"check": name, "status": status, "detail": str(detail)})
    print(f"{status:<10} {name:<70} {detail}")


def _compile_file(path: Path, label: str) -> None:
    try:
        py_compile.compile(str(path), doraise=True)
        record(f"{label} syntax valid", True, "syntax valid")
    except Exception as exc:
        record(f"{label} syntax valid", False, exc)
        traceback.print_exc()


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
    print("Phase 6-1 dashboard integration readiness check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    record("Dashboard file exists", DASHBOARD_FILE.exists(), DASHBOARD_FILE)
    record("Phase 6-1 readiness module exists", PHASE6_1_FILE.exists(), PHASE6_1_FILE)
    record("Phase 6-1 documentation exists", DOC_FILE.exists(), DOC_FILE)

    if DASHBOARD_FILE.exists():
        _compile_file(DASHBOARD_FILE, "Dashboard")
    if PHASE6_1_FILE.exists():
        _compile_file(PHASE6_1_FILE, "Phase 6-1 module")

    summary: dict[str, Any] | None = None
    if PHASE6_1_FILE.exists():
        try:
            module = _import_module(PHASE6_1_FILE, "phase6_dashboard_integration_readiness")
            summary = module.build_phase6_1_summary()
            record("Phase 6-1 module imports and builds readiness map", isinstance(summary, dict), type(summary).__name__)
        except Exception as exc:
            record("Phase 6-1 module imports and builds readiness map", False, exc)
            traceback.print_exc()

    if not isinstance(summary, dict):
        summary = {}

    record("Readiness map has ready marker", summary.get("ready_marker") == "PHASE6_1_DASHBOARD_INTEGRATION_READINESS_READY", summary.get("ready_marker"))
    record("Readiness map has release decision", summary.get("release_decision") == "PHASE6_1_DASHBOARD_INTEGRATION_READINESS_CREATED_NO_DASHBOARD_CHANGE", summary.get("release_decision"))
    record("Readiness map confirms no dashboard change", summary.get("dashboard_changed") is False, summary.get("dashboard_changed"))
    record("Readiness map uses dashboard-readiness mode", summary.get("source_mode") == "dashboard_integration_readiness", summary.get("source_mode"))
    record("Synthetic default remains preserved", summary.get("synthetic_default_preserved") is True, summary.get("synthetic_default_preserved"))
    record("Historical mode remains explicit only", summary.get("historical_mode_explicit_only") is True, summary.get("historical_mode_explicit_only"))
    record("Dashboard file confirmed by summary", summary.get("dashboard_file_exists") is True, summary.get("dashboard_file_exists"))
    record("Dashboard touchpoints mapped", int(summary.get("dashboard_touchpoint_rows") or 0) >= 5, summary.get("dashboard_touchpoint_rows"))
    record("Recommended sequence mapped", int(summary.get("recommended_sequence_rows") or 0) >= 5, summary.get("recommended_sequence_rows"))
    record("Readiness overall status acceptable", summary.get("overall_status") in {"PASS", "REVIEW"}, summary.get("overall_status"))

    for label, path in EXPECTED_OUTPUTS.items():
        record(f"Output written: {label}", path.exists(), path)

    if EXPECTED_OUTPUTS["touchpoints_csv"].exists():
        try:
            df = pd.read_csv(EXPECTED_OUTPUTS["touchpoints_csv"])
            record("Touchpoints CSV has expected content", len(df) >= 5, f"rows={len(df)}")
        except Exception as exc:
            record("Touchpoints CSV has expected content", False, exc)

    overall_pass = all(item["status"] == "PASS" for item in results)

    print()
    print("=" * 100)
    print(f"Overall Phase 6-1 checkpoint status: {'PASS' if overall_pass else 'FAIL'}")
    print("=" * 100)

    report_lines = [
        "Phase 6-1 dashboard integration readiness checkpoint report",
        "=" * 80,
        f"Project root: {PROJECT_ROOT}",
        "",
    ]
    for item in results:
        report_lines.append(f"{item['status']:<10} {item['check']:<70} {item['detail']}")
    report_lines.extend(["", f"Overall Phase 6-1 checkpoint status: {'PASS' if overall_pass else 'FAIL'}"])
    CHECKPOINT_REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    CHECKPOINT_JSON.write_text(json.dumps({"overall_pass": overall_pass, "results": results, "summary": summary}, indent=2), encoding="utf-8")

    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
