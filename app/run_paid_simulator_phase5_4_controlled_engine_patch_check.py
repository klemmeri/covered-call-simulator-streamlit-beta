"""
run_paid_simulator_phase5_4_controlled_engine_patch_check.py

Checkpoint runner for Phase 5-4 controlled historical path engine patch.
"""

from __future__ import annotations

import importlib.util
import json
import py_compile
import traceback
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
PHASE5_3_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase5_controlled_historical_path_engine_hook.py"
PHASE5_4_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase5_controlled_engine_patch_historical_paths.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase5_4_controlled_engine_patch_historical_paths.md"

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CHECK_REPORT = REPORT_DIR / "phase5_4_controlled_engine_patch_historical_paths_checkpoint_report.txt"
CHECK_JSON = REPORT_DIR / "phase5_4_controlled_engine_patch_historical_paths_checkpoint.json"

EXPECTED_OUTPUTS = {
    "patched_path_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase5_4_controlled_engine_patched_path.csv",
    "summary_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase5_4_controlled_engine_patch_summary.csv",
    "json": PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase5_4_controlled_engine_patch_historical_paths.json",
    "report": PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase5_4_controlled_engine_patch_historical_paths_report.txt",
}


class CheckRecorder:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, label: str, condition: bool, detail: Any = "") -> None:
        status = "PASS" if condition else "FAIL"
        self.rows.append({"status": status, "label": label, "detail": str(detail)})
        print(f"{status:<10} {label:<70} {detail}")

    @property
    def passed(self) -> bool:
        return all(row["status"] == "PASS" for row in self.rows)


def _compile_file(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "syntax valid"
    except Exception as exc:
        return False, str(exc)


def _import_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _csv_has_rows(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, "missing"
    try:
        df = pd.read_csv(path)
        return len(df) > 0, f"rows={len(df)}"
    except Exception as exc:
        return False, str(exc)


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 100)
    print("Phase 5-4 controlled historical path engine patch check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    recorder = CheckRecorder()

    recorder.check("Dashboard file exists", DASHBOARD_FILE.exists(), DASHBOARD_FILE)
    recorder.check("Prior Phase 5-3 engine hook module exists", PHASE5_3_FILE.exists(), PHASE5_3_FILE)
    recorder.check("Phase 5-4 controlled engine patch module exists", PHASE5_4_FILE.exists(), PHASE5_4_FILE)
    recorder.check("Phase 5-4 documentation exists", DOC_FILE.exists(), DOC_FILE)

    ok, detail = _compile_file(DASHBOARD_FILE) if DASHBOARD_FILE.exists() else (False, "missing")
    recorder.check("Dashboard syntax remains valid", ok, detail)

    ok, detail = _compile_file(PHASE5_4_FILE) if PHASE5_4_FILE.exists() else (False, "missing")
    recorder.check("Phase 5-4 module syntax valid", ok, detail)

    summary: dict[str, Any] | None = None
    try:
        module = _import_module(PHASE5_4_FILE, "phase5_controlled_engine_patch_historical_paths")
        summary = module.build_phase5_4_summary()
        recorder.check("Phase 5-4 module imports and builds patch", isinstance(summary, dict), type(summary).__name__)
    except Exception as exc:
        recorder.check("Phase 5-4 module imports and builds patch", False, exc)
        traceback.print_exc()

    if not isinstance(summary, dict):
        summary = {}

    recorder.check(
        "Controlled engine patch has ready marker",
        summary.get("ready_marker") == "PHASE5_4_CONTROLLED_ENGINE_PATCH_HISTORICAL_PATHS_READY",
        summary.get("ready_marker"),
    )
    recorder.check(
        "Controlled engine patch has release decision",
        summary.get("release_decision") == "PHASE5_4_CONTROLLED_ENGINE_PATCH_CREATED_OPT_IN_NO_DASHBOARD_CHANGE",
        summary.get("release_decision"),
    )
    recorder.check(
        "Controlled engine patch confirms no dashboard change",
        summary.get("dashboard_change_required") is False,
        summary.get("dashboard_change_required"),
    )
    recorder.check(
        "Core engine default remains unchanged",
        summary.get("core_engine_default_changed") is False,
        summary.get("core_engine_default_changed"),
    )
    recorder.check(
        "Synthetic path mode remains default",
        summary.get("synthetic_remains_default") is True,
        summary.get("synthetic_remains_default"),
    )
    recorder.check(
        "Historical mode requires explicit request",
        summary.get("historical_import_requires_explicit_request") is True,
        summary.get("historical_import_requires_explicit_request"),
    )
    recorder.check(
        "Controlled engine patch was created",
        summary.get("controlled_engine_patch_created") is True,
        summary.get("controlled_engine_patch_created"),
    )
    recorder.check(
        "Requested mode was historical import",
        summary.get("requested_mode") == "historical_import",
        summary.get("requested_mode"),
    )
    recorder.check(
        "Selected mode is valid",
        summary.get("selected_mode") in {"historical_import", "synthetic"},
        summary.get("selected_mode"),
    )
    recorder.check(
        "Patched path has rows",
        isinstance(summary.get("patched_path_rows"), int) and summary.get("patched_path_rows", 0) > 0,
        summary.get("patched_path_rows"),
    )
    recorder.check(
        "Patched path first price is positive",
        isinstance(summary.get("patched_path_first_price"), (int, float)) and summary.get("patched_path_first_price", 0) > 0,
        summary.get("patched_path_first_price"),
    )
    recorder.check(
        "Patched path last price is positive",
        isinstance(summary.get("patched_path_last_price"), (int, float)) and summary.get("patched_path_last_price", 0) > 0,
        summary.get("patched_path_last_price"),
    )

    for label, path in EXPECTED_OUTPUTS.items():
        recorder.check(f"Output written: {label}", path.exists(), path)

    ok, detail = _csv_has_rows(EXPECTED_OUTPUTS["patched_path_csv"])
    recorder.check("Patched path CSV has expected content", ok, detail)

    overall = "PASS" if recorder.passed else "FAIL"
    print()
    print("=" * 100)
    print(f"Overall Phase 5-4 checkpoint status: {overall}")
    print("=" * 100)

    CHECK_REPORT.write_text(
        "Phase 5-4 controlled historical path engine patch checkpoint\n"
        + "=" * 72
        + "\n\n"
        + "\n".join(f"{row['status']:<10} {row['label']:<70} {row['detail']}" for row in recorder.rows)
        + f"\n\nOverall Phase 5-4 checkpoint status: {overall}\n",
        encoding="utf-8",
    )
    CHECK_JSON.write_text(json.dumps({"overall_status": overall, "checks": recorder.rows}, indent=2), encoding="utf-8")
    print(f"Saved checkpoint report: {CHECK_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECK_JSON}")

    return 0 if recorder.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
