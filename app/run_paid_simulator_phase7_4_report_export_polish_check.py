"""
run_paid_simulator_phase7_4_report_export_polish_check.py

Phase 7-4 report export polish check.
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
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase7_report_export_polish.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase7_4_report_export_polish.md"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

CHECKLIST_CSV = OUTPUT_TABLE_DIR / "phase7_4_report_export_polish_checklist.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase7_4_report_export_polish_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase7_4_report_export_polish.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase7_4_report_export_polish_report.txt"

CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase7_4_report_export_polish_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase7_4_report_export_polish_checkpoint.json"

READY_MARKER = "PHASE7_4_REPORT_EXPORT_POLISH_READY"
RELEASE_DECISION = "PHASE7_4_REPORT_EXPORT_POLISH_CREATED_NO_DASHBOARD_CHANGE"
SOURCE_MODE = "report_export_polish"
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
    print("Phase 7-4 report export polish check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    summary: dict[str, Any] = {}

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(MODULE_FILE.exists(), "Phase 7-4 report-export module exists", MODULE_FILE)
    rec.add(DOC_FILE.exists(), "Phase 7-4 documentation exists", DOC_FILE)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    ok, detail = _compile_file(MODULE_FILE)
    rec.add(ok, "Phase 7-4 module syntax valid", detail)

    try:
        module = _import_module(MODULE_FILE, "phase7_report_export_polish")
        summary = module.build_phase7_4_summary()
        rec.add(isinstance(summary, dict), "Phase 7-4 module imports and writes outputs", type(summary).__name__)
    except Exception as exc:
        rec.add(False, "Phase 7-4 module imports and writes outputs", exc)
        traceback.print_exc()

    rec.add(summary.get("ready_marker") == READY_MARKER, "Report-export polish has ready marker", summary.get("ready_marker"))
    rec.add(summary.get("release_decision") == RELEASE_DECISION, "Report-export polish has release decision", summary.get("release_decision"))
    rec.add(summary.get("source_mode") == SOURCE_MODE, "Report-export polish uses expected source mode", summary.get("source_mode"))
    rec.add(summary.get("dashboard_change_required") is False, "Report-export polish confirms no dashboard change", summary.get("dashboard_change_required"))
    rec.add(summary.get("engine_change_required") is False, "Report-export polish confirms no engine change", summary.get("engine_change_required"))
    rec.add(summary.get("report_export_polish_created") is True, "Report-export polish created", summary.get("report_export_polish_created"))
    rec.add(isinstance(summary.get("checklist_rows"), int) and summary.get("checklist_rows", 0) >= 9, "Export checklist has rows", summary.get("checklist_rows"))
    rec.add(isinstance(summary.get("required_export_items"), int) and summary.get("required_export_items", 0) >= 7, "Required export items present", summary.get("required_export_items"))
    rec.add(summary.get("options_risk_wording_required") is True, "Options-risk wording required", summary.get("options_risk_wording_required"))
    rec.add(summary.get("financial_advice_disclaimer_required") is True, "Financial-advice disclaimer required", summary.get("financial_advice_disclaimer_required"))
    rec.add(summary.get("historical_data_is_scenario_input_not_forecast") is True, "Historical data is scenario input, not forecast", summary.get("historical_data_is_scenario_input_not_forecast"))
    rec.add(summary.get("regime_detection_probabilistic_not_oracle") is True, "Regime detection framed as probabilistic, not oracle", summary.get("regime_detection_probabilistic_not_oracle"))
    rec.add(summary.get("no_guaranteed_profit_wording") is True, "No guaranteed-profit wording required", summary.get("no_guaranteed_profit_wording"))
    rec.add(summary.get("patch_now") is False, "No report-export patch applied by this checkpoint", summary.get("patch_now"))

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
            checklist_ok = (
                len(df) >= 9
                and "Scenario summary report" in text
                and "Risk disclosure" in text
                and "Historical-data caution" in text
                and "Commercial safety" in text
            )
            checklist_detail = f"rows={len(df)}"
        except Exception as exc:
            checklist_detail = str(exc)
    rec.add(checklist_ok, "Export checklist CSV has expected content", checklist_detail)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall Phase 7-4 checkpoint status: {final_status}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join([f"{r['status']:<10} {r['label']:<76} {r['detail']}" for r in rec.rows] + ["", f"Overall Phase 7-4 checkpoint status: {final_status}"]) + "\n",
        encoding="utf-8",
    )
    CHECKPOINT_JSON.write_text(json.dumps({"overall_status": final_status, "checks": rec.rows}, indent=2), encoding="utf-8")
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if rec.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
