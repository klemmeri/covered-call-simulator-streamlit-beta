"""
run_paid_simulator_phase7_2_customer_wording_disclaimer_audit_check.py

Phase 7-2 customer wording and disclaimer audit check.
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
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase7_customer_wording_disclaimer_audit.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase7_2_customer_wording_disclaimer_audit.md"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

AUDIT_CSV = OUTPUT_TABLE_DIR / "phase7_2_customer_wording_disclaimer_audit.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase7_2_customer_wording_disclaimer_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase7_2_customer_wording_disclaimer_audit.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase7_2_customer_wording_disclaimer_audit_report.txt"
CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase7_2_customer_wording_disclaimer_audit_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase7_2_customer_wording_disclaimer_audit_checkpoint.json"

READY_MARKER = "PHASE7_2_CUSTOMER_WORDING_DISCLAIMER_AUDIT_READY"
RELEASE_DECISION = "PHASE7_2_CUSTOMER_WORDING_DISCLAIMER_AUDIT_CREATED_NO_DASHBOARD_CHANGE"
SOURCE_MODE = "customer_wording_disclaimer_audit"
REQUIRED_CAUTION = "Historical data is scenario input, not forecast"


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
    print("Phase 7-2 customer wording and disclaimer audit check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    summary: dict[str, Any] = {}

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(MODULE_FILE.exists(), "Phase 7-2 audit module exists", MODULE_FILE)
    rec.add(DOC_FILE.exists(), "Phase 7-2 documentation exists", DOC_FILE)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    ok, detail = _compile_file(MODULE_FILE)
    rec.add(ok, "Phase 7-2 module syntax valid", detail)

    try:
        module = _import_module(MODULE_FILE, "phase7_customer_wording_disclaimer_audit")
        summary = module.build_phase7_2_summary()
        rec.add(isinstance(summary, dict), "Phase 7-2 module imports and writes outputs", type(summary).__name__)
    except Exception as exc:
        rec.add(False, "Phase 7-2 module imports and writes outputs", exc)
        traceback.print_exc()

    rec.add(summary.get("ready_marker") == READY_MARKER, "Audit has ready marker", summary.get("ready_marker"))
    rec.add(summary.get("release_decision") == RELEASE_DECISION, "Audit has release decision", summary.get("release_decision"))
    rec.add(summary.get("dashboard_change_required") is False, "Audit confirms no dashboard change", summary.get("dashboard_change_required"))
    rec.add(summary.get("source_mode") == SOURCE_MODE, "Audit uses expected source mode", summary.get("source_mode"))
    rec.add(summary.get("customer_wording_audit_created") is True, "Customer wording audit created", summary.get("customer_wording_audit_created"))
    rec.add(summary.get("risk_disclaimer_required") is True, "Risk disclaimer is required", summary.get("risk_disclaimer_required"))
    rec.add(summary.get("financial_advice_disclaimer_required") is True, "Financial-advice disclaimer is required", summary.get("financial_advice_disclaimer_required"))
    rec.add(summary.get("historical_data_is_scenario_input_not_forecast") is True, "Historical data is scenario input, not forecast", summary.get("historical_data_is_scenario_input_not_forecast"))
    rec.add(summary.get("regime_detection_is_probabilistic_guidance") is True, "Regime detection is probabilistic guidance", summary.get("regime_detection_is_probabilistic_guidance"))
    rec.add(summary.get("regime_detection_not_oracle") is True, "Regime detection is not treated as oracle", summary.get("regime_detection_not_oracle"))
    rec.add(summary.get("performance_not_guaranteed") is True, "Performance is not guaranteed", summary.get("performance_not_guaranteed"))
    rec.add(summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    rec.add(summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    rec.add(summary.get("forbidden_performance_terms_found") == 0, "No forbidden performance terms found", summary.get("forbidden_terms_found_list"))
    rec.add(isinstance(summary.get("audit_rows"), int) and summary.get("audit_rows", 0) >= 6, "Audit table has rows", summary.get("audit_rows"))

    for label, path in [
        ("audit_csv", AUDIT_CSV),
        ("summary_csv", SUMMARY_CSV),
        ("json", JSON_REPORT),
        ("report", TEXT_REPORT),
    ]:
        rec.add(path.exists(), f"Output written: {label}", path)

    audit_ok = False
    audit_detail = "missing"
    if AUDIT_CSV.exists():
        try:
            df = pd.read_csv(AUDIT_CSV)
            text = df.astype(str).to_string(index=False)
            audit_ok = (
                len(df) >= 6
                and REQUIRED_CAUTION in text
                and "Options involve risk" in text
                and "not individualized financial advice" in text
                and "Regime labels are probabilistic" in text
            )
            audit_detail = f"rows={len(df)}"
        except Exception as exc:
            audit_detail = str(exc)
    rec.add(audit_ok, "Audit CSV has expected commercial wording", audit_detail)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall Phase 7-2 checkpoint status: {final_status}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join([f"{r['status']:<10} {r['label']:<76} {r['detail']}" for r in rec.rows] + ["", f"Overall Phase 7-2 checkpoint status: {final_status}"]) + "\n",
        encoding="utf-8",
    )
    CHECKPOINT_JSON.write_text(json.dumps({"overall_status": final_status, "checks": rec.rows}, indent=2), encoding="utf-8")
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if rec.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
