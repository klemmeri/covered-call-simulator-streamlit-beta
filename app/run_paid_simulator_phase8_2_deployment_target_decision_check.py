"""
run_paid_simulator_phase8_2_deployment_target_decision_check.py

Phase 8-2 deployment target decision check.
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
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase8_deployment_target_decision.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase8_2_deployment_target_decision.md"
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

TARGETS_CSV = OUTPUT_TABLE_DIR / "phase8_2_deployment_target_decision_targets.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase8_2_deployment_target_decision_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase8_2_deployment_target_decision.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase8_2_deployment_target_decision_report.txt"

CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase8_2_deployment_target_decision_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase8_2_deployment_target_decision_checkpoint.json"

READY_MARKER = "PHASE8_2_DEPLOYMENT_TARGET_DECISION_READY"
RELEASE_DECISION = "PHASE8_2_DEPLOYMENT_TARGET_DECISION_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "deployment_target_decision"


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
    print("Phase 8-2 deployment target decision check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    summary: dict[str, Any] = {}

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(MODULE_FILE.exists(), "Phase 8-2 deployment target module exists", MODULE_FILE)
    rec.add(DOC_FILE.exists(), "Phase 8-2 documentation exists", DOC_FILE)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    ok, detail = _compile_file(MODULE_FILE)
    rec.add(ok, "Phase 8-2 module syntax valid", detail)

    try:
        module = _import_module(MODULE_FILE, "phase8_deployment_target_decision")
        summary = module.build_phase8_2_summary()
        rec.add(isinstance(summary, dict), "Phase 8-2 module imports and writes outputs", type(summary).__name__)
    except Exception as exc:
        rec.add(False, "Phase 8-2 module imports and writes outputs", exc)
        traceback.print_exc()

    rec.add(summary.get("ready_marker") == READY_MARKER, "Deployment target decision has ready marker", summary.get("ready_marker"))
    rec.add(summary.get("release_decision") == RELEASE_DECISION, "Deployment target decision has release decision", summary.get("release_decision"))
    rec.add(summary.get("source_mode") == SOURCE_MODE, "Deployment target decision uses expected source mode", summary.get("source_mode"))
    rec.add(summary.get("dashboard_change_required") is False, "No dashboard change required", summary.get("dashboard_change_required"))
    rec.add(summary.get("engine_change_required") is False, "No engine change required", summary.get("engine_change_required"))
    rec.add(summary.get("deployment_target_decision_created") is True, "Deployment target decision created", summary.get("deployment_target_decision_created"))
    rec.add(summary.get("streamlit_mvp_path_supported") is True, "Streamlit MVP path supported", summary.get("streamlit_mvp_path_supported"))
    rec.add(summary.get("full_web_app_deferred") is True, "Full web app deferred", summary.get("full_web_app_deferred"))
    rec.add(summary.get("payments_access_control_not_yet_implemented") is True, "Payments/access control flagged as not yet implemented", summary.get("payments_access_control_not_yet_implemented"))
    rec.add(isinstance(summary.get("target_rows"), int) and summary.get("target_rows", 0) >= 5, "Deployment target table has rows", summary.get("target_rows"))
    rec.add(isinstance(summary.get("recommended_for_mvp_count"), int) and summary.get("recommended_for_mvp_count", 0) >= 1, "At least one MVP target recommended", summary.get("recommended_for_mvp_count"))
    rec.add(summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    rec.add(summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    rec.add(summary.get("historical_data_is_scenario_input_not_forecast") is True, "Historical data is scenario input, not forecast", summary.get("historical_data_is_scenario_input_not_forecast"))

    for label, path in [
        ("targets_csv", TARGETS_CSV),
        ("summary_csv", SUMMARY_CSV),
        ("json", JSON_REPORT),
        ("report", TEXT_REPORT),
    ]:
        rec.add(path.exists(), f"Output written: {label}", path)

    targets_ok = False
    targets_detail = "missing"
    if TARGETS_CSV.exists():
        try:
            df = pd.read_csv(TARGETS_CSV)
            text = df.astype(str).to_string(index=False)
            targets_ok = len(df) >= 5 and "Streamlit" in text and "Full custom web app" in text and "recommended_for_mvp" in df.columns
            targets_detail = f"rows={len(df)}"
        except Exception as exc:
            targets_detail = str(exc)
    rec.add(targets_ok, "Deployment target CSV has expected content", targets_detail)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall Phase 8-2 checkpoint status: {final_status}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join([f"{r['status']:<10} {r['label']:<76} {r['detail']}" for r in rec.rows] + ["", f"Overall Phase 8-2 checkpoint status: {final_status}"]) + "\n",
        encoding="utf-8",
    )
    CHECKPOINT_JSON.write_text(json.dumps({"overall_status": final_status, "checks": rec.rows}, indent=2), encoding="utf-8")
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if rec.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
