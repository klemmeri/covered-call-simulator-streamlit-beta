"""
run_paid_simulator_phase5_3_controlled_engine_hook_check.py

Checkpoint script for Phase 5-3: Controlled historical path engine hook.
"""

from __future__ import annotations

import importlib.util
import json
import py_compile
import traceback
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
PHASE5_2_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase5_imported_historical_path_engine_adapter.py"
PHASE5_3_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase5_controlled_historical_path_engine_hook.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase5_3_controlled_historical_path_engine_hook.md"

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
CHECK_REPORT = REPORT_DIR / "phase5_3_controlled_historical_path_engine_hook_checkpoint_report.txt"
CHECK_JSON = REPORT_DIR / "phase5_3_controlled_historical_path_engine_hook_checkpoint.json"

EXPECTED_OUTPUTS = {
    "hook_contract_csv": TABLE_DIR / "phase5_3_historical_path_engine_hook_contract.csv",
    "hook_preview_csv": TABLE_DIR / "phase5_3_historical_path_engine_hook_preview.csv",
    "summary_csv": TABLE_DIR / "phase5_3_historical_path_engine_hook_summary.csv",
    "json": REPORT_DIR / "phase5_3_historical_path_engine_hook.json",
    "report": REPORT_DIR / "phase5_3_historical_path_engine_hook_report.txt",
}


results = []


def record(status: bool, label: str, detail: object = "") -> None:
    results.append({"status": "PASS" if status else "FAIL", "label": label, "detail": str(detail)})
    print(f"{'PASS' if status else 'FAIL':<10} {label:<72} {detail}")


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def safe_csv_rows(path: Path) -> int | None:
    try:
        if not path.exists():
            return None
        return len(pd.read_csv(path))
    except Exception:
        return None


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 100)
    print("Phase 5-3 controlled historical path engine hook check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    record(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    record(PHASE5_2_FILE.exists(), "Prior Phase 5-2 adapter module exists", PHASE5_2_FILE)
    record(PHASE5_3_FILE.exists(), "Phase 5-3 controlled engine hook module exists", PHASE5_3_FILE)
    record(DOC_FILE.exists(), "Phase 5-3 documentation exists", DOC_FILE)

    try:
        py_compile.compile(str(DASHBOARD_FILE), doraise=True)
        record(True, "Dashboard syntax remains valid", "syntax valid")
    except Exception as exc:
        record(False, "Dashboard syntax remains valid", exc)

    try:
        py_compile.compile(str(PHASE5_3_FILE), doraise=True)
        record(True, "Phase 5-3 module syntax valid", "syntax valid")
    except Exception as exc:
        record(False, "Phase 5-3 module syntax valid", exc)

    summary = None
    try:
        module = import_module(PHASE5_3_FILE, "phase5_controlled_historical_path_engine_hook")
        summary = module.build_phase5_3_summary()
        record(isinstance(summary, dict), "Phase 5-3 module imports and builds hook", type(summary).__name__)
    except Exception as exc:
        record(False, "Phase 5-3 module imports and builds hook", exc)
        traceback.print_exc()

    if not isinstance(summary, dict):
        summary = {}

    record(summary.get("ready_marker") == "PHASE5_3_CONTROLLED_HISTORICAL_PATH_ENGINE_HOOK_READY", "Engine hook has ready marker", summary.get("ready_marker"))
    record(summary.get("release_decision") == "PHASE5_3_ENGINE_HOOK_CONTRACT_CREATED_NO_DASHBOARD_CHANGE", "Engine hook has release decision", summary.get("release_decision"))
    record(summary.get("dashboard_change_required") is False, "Engine hook confirms no dashboard change", summary.get("dashboard_change_required"))
    record(summary.get("source_mode") == "controlled_historical_path_hook", "Engine hook uses controlled hook mode", summary.get("source_mode"))
    record(summary.get("requested_mode") == "historical_import", "Engine hook requested historical import", summary.get("requested_mode"))
    record(summary.get("selected_mode") in {"historical_import", "synthetic_paths"}, "Engine hook selected valid mode", summary.get("selected_mode"))
    record(summary.get("engine_hook_contract_created") is True, "Engine hook contract created", summary.get("engine_hook_contract_created"))
    record(summary.get("engine_patch_applied") is False, "No engine patch applied yet", summary.get("engine_patch_applied"))
    record((summary.get("hook_contract_rows") or 0) >= 5, "Hook contract has rows", summary.get("hook_contract_rows"))
    record((summary.get("required_column_count") or 0) >= 5, "Hook contract lists required engine columns", summary.get("required_column_count"))
    record((summary.get("historical_path_rows") or 0) >= 1, "Historical engine-ready path has rows", summary.get("historical_path_rows"))

    for label, path in EXPECTED_OUTPUTS.items():
        record(path.exists(), f"Output written: {label}", path)

    record((safe_csv_rows(EXPECTED_OUTPUTS["hook_contract_csv"]) or 0) >= 5, "Hook contract CSV has expected content", f"rows={safe_csv_rows(EXPECTED_OUTPUTS['hook_contract_csv'])}")

    overall_pass = all(item["status"] == "PASS" for item in results)
    final_status = "PASS" if overall_pass else "FAIL"

    print()
    print("=" * 100)
    print(f"Overall Phase 5-3 checkpoint status: {final_status}")
    print("=" * 100)

    CHECK_REPORT.write_text("\n".join([f"{item['status']:<10} {item['label']:<72} {item['detail']}" for item in results] + ["", f"Overall Phase 5-3 checkpoint status: {final_status}"]), encoding="utf-8")
    CHECK_JSON.write_text(json.dumps({"overall_status": final_status, "results": results}, indent=2), encoding="utf-8")

    print(f"Saved checkpoint report: {CHECK_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECK_JSON}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
