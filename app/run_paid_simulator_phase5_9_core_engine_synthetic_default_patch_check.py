"""
run_paid_simulator_phase5_9_core_engine_synthetic_default_patch_check.py

Checkpoint script for Phase 5-9.
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


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
DASHBOARD_FILE = APP_DIR / "paid_simulator" / "config_form_app.py"
MODULE_FILE = APP_DIR / "paid_simulator" / "phase5_core_engine_synthetic_default_patch.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase5_9_core_engine_synthetic_default_patch.md"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CHECKPOINT_REPORT = REPORT_DIR / "phase5_9_core_engine_synthetic_default_patch_checkpoint_report.txt"
CHECKPOINT_JSON = REPORT_DIR / "phase5_9_core_engine_synthetic_default_patch_checkpoint.json"

EXPECTED_OUTPUTS = {
    "engine_file_status_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase5_9_engine_file_status.csv",
    "prior_artifact_status_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase5_9_prior_artifact_status.csv",
    "engine_mode_contract_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase5_9_engine_mode_contract.csv",
    "patch_readiness_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase5_9_core_engine_patch_readiness.csv",
    "summary_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase5_9_core_engine_synthetic_default_patch_summary.csv",
    "json": PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase5_9_core_engine_synthetic_default_patch.json",
    "report": PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase5_9_core_engine_synthetic_default_patch_report.txt",
}

results: list[dict[str, Any]] = []


def record(status: bool, label: str, detail: Any = "") -> None:
    results.append({"status": "PASS" if status else "FAIL", "label": label, "detail": str(detail)})
    print(f"{'PASS' if status else 'FAIL':<10} {label:<72} {detail}")


def import_module_from_path(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    print("=" * 100)
    print("Phase 5-9 core engine synthetic-default patch check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] | None = None

    record(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    record(MODULE_FILE.exists(), "Phase 5-9 core-engine patch module exists", MODULE_FILE)
    record(DOC_FILE.exists(), "Phase 5-9 documentation exists", DOC_FILE)

    try:
        py_compile.compile(str(DASHBOARD_FILE), doraise=True)
        record(True, "Dashboard syntax remains valid", "syntax valid")
    except Exception as exc:
        record(False, "Dashboard syntax remains valid", exc)
        traceback.print_exc()

    try:
        py_compile.compile(str(MODULE_FILE), doraise=True)
        record(True, "Phase 5-9 module syntax valid", "syntax valid")
    except Exception as exc:
        record(False, "Phase 5-9 module syntax valid", exc)
        traceback.print_exc()

    try:
        module = import_module_from_path(MODULE_FILE, "phase5_core_engine_synthetic_default_patch")
        summary = module.build_phase5_9_summary()
        record(isinstance(summary, dict), "Phase 5-9 module imports and builds patch contract", type(summary).__name__)
    except Exception as exc:
        record(False, "Phase 5-9 module imports and builds patch contract", exc)
        traceback.print_exc()

    if not isinstance(summary, dict):
        summary = {}

    record(summary.get("ready_marker") == "PHASE5_9_CORE_ENGINE_SYNTHETIC_DEFAULT_PATCH_READY", "Core-engine patch has ready marker", summary.get("ready_marker"))
    record(summary.get("release_decision") == "PHASE5_9_CORE_ENGINE_SYNTHETIC_DEFAULT_PATCH_CREATED_SYNTHETIC_DEFAULT_PROTECTED", "Core-engine patch has release decision", summary.get("release_decision"))
    record(summary.get("source_mode") == "core_engine_synthetic_default_guard", "Core-engine patch uses guarded source mode", summary.get("source_mode"))
    record(summary.get("dashboard_change_required") is False, "Core-engine patch confirms no dashboard change", summary.get("dashboard_change_required"))
    record(summary.get("customer_workflow_change_required") is False, "Core-engine patch confirms no customer workflow change", summary.get("customer_workflow_change_required"))
    record(summary.get("core_engine_patch_contract_created") is True, "Core-engine patch contract created", summary.get("core_engine_patch_contract_created"))
    record(summary.get("actual_core_engine_files_replaced") is False, "No core engine files replaced yet", summary.get("actual_core_engine_files_replaced"))
    record(summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    record(summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    record(summary.get("unknown_mode_falls_back_to_synthetic") is True, "Unknown modes fall back to synthetic", summary.get("unknown_mode_falls_back_to_synthetic"))
    record(summary.get("engine_file_rows", 0) >= 5, "Engine file inventory has rows", summary.get("engine_file_rows"))
    record(summary.get("engine_mode_contract_rows", 0) >= 5, "Engine mode contract has rows", summary.get("engine_mode_contract_rows"))
    record(summary.get("engine_mode_contract_pass_count") == summary.get("engine_mode_contract_rows"), "Engine mode contract rows pass", f"{summary.get('engine_mode_contract_pass_count')}/{summary.get('engine_mode_contract_rows')}")
    record(summary.get("patch_readiness_rows", 0) >= 3, "Patch readiness table has rows", summary.get("patch_readiness_rows"))
    record(summary.get("first_patch_target") == "app/price_paths.py", "First patch target is price_paths.py", summary.get("first_patch_target"))
    record(summary.get("overall_status") == "PASS", "Phase 5-9 overall status is PASS", summary.get("overall_status"))

    for label, path in EXPECTED_OUTPUTS.items():
        record(path.exists(), f"Output written: {label}", path)

    contract_path = EXPECTED_OUTPUTS["engine_mode_contract_csv"]
    if contract_path.exists():
        try:
            contract_df = pd.read_csv(contract_path)
            record(len(contract_df) >= 5, "Engine mode contract CSV has expected content", f"rows={len(contract_df)}")
        except Exception as exc:
            record(False, "Engine mode contract CSV has expected content", exc)
    else:
        record(False, "Engine mode contract CSV has expected content", "missing")

    overall_pass = all(item["status"] == "PASS" for item in results)
    print()
    print("=" * 100)
    print(f"Overall Phase 5-9 checkpoint status: {'PASS' if overall_pass else 'FAIL'}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(_format_report(overall_pass), encoding="utf-8")
    CHECKPOINT_JSON.write_text(json.dumps({"overall_status": "PASS" if overall_pass else "FAIL", "results": results}, indent=2), encoding="utf-8")
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")
    return 0 if overall_pass else 1


def _format_report(overall_pass: bool) -> str:
    lines = [
        "Phase 5-9 core engine synthetic-default patch checkpoint report",
        "=" * 80,
        f"Overall status: {'PASS' if overall_pass else 'FAIL'}",
        "",
    ]
    for item in results:
        lines.append(f"{item['status']:<6} {item['label']} -- {item['detail']}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
