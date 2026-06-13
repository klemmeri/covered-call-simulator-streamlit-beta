"""
run_paid_simulator_phase9_5_trial_run_smoke_test_script_check.py

Phase 9-5 trial-run smoke-test script check.
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

MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase9_trial_run_smoke_test_script.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase9_5_trial_run_smoke_test_script.md"
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

SCRIPT_CSV = OUTPUT_TABLE_DIR / "phase9_5_trial_run_smoke_test_script.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase9_5_trial_run_smoke_test_script_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase9_5_trial_run_smoke_test_script.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase9_5_trial_run_smoke_test_script_report.txt"

CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase9_5_trial_run_smoke_test_script_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase9_5_trial_run_smoke_test_script_checkpoint.json"

READY_MARKER = "PHASE9_5_TRIAL_RUN_SMOKE_TEST_SCRIPT_READY"
RELEASE_DECISION = "PHASE9_5_TRIAL_RUN_SMOKE_TEST_SCRIPT_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "trial_run_smoke_test_script"
CAUTION = "Historical data is scenario input, not forecast"


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
    print("Phase 9-5 trial-run smoke-test script check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    summary: dict[str, Any] = {}

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(MODULE_FILE.exists(), "Phase 9-5 trial-run smoke-test module exists", MODULE_FILE)
    rec.add(DOC_FILE.exists(), "Phase 9-5 documentation exists", DOC_FILE)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    ok, detail = _compile_file(MODULE_FILE)
    rec.add(ok, "Phase 9-5 module syntax valid", detail)

    try:
        module = _import_module(MODULE_FILE, "phase9_trial_run_smoke_test_script")
        summary = module.build_phase9_5_summary()
        rec.add(isinstance(summary, dict), "Phase 9-5 module imports and writes outputs", type(summary).__name__)
    except Exception as exc:
        rec.add(False, "Phase 9-5 module imports and writes outputs", exc)
        traceback.print_exc()

    rec.add(summary.get("ready_marker") == READY_MARKER, "Trial-run smoke-test script has ready marker", summary.get("ready_marker"))
    rec.add(summary.get("release_decision") == RELEASE_DECISION, "Trial-run smoke-test script has release decision", summary.get("release_decision"))
    rec.add(summary.get("source_mode") == SOURCE_MODE, "Trial-run smoke-test script uses expected source mode", summary.get("source_mode"))
    rec.add(summary.get("dashboard_change_required") is False, "No dashboard change required", summary.get("dashboard_change_required"))
    rec.add(summary.get("engine_change_required") is False, "No engine change required", summary.get("engine_change_required"))
    rec.add(summary.get("trial_run_smoke_test_script_created") is True, "Trial-run smoke-test script created", summary.get("trial_run_smoke_test_script_created"))
    rec.add(summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    rec.add(summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    rec.add(summary.get("unknown_modes_fall_back_to_synthetic") is True, "Unknown modes fall back to synthetic", summary.get("unknown_modes_fall_back_to_synthetic"))
    rec.add(summary.get("historical_data_is_scenario_input_not_forecast") is True, "Historical data is scenario input, not forecast", summary.get("historical_data_is_scenario_input_not_forecast"))
    rec.add(summary.get("no_guaranteed_profit_wording_required") is True, "No guaranteed-profit wording required", summary.get("no_guaranteed_profit_wording_required"))
    rec.add(summary.get("risk_wording_required") is True, "Risk wording required", summary.get("risk_wording_required"))
    rec.add(summary.get("feedback_capture_required") is True, "Feedback capture required", summary.get("feedback_capture_required"))
    rec.add(isinstance(summary.get("script_rows"), int) and summary.get("script_rows", 0) >= 9, "Trial-run script has rows", summary.get("script_rows"))
    rec.add(isinstance(summary.get("required_trial_steps"), int) and summary.get("required_trial_steps", 0) >= 9, "Required trial steps present", summary.get("required_trial_steps"))

    for label, path in [
        ("script_csv", SCRIPT_CSV),
        ("summary_csv", SUMMARY_CSV),
        ("json", JSON_REPORT),
        ("report", TEXT_REPORT),
    ]:
        rec.add(path.exists(), f"Output written: {label}", path)

    script_ok = False
    script_detail = "missing"
    if SCRIPT_CSV.exists():
        try:
            df = pd.read_csv(SCRIPT_CSV)
            text = df.astype(str).to_string(index=False)
            script_ok = len(df) >= 9 and "synthetic" in text.lower() and "historical" in text.lower() and "feedback" in text.lower()
            script_detail = f"rows={len(df)}"
        except Exception as exc:
            script_detail = str(exc)
    rec.add(script_ok, "Trial-run script CSV has expected content", script_detail)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall Phase 9-5 checkpoint status: {final_status}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join(
            [f"{r['status']:<10} {r['label']:<76} {r['detail']}" for r in rec.rows]
            + ["", f"Overall Phase 9-5 checkpoint status: {final_status}"]
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
