"""
run_paid_simulator_phase9_1_beta_testing_customer_trial_workflow_map_check.py

Phase 9-1 beta testing and customer-trial workflow map check.
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

MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase9_beta_testing_customer_trial_workflow_map.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase9_1_beta_testing_customer_trial_workflow_map.md"
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

WORKFLOW_CSV = OUTPUT_TABLE_DIR / "phase9_1_beta_testing_customer_trial_workflow_map.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase9_1_beta_testing_customer_trial_workflow_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase9_1_beta_testing_customer_trial_workflow_map.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase9_1_beta_testing_customer_trial_workflow_map_report.txt"

CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase9_1_beta_testing_customer_trial_workflow_map_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase9_1_beta_testing_customer_trial_workflow_map_checkpoint.json"

READY_MARKER = "PHASE9_1_BETA_TESTING_CUSTOMER_TRIAL_WORKFLOW_MAP_READY"
RELEASE_DECISION = "PHASE9_1_BETA_TESTING_CUSTOMER_TRIAL_WORKFLOW_MAP_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "beta_testing_customer_trial_workflow_map"


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
    print("Phase 9-1 beta testing and customer-trial workflow map check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    summary: dict[str, Any] = {}

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(MODULE_FILE.exists(), "Phase 9-1 beta workflow module exists", MODULE_FILE)
    rec.add(DOC_FILE.exists(), "Phase 9-1 documentation exists", DOC_FILE)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    ok, detail = _compile_file(MODULE_FILE)
    rec.add(ok, "Phase 9-1 module syntax valid", detail)

    try:
        module = _import_module(MODULE_FILE, "phase9_beta_testing_customer_trial_workflow_map")
        summary = module.build_phase9_1_summary()
        rec.add(isinstance(summary, dict), "Phase 9-1 module imports and writes outputs", type(summary).__name__)
    except Exception as exc:
        rec.add(False, "Phase 9-1 module imports and writes outputs", exc)
        traceback.print_exc()

    rec.add(summary.get("ready_marker") == READY_MARKER, "Beta workflow map has ready marker", summary.get("ready_marker"))
    rec.add(summary.get("release_decision") == RELEASE_DECISION, "Beta workflow map has release decision", summary.get("release_decision"))
    rec.add(summary.get("source_mode") == SOURCE_MODE, "Beta workflow map uses expected source mode", summary.get("source_mode"))
    rec.add(summary.get("dashboard_change_required") is False, "No dashboard change required", summary.get("dashboard_change_required"))
    rec.add(summary.get("engine_change_required") is False, "No engine change required", summary.get("engine_change_required"))
    rec.add(summary.get("beta_workflow_map_created") is True, "Beta workflow map created", summary.get("beta_workflow_map_created"))
    rec.add(summary.get("phase9_plan_defined") is True, "Phase 9 plan defined", summary.get("phase9_plan_defined"))
    rec.add(isinstance(summary.get("phase9_step_count"), int) and summary.get("phase9_step_count", 0) == 6, "Phase 9 has finite six-step plan", summary.get("phase9_step_count"))
    rec.add(summary.get("private_beta_first") is True, "Private beta first", summary.get("private_beta_first"))
    rec.add(summary.get("feedback_capture_required") is True, "Feedback capture required", summary.get("feedback_capture_required"))
    rec.add(summary.get("disclaimer_acceptance_required") is True, "Disclaimer acceptance required", summary.get("disclaimer_acceptance_required"))
    rec.add(summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    rec.add(summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    rec.add(summary.get("historical_data_is_scenario_input_not_forecast") is True, "Historical data is scenario input, not forecast", summary.get("historical_data_is_scenario_input_not_forecast"))
    rec.add(summary.get("regime_detection_probabilistic_not_oracle") is True, "Regime detection is probabilistic, not an oracle", summary.get("regime_detection_probabilistic_not_oracle"))
    rec.add(isinstance(summary.get("workflow_rows"), int) and summary.get("workflow_rows", 0) >= 7, "Beta workflow table has rows", summary.get("workflow_rows"))

    for label, path in [
        ("workflow_csv", WORKFLOW_CSV),
        ("summary_csv", SUMMARY_CSV),
        ("json", JSON_REPORT),
        ("report", TEXT_REPORT),
    ]:
        rec.add(path.exists(), f"Output written: {label}", path)

    workflow_ok = False
    workflow_detail = "missing"
    if WORKFLOW_CSV.exists():
        try:
            df = pd.read_csv(WORKFLOW_CSV)
            text = df.astype(str).to_string(index=False)
            workflow_ok = len(df) >= 7 and "Select beta testers" in text and "Collect structured feedback" in text and "Confirm disclaimer acceptance" in text
            workflow_detail = f"rows={len(df)}"
        except Exception as exc:
            workflow_detail = str(exc)
    rec.add(workflow_ok, "Beta workflow CSV has expected content", workflow_detail)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall Phase 9-1 checkpoint status: {final_status}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join(
            [f"{r['status']:<10} {r['label']:<78} {r['detail']}" for r in rec.rows]
            + ["", f"Overall Phase 9-1 checkpoint status: {final_status}"]
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
