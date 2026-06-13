"""
run_paid_simulator_phase9_4_beta_safety_disclaimer_review_check.py

Phase 9-4 beta safety and disclaimer review check.
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
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase9_beta_safety_disclaimer_review.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase9_4_beta_safety_disclaimer_review.md"
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

REVIEW_CSV = OUTPUT_TABLE_DIR / "phase9_4_beta_safety_disclaimer_review.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase9_4_beta_safety_disclaimer_review_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase9_4_beta_safety_disclaimer_review.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase9_4_beta_safety_disclaimer_review_report.txt"
CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase9_4_beta_safety_disclaimer_review_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase9_4_beta_safety_disclaimer_review_checkpoint.json"

READY_MARKER = "PHASE9_4_BETA_SAFETY_DISCLAIMER_REVIEW_READY"
RELEASE_DECISION = "PHASE9_4_BETA_SAFETY_DISCLAIMER_REVIEW_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "beta_safety_disclaimer_review"
CAUTION = "Historical data is scenario input, not forecast"
REGIME_CAUTION = "Regime detection is probabilistic guidance, not an oracle"


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
    print("Phase 9-4 beta safety and disclaimer review check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    summary: dict[str, Any] = {}

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(MODULE_FILE.exists(), "Phase 9-4 safety review module exists", MODULE_FILE)
    rec.add(DOC_FILE.exists(), "Phase 9-4 documentation exists", DOC_FILE)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    ok, detail = _compile_file(MODULE_FILE)
    rec.add(ok, "Phase 9-4 module syntax valid", detail)

    try:
        module = _import_module(MODULE_FILE, "phase9_beta_safety_disclaimer_review")
        summary = module.build_phase9_4_summary()
        rec.add(isinstance(summary, dict), "Phase 9-4 module imports and writes outputs", type(summary).__name__)
    except Exception as exc:
        rec.add(False, "Phase 9-4 module imports and writes outputs", exc)
        traceback.print_exc()

    rec.add(summary.get("ready_marker") == READY_MARKER, "Safety review has ready marker", summary.get("ready_marker"))
    rec.add(summary.get("release_decision") == RELEASE_DECISION, "Safety review has release decision", summary.get("release_decision"))
    rec.add(summary.get("source_mode") == SOURCE_MODE, "Safety review uses expected source mode", summary.get("source_mode"))
    rec.add(summary.get("dashboard_change_required") is False, "No dashboard change required", summary.get("dashboard_change_required"))
    rec.add(summary.get("engine_change_required") is False, "No engine change required", summary.get("engine_change_required"))
    rec.add(summary.get("beta_safety_disclaimer_review_created") is True, "Beta safety review created", summary.get("beta_safety_disclaimer_review_created"))
    rec.add(summary.get("options_risk_wording_required") is True, "Options risk wording required", summary.get("options_risk_wording_required"))
    rec.add(summary.get("no_financial_advice_wording_required") is True, "No-financial-advice wording required", summary.get("no_financial_advice_wording_required"))
    rec.add(summary.get("historical_data_is_scenario_input_not_forecast") is True, "Historical data is scenario input, not forecast", summary.get("historical_data_is_scenario_input_not_forecast"))
    rec.add(summary.get("regime_detection_probabilistic_not_oracle") is True, "Regime detection is probabilistic, not oracle", summary.get("regime_detection_probabilistic_not_oracle"))
    rec.add(summary.get("no_guaranteed_profit_wording") is True, "No guaranteed-profit wording required", summary.get("no_guaranteed_profit_wording"))
    rec.add(summary.get("customer_responsibility_wording_required") is True, "Customer responsibility wording required", summary.get("customer_responsibility_wording_required"))
    rec.add(summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    rec.add(summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    rec.add(isinstance(summary.get("review_rows"), int) and summary.get("review_rows", 0) >= 8, "Safety review table has rows", summary.get("review_rows"))
    rec.add(isinstance(summary.get("required_review_items"), int) and summary.get("required_review_items", 0) >= 8, "Required safety review items present", summary.get("required_review_items"))

    for label, path in [
        ("review_csv", REVIEW_CSV),
        ("summary_csv", SUMMARY_CSV),
        ("json", JSON_REPORT),
        ("report", TEXT_REPORT),
    ]:
        rec.add(path.exists(), f"Output written: {label}", path)

    review_ok = False
    review_detail = "missing"
    if REVIEW_CSV.exists():
        try:
            df = pd.read_csv(REVIEW_CSV)
            text = df.astype(str).to_string(index=False)
            review_ok = len(df) >= 8 and CAUTION in text and REGIME_CAUTION in text and "No financial advice" in text
            review_detail = f"rows={len(df)}"
        except Exception as exc:
            review_detail = str(exc)
    rec.add(review_ok, "Safety review CSV has expected content", review_detail)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall Phase 9-4 checkpoint status: {final_status}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join(
            [f"{r['status']:<10} {r['label']:<76} {r['detail']}" for r in rec.rows]
            + ["", f"Overall Phase 9-4 checkpoint status: {final_status}"]
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
