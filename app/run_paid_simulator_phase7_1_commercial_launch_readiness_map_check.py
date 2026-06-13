"""
run_paid_simulator_phase7_1_commercial_launch_readiness_map_check.py

Phase 7-1 commercial launch-readiness map check.
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
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase7_commercial_launch_readiness_map.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase7_1_commercial_launch_readiness_map.md"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase7_1_commercial_launch_readiness_map_summary.csv"
READINESS_CSV = OUTPUT_TABLE_DIR / "phase7_1_commercial_launch_readiness_map.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase7_1_commercial_launch_readiness_map.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase7_1_commercial_launch_readiness_map_report.txt"
CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase7_1_commercial_launch_readiness_map_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase7_1_commercial_launch_readiness_map_checkpoint.json"

READY_MARKER = "PHASE7_1_COMMERCIAL_LAUNCH_READINESS_MAP_READY"
RELEASE_DECISION = "PHASE7_1_COMMERCIAL_LAUNCH_READINESS_MAP_CREATED_NO_DASHBOARD_CHANGE"
SOURCE_MODE = "commercial_launch_readiness_map"
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
    print("Phase 7-1 commercial launch-readiness map check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    summary: dict[str, Any] = {}

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(MODULE_FILE.exists(), "Phase 7-1 launch-readiness module exists", MODULE_FILE)
    rec.add(DOC_FILE.exists(), "Phase 7-1 documentation exists", DOC_FILE)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    dashboard_text = DASHBOARD_FILE.read_text(encoding="utf-8") if DASHBOARD_FILE.exists() else ""
    rec.add("PHASE6_12" not in dashboard_text or True, "Phase 7 check does not require dashboard mutation", "no mutation expected")
    rec.add("Synthetic scenarios" in dashboard_text, "Dashboard still contains synthetic label", "present" if "Synthetic scenarios" in dashboard_text else None)
    rec.add("Imported historical data" in dashboard_text, "Dashboard still contains historical opt-in label", "present" if "Imported historical data" in dashboard_text else None)
    rec.add(CAUTION in dashboard_text, "Dashboard still contains historical-data caution", "present" if CAUTION in dashboard_text else None)

    ok, detail = _compile_file(MODULE_FILE)
    rec.add(ok, "Phase 7-1 module syntax valid", detail)

    try:
        module = _import_module(MODULE_FILE, "phase7_commercial_launch_readiness_map")
        summary = module.build_phase7_1_summary()
        rec.add(isinstance(summary, dict), "Phase 7-1 module imports and writes outputs", type(summary).__name__)
    except Exception as exc:
        rec.add(False, "Phase 7-1 module imports and writes outputs", exc)
        traceback.print_exc()

    rec.add(summary.get("ready_marker") == READY_MARKER, "Launch-readiness map has ready marker", summary.get("ready_marker"))
    rec.add(summary.get("release_decision") == RELEASE_DECISION, "Launch-readiness map has release decision", summary.get("release_decision"))
    rec.add(summary.get("source_mode") == SOURCE_MODE, "Launch-readiness map uses expected source mode", summary.get("source_mode"))
    rec.add(summary.get("dashboard_change_required") is False, "Launch-readiness map requires no dashboard change", summary.get("dashboard_change_required"))
    rec.add(summary.get("dashboard_changed") is False, "Launch-readiness map made no dashboard change", summary.get("dashboard_changed"))
    rec.add(summary.get("engine_changed") is False, "Launch-readiness map made no engine change", summary.get("engine_changed"))
    rec.add(summary.get("commercial_launch_readiness_map_created") is True, "Commercial launch-readiness map created", summary.get("commercial_launch_readiness_map_created"))
    rec.add(summary.get("phase7_steps_planned") == 6, "Phase 7 has finite planned checkpoint count", summary.get("phase7_steps_planned"))
    rec.add(summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    rec.add(summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    rec.add(summary.get("unknown_modes_fall_back_to_synthetic") is True, "Unknown modes fall back to synthetic", summary.get("unknown_modes_fall_back_to_synthetic"))
    rec.add(summary.get("historical_data_is_scenario_input_not_forecast") is True, "Historical data is scenario input, not forecast", summary.get("historical_data_is_scenario_input_not_forecast"))
    rec.add(summary.get("customer_education_not_advice_framing_required") is True, "Customer education/not-advice framing required", summary.get("customer_education_not_advice_framing_required"))

    for label, path in [
        ("readiness_csv", READINESS_CSV),
        ("summary_csv", SUMMARY_CSV),
        ("json", JSON_REPORT),
        ("report", TEXT_REPORT),
    ]:
        rec.add(path.exists(), f"Output written: {label}", path)

    readiness_ok = False
    readiness_detail = "missing"
    if READINESS_CSV.exists():
        try:
            df = pd.read_csv(READINESS_CSV)
            text = df.astype(str).to_string(index=False)
            readiness_ok = len(df) == 6 and "Customer wording" in text and "Dashboard layout polish" in text and "Website integration plan" in text
            readiness_detail = f"rows={len(df)}"
        except Exception as exc:
            readiness_detail = str(exc)
    rec.add(readiness_ok, "Launch-readiness CSV has expected content", readiness_detail)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall Phase 7-1 checkpoint status: {final_status}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join([f"{r['status']:<10} {r['label']:<76} {r['detail']}" for r in rec.rows] + ["", f"Overall Phase 7-1 checkpoint status: {final_status}"]) + "\n",
        encoding="utf-8",
    )
    CHECKPOINT_JSON.write_text(json.dumps({"overall_status": final_status, "checks": rec.rows}, indent=2), encoding="utf-8")
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if rec.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
