"""
run_paid_simulator_phase9_6_completion_handoff_check.py

Phase 9-6 completion handoff check.
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

MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase9_completion_handoff.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase9_6_completion_handoff.md"
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase9_6_completion_handoff_summary.csv"
ARTIFACTS_CSV = OUTPUT_TABLE_DIR / "phase9_6_completion_handoff_artifacts.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase9_6_completion_handoff.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase9_6_completion_handoff_report.txt"
CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase9_6_completion_handoff_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase9_6_completion_handoff_checkpoint.json"

READY_MARKER = "PHASE9_6_COMPLETION_HANDOFF_READY"
RELEASE_DECISION = "PHASE9_COMPLETE_READY_FOR_PHASE10_FINAL_RELEASE_PACKAGE"
SOURCE_MODE = "phase9_completion_handoff"


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
    print("Phase 9-6 completion handoff check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    summary: dict[str, Any] = {}

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(MODULE_FILE.exists(), "Phase 9-6 completion module exists", MODULE_FILE)
    rec.add(DOC_FILE.exists(), "Phase 9-6 documentation exists", DOC_FILE)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    ok, detail = _compile_file(MODULE_FILE)
    rec.add(ok, "Phase 9-6 module syntax valid", detail)

    try:
        module = _import_module(MODULE_FILE, "phase9_completion_handoff")
        summary = module.build_phase9_6_summary()
        rec.add(isinstance(summary, dict), "Phase 9-6 module imports and writes outputs", type(summary).__name__)
    except Exception as exc:
        rec.add(False, "Phase 9-6 module imports and writes outputs", exc)
        traceback.print_exc()

    rec.add(summary.get("ready_marker") == READY_MARKER, "Completion handoff has ready marker", summary.get("ready_marker"))
    rec.add(summary.get("release_decision") == RELEASE_DECISION, "Completion handoff has release decision", summary.get("release_decision"))
    rec.add(summary.get("source_mode") == SOURCE_MODE, "Completion handoff uses expected source mode", summary.get("source_mode"))
    rec.add(summary.get("dashboard_change_required") is False, "No dashboard change required", summary.get("dashboard_change_required"))
    rec.add(summary.get("engine_change_required") is False, "No engine change required", summary.get("engine_change_required"))
    rec.add(summary.get("phase9_completion_handoff_created") is True, "Phase 9 completion handoff created", summary.get("phase9_completion_handoff_created"))
    rec.add(summary.get("all_required_phase9_artifacts_present") is True, "All required Phase 9 artifacts present", summary.get("all_required_phase9_artifacts_present"))
    rec.add(summary.get("beta_workflow_map_exists") is True, "Beta workflow map exists", summary.get("beta_workflow_map_exists"))
    rec.add(summary.get("beta_onboarding_checklist_exists") is True, "Beta onboarding checklist exists", summary.get("beta_onboarding_checklist_exists"))
    rec.add(summary.get("customer_feedback_template_exists") is True, "Customer feedback template exists", summary.get("customer_feedback_template_exists"))
    rec.add(summary.get("beta_safety_disclaimer_review_exists") is True, "Beta safety disclaimer review exists", summary.get("beta_safety_disclaimer_review_exists"))
    rec.add(summary.get("trial_run_smoke_test_script_exists") is True, "Trial-run smoke-test script exists", summary.get("trial_run_smoke_test_script_exists"))
    rec.add(summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    rec.add(summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    rec.add(summary.get("unknown_modes_fall_back_to_synthetic") is True, "Unknown modes fall back to synthetic", summary.get("unknown_modes_fall_back_to_synthetic"))
    rec.add(summary.get("historical_data_is_scenario_input_not_forecast") is True, "Historical data is scenario input, not forecast", summary.get("historical_data_is_scenario_input_not_forecast"))
    rec.add(summary.get("regime_detection_probabilistic_not_oracle") is True, "Regime detection is probabilistic, not an oracle", summary.get("regime_detection_probabilistic_not_oracle"))
    rec.add(summary.get("ready_for_phase10") is True, "Ready for Phase 10", summary.get("ready_for_phase10"))
    rec.add(isinstance(summary.get("phase9_artifact_rows"), int) and summary.get("phase9_artifact_rows", 0) >= 5, "Phase 9 artifact table has rows", summary.get("phase9_artifact_rows"))

    for label, path in [
        ("artifacts_csv", ARTIFACTS_CSV),
        ("summary_csv", SUMMARY_CSV),
        ("json", JSON_REPORT),
        ("report", TEXT_REPORT),
    ]:
        rec.add(path.exists(), f"Output written: {label}", path)

    artifacts_ok = False
    artifacts_detail = "missing"
    if ARTIFACTS_CSV.exists():
        try:
            df = pd.read_csv(ARTIFACTS_CSV)
            artifacts_ok = len(df) >= 5 and bool(df["artifact_complete"].all())
            artifacts_detail = f"rows={len(df)}"
        except Exception as exc:
            artifacts_detail = str(exc)
    rec.add(artifacts_ok, "Phase 9 artifact CSV has expected content", artifacts_detail)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall Phase 9-6 checkpoint status: {final_status}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join(
            [f"{r['status']:<10} {r['label']:<76} {r['detail']}" for r in rec.rows]
            + ["", f"Overall Phase 9-6 checkpoint status: {final_status}"]
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
