"""
run_paid_simulator_phase5_1_engine_integration_readiness_check.py

Checkpoint script for Phase 5-1: Engine integration readiness map.
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
PAID_SIMULATOR_DIR = APP_DIR / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"

MODULE_FILE = PAID_SIMULATOR_DIR / "phase5_engine_integration_readiness.py"
DOC_FILE = DOCS_DIR / "phase5_1_engine_integration_readiness.md"
DASHBOARD_FILE = PAID_SIMULATOR_DIR / "config_form_app.py"

CHECK_REPORT = OUTPUT_REPORT_DIR / "phase5_1_engine_integration_readiness_checkpoint_report.txt"
CHECK_JSON = OUTPUT_REPORT_DIR / "phase5_1_engine_integration_readiness_checkpoint.json"


checks: list[dict[str, Any]] = []


def add_check(name: str, passed: bool, detail: Any = "") -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": str(detail)})
    status = "PASS" if passed else "FAIL"
    print(f"{status:<10} {name:<70} {detail}")


def compile_file(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "syntax valid"
    except Exception as exc:
        return False, str(exc)


def import_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    print("=" * 100)
    print("Phase 5-1 engine integration readiness check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)

    add_check("Dashboard file exists", DASHBOARD_FILE.exists(), DASHBOARD_FILE)
    add_check("Phase 5-1 readiness module exists", MODULE_FILE.exists(), MODULE_FILE)
    add_check("Phase 5-1 documentation exists", DOC_FILE.exists(), DOC_FILE)

    if DASHBOARD_FILE.exists():
        ok, detail = compile_file(DASHBOARD_FILE)
        add_check("Dashboard syntax remains valid", ok, detail)

    if MODULE_FILE.exists():
        ok, detail = compile_file(MODULE_FILE)
        add_check("Phase 5-1 module syntax valid", ok, detail)

    summary: dict[str, Any] | None = None
    try:
        module = import_module(MODULE_FILE, "phase5_engine_integration_readiness")
        summary = module.build_phase5_1_summary()
        add_check("Phase 5-1 module imports and builds readiness map", isinstance(summary, dict), type(summary).__name__)
    except Exception as exc:
        add_check("Phase 5-1 module imports and builds readiness map", False, exc)
        traceback.print_exc()

    if isinstance(summary, dict):
        add_check("Readiness map has ready marker", summary.get("ready_marker") == "PHASE5_1_ENGINE_INTEGRATION_READINESS_READY", summary.get("ready_marker"))
        add_check("Readiness map has release decision", summary.get("release_decision") == "PHASE5_1_READY_TO_BEGIN_ENGINE_HARDENING_NO_DASHBOARD_CHANGE", summary.get("release_decision"))
        add_check("Readiness map confirms no dashboard change", summary.get("dashboard_change_required") is False, summary.get("dashboard_change_required"))
        add_check("Readiness map overall status is PASS", summary.get("overall_status") == "PASS", summary.get("overall_status"))
        add_check("Readiness map has engine touchpoints", int(summary.get("touchpoint_count", 0)) >= 5, summary.get("touchpoint_count"))
        add_check("Readiness map has Phase 5 sequence", int(summary.get("phase5_checkpoint_count", 0)) >= 4, summary.get("phase5_checkpoint_count"))
        add_check("Recommended next checkpoint is Phase 5-2", "Phase 5-2" in str(summary.get("recommended_next_checkpoint", "")), summary.get("recommended_next_checkpoint"))
    else:
        add_check("Readiness summary produced", False, "summary was not a dict")

    expected_outputs = {
        "touchpoints_csv": OUTPUT_TABLE_DIR / "phase5_1_engine_integration_touchpoints.csv",
        "artifact_status_csv": OUTPUT_TABLE_DIR / "phase5_1_engine_integration_artifact_status.csv",
        "sequence_csv": OUTPUT_TABLE_DIR / "phase5_1_engine_integration_sequence.csv",
        "summary_csv": OUTPUT_TABLE_DIR / "phase5_1_engine_integration_readiness_summary.csv",
        "json": OUTPUT_REPORT_DIR / "phase5_1_engine_integration_readiness.json",
        "report": OUTPUT_REPORT_DIR / "phase5_1_engine_integration_readiness_report.txt",
    }
    for label, path in expected_outputs.items():
        add_check(f"Output written: {label}", path.exists() and path.stat().st_size > 0, path)

    overall_pass = all(row["passed"] for row in checks)
    final_status = "PASS" if overall_pass else "FAIL"

    payload = {
        "checkpoint": "Phase 5-1 engine integration readiness",
        "overall_status": final_status,
        "checks": checks,
    }
    CHECK_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    report_lines = [
        "Phase 5-1 engine integration readiness checkpoint report",
        "=" * 100,
        f"Project root: {PROJECT_ROOT}",
        "",
    ]
    for row in checks:
        status = "PASS" if row["passed"] else "FAIL"
        report_lines.append(f"{status:<10} {row['name']:<70} {row['detail']}")
    report_lines.extend([
        "",
        "=" * 100,
        f"Overall Phase 5-1 checkpoint status: {final_status}",
        "=" * 100,
    ])
    CHECK_REPORT.write_text("\n".join(report_lines), encoding="utf-8")

    print()
    print("=" * 100)
    print(f"Overall Phase 5-1 checkpoint status: {final_status}")
    print("=" * 100)
    print(f"Saved checkpoint report: {CHECK_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECK_JSON}")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
