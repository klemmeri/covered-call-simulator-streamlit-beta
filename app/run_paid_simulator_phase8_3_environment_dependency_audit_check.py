"""
run_paid_simulator_phase8_3_environment_dependency_audit_check.py

Phase 8-3 environment and dependency audit check.
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
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase8_environment_dependency_audit.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase8_3_environment_dependency_audit.md"
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

DEPENDENCIES_CSV = OUTPUT_TABLE_DIR / "phase8_3_environment_dependency_audit_dependencies.csv"
FILES_CSV = OUTPUT_TABLE_DIR / "phase8_3_environment_dependency_audit_required_files.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase8_3_environment_dependency_audit_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase8_3_environment_dependency_audit.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase8_3_environment_dependency_audit_report.txt"

CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase8_3_environment_dependency_audit_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase8_3_environment_dependency_audit_checkpoint.json"

READY_MARKER = "PHASE8_3_ENVIRONMENT_DEPENDENCY_AUDIT_READY"
RELEASE_DECISION = "PHASE8_3_ENVIRONMENT_DEPENDENCY_AUDIT_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "environment_dependency_audit"


class Recorder:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(self, passed: bool, label: str, detail: Any = "") -> None:
        status = "PASS" if passed else "FAIL"
        detail_text = "" if detail is None else str(detail)
        self.rows.append({"status": status, "label": label, "detail": detail_text})
        print(f"{status:<10} {label:<76} {detail_text}")

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
    print("Phase 8-3 environment and dependency audit check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    summary: dict[str, Any] = {}

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(MODULE_FILE.exists(), "Phase 8-3 environment audit module exists", MODULE_FILE)
    rec.add(DOC_FILE.exists(), "Phase 8-3 documentation exists", DOC_FILE)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    ok, detail = _compile_file(MODULE_FILE)
    rec.add(ok, "Phase 8-3 module syntax valid", detail)

    try:
        module = _import_module(MODULE_FILE, "phase8_environment_dependency_audit")
        summary = module.build_phase8_3_summary()
        rec.add(isinstance(summary, dict), "Phase 8-3 module imports and writes outputs", type(summary).__name__)
    except Exception as exc:
        rec.add(False, "Phase 8-3 module imports and writes outputs", exc)
        traceback.print_exc()

    rec.add(summary.get("ready_marker") == READY_MARKER, "Environment audit has ready marker", summary.get("ready_marker"))
    rec.add(summary.get("release_decision") == RELEASE_DECISION, "Environment audit has release decision", summary.get("release_decision"))
    rec.add(summary.get("source_mode") == SOURCE_MODE, "Environment audit uses expected source mode", summary.get("source_mode"))
    rec.add(summary.get("dashboard_change_required") is False, "No dashboard change required", summary.get("dashboard_change_required"))
    rec.add(summary.get("engine_change_required") is False, "No engine change required", summary.get("engine_change_required"))
    rec.add(summary.get("environment_dependency_audit_created") is True, "Environment dependency audit created", summary.get("environment_dependency_audit_created"))
    rec.add(isinstance(summary.get("python_version"), str) and len(summary.get("python_version", "")) > 0, "Python version captured", summary.get("python_version"))
    rec.add(isinstance(summary.get("core_package_rows"), int) and summary.get("core_package_rows", 0) >= 4, "Core package table has rows", summary.get("core_package_rows"))
    rec.add(isinstance(summary.get("required_file_rows"), int) and summary.get("required_file_rows", 0) >= 6, "Required file table has rows", summary.get("required_file_rows"))
    rec.add(summary.get("all_required_files_present") is True, "All required project files are present", summary.get("all_required_files_present"))
    rec.add(summary.get("requirements_file_needed") is True, "Requirements file need identified", summary.get("requirements_file_needed"))
    rec.add(summary.get("streamlit_mvp_path_supported") is True, "Streamlit MVP path remains supported", summary.get("streamlit_mvp_path_supported"))
    rec.add(summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    rec.add(summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    rec.add(summary.get("historical_data_is_scenario_input_not_forecast") is True, "Historical data is scenario input, not forecast", summary.get("historical_data_is_scenario_input_not_forecast"))

    for label, path in [
        ("dependencies_csv", DEPENDENCIES_CSV),
        ("required_files_csv", FILES_CSV),
        ("summary_csv", SUMMARY_CSV),
        ("json", JSON_REPORT),
        ("report", TEXT_REPORT),
    ]:
        rec.add(path.exists(), f"Output written: {label}", path)

    deps_ok = False
    deps_detail = "missing"
    if DEPENDENCIES_CSV.exists():
        try:
            df = pd.read_csv(DEPENDENCIES_CSV)
            text = df.astype(str).to_string(index=False)
            deps_ok = len(df) >= 4 and "pandas" in text and "streamlit" in text and "installed" in df.columns
            deps_detail = f"rows={len(df)}"
        except Exception as exc:
            deps_detail = str(exc)
    rec.add(deps_ok, "Dependency CSV has expected content", deps_detail)

    files_ok = False
    files_detail = "missing"
    if FILES_CSV.exists():
        try:
            df = pd.read_csv(FILES_CSV)
            text = df.astype(str).to_string(index=False)
            files_ok = len(df) >= 6 and "config_form_app.py" in text and bool(df["exists"].all())
            files_detail = f"rows={len(df)}"
        except Exception as exc:
            files_detail = str(exc)
    rec.add(files_ok, "Required-files CSV has expected content", files_detail)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall Phase 8-3 checkpoint status: {final_status}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join([f"{r['status']:<10} {r['label']:<76} {r['detail']}" for r in rec.rows] + ["", f"Overall Phase 8-3 checkpoint status: {final_status}"]) + "\n",
        encoding="utf-8",
    )
    CHECKPOINT_JSON.write_text(json.dumps({"overall_status": final_status, "checks": rec.rows}, indent=2), encoding="utf-8")
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if rec.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
