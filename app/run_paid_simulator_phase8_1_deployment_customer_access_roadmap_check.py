"""
run_paid_simulator_phase8_1_deployment_customer_access_roadmap_check.py

Phase 8-1 deployment and customer-access roadmap check.
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
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase8_deployment_customer_access_roadmap.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase8_1_deployment_customer_access_roadmap.md"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

ROADMAP_CSV = OUTPUT_TABLE_DIR / "phase8_1_deployment_customer_access_roadmap.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase8_1_deployment_customer_access_roadmap_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase8_1_deployment_customer_access_roadmap.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase8_1_deployment_customer_access_roadmap_report.txt"
CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase8_1_deployment_customer_access_roadmap_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase8_1_deployment_customer_access_roadmap_checkpoint.json"

READY_MARKER = "PHASE8_1_DEPLOYMENT_CUSTOMER_ACCESS_ROADMAP_READY"
RELEASE_DECISION = "PHASE8_1_DEPLOYMENT_CUSTOMER_ACCESS_ROADMAP_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "deployment_customer_access_roadmap"
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
    print("Phase 8-1 deployment and customer-access roadmap check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    summary: dict[str, Any] = {}

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(MODULE_FILE.exists(), "Phase 8-1 roadmap module exists", MODULE_FILE)
    rec.add(DOC_FILE.exists(), "Phase 8-1 documentation exists", DOC_FILE)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    ok, detail = _compile_file(MODULE_FILE)
    rec.add(ok, "Phase 8-1 module syntax valid", detail)

    try:
        module = _import_module(MODULE_FILE, "phase8_deployment_customer_access_roadmap")
        summary = module.build_phase8_1_summary()
        rec.add(isinstance(summary, dict), "Phase 8-1 module imports and writes outputs", type(summary).__name__)
    except Exception as exc:
        rec.add(False, "Phase 8-1 module imports and writes outputs", exc)
        traceback.print_exc()

    rec.add(summary.get("ready_marker") == READY_MARKER, "Roadmap has ready marker", summary.get("ready_marker"))
    rec.add(summary.get("release_decision") == RELEASE_DECISION, "Roadmap has release decision", summary.get("release_decision"))
    rec.add(summary.get("source_mode") == SOURCE_MODE, "Roadmap uses expected source mode", summary.get("source_mode"))
    rec.add(summary.get("dashboard_change_required") is False, "Roadmap confirms no dashboard change", summary.get("dashboard_change_required"))
    rec.add(summary.get("engine_change_required") is False, "Roadmap confirms no engine change", summary.get("engine_change_required"))
    rec.add(summary.get("roadmap_created") is True, "Deployment roadmap created", summary.get("roadmap_created"))
    rec.add(summary.get("phase8_finite_plan_created") is True, "Finite Phase 8 plan created", summary.get("phase8_finite_plan_created"))
    rec.add(summary.get("planned_phase8_checkpoints") == 6, "Phase 8 has six planned checkpoints", summary.get("planned_phase8_checkpoints"))
    rec.add(summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    rec.add(summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    rec.add(summary.get("historical_data_is_scenario_input_not_forecast") is True, "Historical data is scenario input, not forecast", summary.get("historical_data_is_scenario_input_not_forecast"))
    rec.add(summary.get("regime_detection_probabilistic_not_oracle") is True, "Regime detection remains probabilistic, not oracle", summary.get("regime_detection_probabilistic_not_oracle"))
    rec.add(summary.get("customer_access_planning_started") is True, "Customer-access planning started", summary.get("customer_access_planning_started"))
    rec.add(summary.get("deployment_planning_started") is True, "Deployment planning started", summary.get("deployment_planning_started"))

    for label, path in [
        ("roadmap_csv", ROADMAP_CSV),
        ("summary_csv", SUMMARY_CSV),
        ("json", JSON_REPORT),
        ("report", TEXT_REPORT),
    ]:
        rec.add(path.exists(), f"Output written: {label}", path)

    roadmap_ok = False
    roadmap_detail = "missing"
    if ROADMAP_CSV.exists():
        try:
            df = pd.read_csv(ROADMAP_CSV)
            text = df.astype(str).to_string(index=False)
            roadmap_ok = len(df) == 6 and "Phase 8-2" in text and "Deployment target decision" in text and "Deployment completion handoff" in text
            roadmap_detail = f"rows={len(df)}"
        except Exception as exc:
            roadmap_detail = str(exc)
    rec.add(roadmap_ok, "Roadmap CSV has expected content", roadmap_detail)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall Phase 8-1 checkpoint status: {final_status}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join([f"{r['status']:<10} {r['label']:<76} {r['detail']}" for r in rec.rows] + ["", f"Overall Phase 8-1 checkpoint status: {final_status}"]) + "\n",
        encoding="utf-8",
    )
    CHECKPOINT_JSON.write_text(json.dumps({"overall_status": final_status, "checks": rec.rows}, indent=2), encoding="utf-8")
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if rec.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
