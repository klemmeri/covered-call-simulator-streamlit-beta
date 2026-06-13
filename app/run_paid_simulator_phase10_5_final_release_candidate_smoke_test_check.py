"""
run_paid_simulator_phase10_5_final_release_candidate_smoke_test_check.py

Phase 10-5 final release candidate smoke test check.
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
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase10_final_release_candidate_smoke_test.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase10_5_final_release_candidate_smoke_test.md"
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

SMOKE_CSV = OUTPUT_TABLE_DIR / "phase10_5_final_release_candidate_smoke_test.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase10_5_final_release_candidate_smoke_test_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase10_5_final_release_candidate_smoke_test.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase10_5_final_release_candidate_smoke_test_report.txt"

CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase10_5_final_release_candidate_smoke_test_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase10_5_final_release_candidate_smoke_test_checkpoint.json"

READY_MARKER = "PHASE10_5_FINAL_RELEASE_CANDIDATE_SMOKE_TEST_READY"
RELEASE_DECISION = "PHASE10_5_FINAL_RELEASE_CANDIDATE_SMOKE_TEST_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "final_release_candidate_smoke_test"
VERSION = "v1.0.0-rc1"


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
    print("Phase 10-5 final release candidate smoke test check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    summary: dict[str, Any] = {}

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(MODULE_FILE.exists(), "Phase 10-5 smoke-test module exists", MODULE_FILE)
    rec.add(DOC_FILE.exists(), "Phase 10-5 documentation exists", DOC_FILE)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    ok, detail = _compile_file(MODULE_FILE)
    rec.add(ok, "Phase 10-5 module syntax valid", detail)

    try:
        module = _import_module(MODULE_FILE, "phase10_final_release_candidate_smoke_test")
        summary = module.build_phase10_5_summary()
        rec.add(isinstance(summary, dict), "Phase 10-5 module imports and writes outputs", type(summary).__name__)
    except Exception as exc:
        rec.add(False, "Phase 10-5 module imports and writes outputs", exc)
        traceback.print_exc()

    rec.add(summary.get("ready_marker") == READY_MARKER, "Final RC smoke test has ready marker", summary.get("ready_marker"))
    rec.add(summary.get("release_decision") == RELEASE_DECISION, "Final RC smoke test has release decision", summary.get("release_decision"))
    rec.add(summary.get("source_mode") == SOURCE_MODE, "Final RC smoke test uses expected source mode", summary.get("source_mode"))
    rec.add(summary.get("version") == VERSION, "Release candidate version is set", summary.get("version"))
    rec.add(summary.get("dashboard_change_required") is False, "No dashboard change required", summary.get("dashboard_change_required"))
    rec.add(summary.get("engine_change_required") is False, "No engine change required", summary.get("engine_change_required"))
    rec.add(summary.get("final_release_candidate_smoke_test_created") is True, "Final RC smoke test created", summary.get("final_release_candidate_smoke_test_created"))
    rec.add(summary.get("all_required_smoke_items_present") is True, "All required smoke items are present", summary.get("all_required_smoke_items_present"))
    rec.add(summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    rec.add(summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    rec.add(summary.get("historical_data_is_scenario_input_not_forecast") is True, "Historical data is scenario input, not forecast", summary.get("historical_data_is_scenario_input_not_forecast"))
    rec.add(summary.get("regime_detection_probabilistic_not_oracle") is True, "Regime detection is probabilistic guidance, not oracle", summary.get("regime_detection_probabilistic_not_oracle"))
    rec.add(summary.get("release_manifest_defined") is True, "Release manifest defined", summary.get("release_manifest_defined"))
    rec.add(summary.get("version_backup_policy_defined") is True, "Version and backup policy defined", summary.get("version_backup_policy_defined"))
    rec.add(summary.get("maintenance_issue_log_defined") is True, "Maintenance issue-log defined", summary.get("maintenance_issue_log_defined"))
    rec.add(summary.get("ready_for_phase10_completion_handoff") is True, "Ready for Phase 10 completion handoff", summary.get("ready_for_phase10_completion_handoff"))
    rec.add(isinstance(summary.get("smoke_rows"), int) and summary.get("smoke_rows", 0) >= 10, "Smoke-test table has rows", summary.get("smoke_rows"))

    for label, path in [
        ("smoke_csv", SMOKE_CSV),
        ("summary_csv", SUMMARY_CSV),
        ("json", JSON_REPORT),
        ("report", TEXT_REPORT),
    ]:
        rec.add(path.exists(), f"Output written: {label}", path)

    smoke_ok = False
    smoke_detail = "missing"
    if SMOKE_CSV.exists():
        try:
            df = pd.read_csv(SMOKE_CSV)
            smoke_ok = len(df) >= 10 and bool(df.loc[df["required_for_rc1"], "present"].all())
            smoke_detail = f"rows={len(df)}"
        except Exception as exc:
            smoke_detail = str(exc)
    rec.add(smoke_ok, "Final RC smoke-test CSV has expected content", smoke_detail)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall Phase 10-5 checkpoint status: {final_status}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join(
            [f"{row['status']:<10} {row['label']:<78} {row['detail']}" for row in rec.rows]
            + ["", f"Overall Phase 10-5 checkpoint status: {final_status}"]
        )
        + "\n",
        encoding="utf-8",
    )
    CHECKPOINT_JSON.write_text(json.dumps({"overall_status": final_status, "checks": rec.rows}, indent=2), encoding="utf-8")
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if rec.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
