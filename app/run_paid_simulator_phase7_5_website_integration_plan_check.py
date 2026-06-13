"""
run_paid_simulator_phase7_5_website_integration_plan_check.py

Phase 7-5 website integration plan check.
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
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase7_website_integration_plan.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase7_5_website_integration_plan.md"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

CHECKLIST_CSV = OUTPUT_TABLE_DIR / "phase7_5_website_integration_plan_checklist.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase7_5_website_integration_plan_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase7_5_website_integration_plan.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase7_5_website_integration_plan_report.txt"
CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase7_5_website_integration_plan_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase7_5_website_integration_plan_checkpoint.json"

READY_MARKER = "PHASE7_5_WEBSITE_INTEGRATION_PLAN_READY"
RELEASE_DECISION = "PHASE7_5_WEBSITE_INTEGRATION_PLAN_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "website_integration_plan"
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
    print("Phase 7-5 website integration plan check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    summary: dict[str, Any] = {}

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(MODULE_FILE.exists(), "Phase 7-5 website integration module exists", MODULE_FILE)
    rec.add(DOC_FILE.exists(), "Phase 7-5 documentation exists", DOC_FILE)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    dashboard_text = DASHBOARD_FILE.read_text(encoding="utf-8") if DASHBOARD_FILE.exists() else ""
    rec.add("Synthetic scenarios" in dashboard_text, "Dashboard retains synthetic scenario label", "present" if "Synthetic scenarios" in dashboard_text else None)
    rec.add("Imported historical data" in dashboard_text, "Dashboard retains historical opt-in label", "present" if "Imported historical data" in dashboard_text else None)
    rec.add(CAUTION in dashboard_text, "Dashboard retains scenario-not-forecast caution", "present" if CAUTION in dashboard_text else None)
    rec.add("phase6_9_resolve_dashboard_runner_mode" in dashboard_text, "Dashboard retains Phase 6-9 runner helper", "present" if "phase6_9_resolve_dashboard_runner_mode" in dashboard_text else None)

    ok, detail = _compile_file(MODULE_FILE)
    rec.add(ok, "Phase 7-5 module syntax valid", detail)

    try:
        module = _import_module(MODULE_FILE, "phase7_website_integration_plan")
        summary = module.build_phase7_5_summary()
        rec.add(isinstance(summary, dict), "Phase 7-5 module imports and writes outputs", type(summary).__name__)
    except Exception as exc:
        rec.add(False, "Phase 7-5 module imports and writes outputs", exc)
        traceback.print_exc()

    rec.add(summary.get("ready_marker") == READY_MARKER, "Website integration plan has ready marker", summary.get("ready_marker"))
    rec.add(summary.get("release_decision") == RELEASE_DECISION, "Website integration plan has release decision", summary.get("release_decision"))
    rec.add(summary.get("source_mode") == SOURCE_MODE, "Website integration plan uses expected source mode", summary.get("source_mode"))
    rec.add(summary.get("dashboard_change_required") is False, "Website integration plan confirms no dashboard change", summary.get("dashboard_change_required"))
    rec.add(summary.get("engine_change_required") is False, "Website integration plan confirms no engine change", summary.get("engine_change_required"))
    rec.add(summary.get("website_integration_plan_created") is True, "Website integration plan created", summary.get("website_integration_plan_created"))
    rec.add(isinstance(summary.get("checklist_rows"), int) and summary.get("checklist_rows", 0) >= 10, "Website checklist has rows", summary.get("checklist_rows"))
    rec.add(isinstance(summary.get("launch_required_items"), int) and summary.get("launch_required_items", 0) >= 8, "Launch-required items present", summary.get("launch_required_items"))
    rec.add(summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    rec.add(summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    rec.add(summary.get("historical_data_is_scenario_input_not_forecast") is True, "Historical data is scenario input, not forecast", summary.get("historical_data_is_scenario_input_not_forecast"))
    rec.add(summary.get("regime_detection_not_oracle_required") is True, "Regime detection not-oracle requirement present", summary.get("regime_detection_not_oracle_required"))
    rec.add(summary.get("no_financial_advice_language_required") is True, "No-financial-advice language requirement present", summary.get("no_financial_advice_language_required"))
    rec.add(summary.get("options_risk_language_required") is True, "Options-risk language requirement present", summary.get("options_risk_language_required"))

    for label, path in [
        ("checklist_csv", CHECKLIST_CSV),
        ("summary_csv", SUMMARY_CSV),
        ("json", JSON_REPORT),
        ("report", TEXT_REPORT),
    ]:
        rec.add(path.exists(), f"Output written: {label}", path)

    checklist_ok = False
    checklist_detail = "missing"
    if CHECKLIST_CSV.exists():
        try:
            df = pd.read_csv(CHECKLIST_CSV)
            text = df.astype(str).to_string(index=False)
            checklist_ok = len(df) >= 10 and "Landing page" in text and "Payments" in text and "Regime wording" in text
            checklist_detail = f"rows={len(df)}"
        except Exception as exc:
            checklist_detail = str(exc)
    rec.add(checklist_ok, "Website integration checklist CSV has expected content", checklist_detail)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall Phase 7-5 checkpoint status: {final_status}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join([f"{r['status']:<10} {r['label']:<76} {r['detail']}" for r in rec.rows] + ["", f"Overall Phase 7-5 checkpoint status: {final_status}"]) + "\n",
        encoding="utf-8",
    )
    CHECKPOINT_JSON.write_text(json.dumps({"overall_status": final_status, "checks": rec.rows}, indent=2), encoding="utf-8")
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if rec.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
