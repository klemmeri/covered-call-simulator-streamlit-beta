"""
run_paid_simulator_phase6_7_dashboard_historical_input_panel_visibility_check.py

Phase 6-7 dashboard historical input-panel visibility smoke test.
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
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase6_dashboard_historical_input_panel_visibility.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase6_7_dashboard_historical_input_panel_visibility.md"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase6_7_dashboard_historical_input_panel_visibility_summary.csv"
MARKERS_CSV = OUTPUT_TABLE_DIR / "phase6_7_dashboard_historical_input_panel_visibility_markers.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase6_7_dashboard_historical_input_panel_visibility.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase6_7_dashboard_historical_input_panel_visibility_report.txt"

CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase6_7_dashboard_historical_input_panel_visibility_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase6_7_dashboard_historical_input_panel_visibility_checkpoint.json"

READY_MARKER = "PHASE6_7_DASHBOARD_HISTORICAL_INPUT_PANEL_VISIBILITY_READY"
RELEASE_DECISION = "PHASE6_7_DASHBOARD_HISTORICAL_INPUT_PANEL_VISIBILITY_CREATED_NO_DASHBOARD_CHANGE"
SOURCE_MODE = "dashboard_historical_input_panel_visibility_smoke"

PHASE6_6_READY_MARKER = "PHASE6_6_DASHBOARD_HISTORICAL_INPUT_PANEL_PATCH_READY"
PHASE6_6_HELPER = "phase6_6_build_historical_input_panel_contract"
CAUTION = "Historical data is scenario input, not forecast"


class Recorder:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(self, passed: bool, label: str, detail: Any = "") -> None:
        status = "PASS" if passed else "FAIL"
        detail_text = "" if detail is None else str(detail)
        self.rows.append({"status": status, "label": label, "detail": detail_text})
        print(f"{status:<10} {label:<72} {detail_text}")

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
    print("Phase 6-7 dashboard historical input-panel visibility smoke test check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    summary: dict[str, Any] = {}

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(MODULE_FILE.exists(), "Phase 6-7 visibility module exists", MODULE_FILE)
    rec.add(DOC_FILE.exists(), "Phase 6-7 documentation exists", DOC_FILE)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    text = DASHBOARD_FILE.read_text(encoding="utf-8") if DASHBOARD_FILE.exists() else ""
    rec.add(PHASE6_6_READY_MARKER in text, "Dashboard contains Phase 6-6 ready marker", "marker check" if PHASE6_6_READY_MARKER in text else None)
    rec.add(PHASE6_6_HELPER in text, "Dashboard exposes Phase 6-6 helper function", "helper check" if PHASE6_6_HELPER in text else None)
    rec.add(CAUTION in text, "Dashboard contains historical-data caution wording", "caution check" if CAUTION in text else None)

    ok, detail = _compile_file(MODULE_FILE)
    rec.add(ok, "Phase 6-7 module syntax valid", detail)

    try:
        module = _import_module(MODULE_FILE, "phase6_dashboard_historical_input_panel_visibility")
        summary = module.build_phase6_7_summary()
        rec.add(isinstance(summary, dict), "Phase 6-7 module imports and writes outputs", type(summary).__name__)
    except Exception as exc:
        rec.add(False, "Phase 6-7 module imports and writes outputs", exc)
        traceback.print_exc()

    rec.add(summary.get("ready_marker") == READY_MARKER, "Visibility smoke has ready marker", summary.get("ready_marker"))
    rec.add(summary.get("release_decision") == RELEASE_DECISION, "Visibility smoke has release decision", summary.get("release_decision"))
    rec.add(summary.get("dashboard_change_required") is False, "Visibility smoke confirms no dashboard change", summary.get("dashboard_change_required"))
    rec.add(summary.get("source_mode") == SOURCE_MODE, "Visibility smoke uses expected source mode", summary.get("source_mode"))
    rec.add(summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    rec.add(summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    rec.add(summary.get("unknown_modes_fall_back_to_synthetic") is True, "Unknown modes fall back to synthetic", summary.get("unknown_modes_fall_back_to_synthetic"))
    rec.add(summary.get("historical_data_is_scenario_input_not_forecast") is True, "Historical data is scenario input, not forecast", summary.get("historical_data_is_scenario_input_not_forecast"))
    rec.add(summary.get("dashboard_historical_input_panel_markers_visible") is True, "Dashboard historical input-panel markers are visible", summary.get("dashboard_historical_input_panel_markers_visible"))
    rec.add(isinstance(summary.get("marker_rows"), int) and summary.get("marker_rows", 0) >= 7, "Marker table has rows", summary.get("marker_rows"))

    for label, path in [
        ("summary_csv", SUMMARY_CSV),
        ("markers_csv", MARKERS_CSV),
        ("json", JSON_REPORT),
        ("report", TEXT_REPORT),
    ]:
        rec.add(path.exists(), f"Output written: {label}", path)

    markers_ok = False
    marker_detail = "missing"
    if MARKERS_CSV.exists():
        try:
            df = pd.read_csv(MARKERS_CSV)
            markers_ok = len(df) >= 7 and bool(df["present"].all())
            marker_detail = f"rows={len(df)}"
        except Exception as exc:
            marker_detail = str(exc)
    rec.add(markers_ok, "Marker CSV has expected content", marker_detail)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall Phase 6-7 checkpoint status: {final_status}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join([f"{r['status']:<10} {r['label']:<72} {r['detail']}" for r in rec.rows] + ["", f"Overall Phase 6-7 checkpoint status: {final_status}"]) + "\n",
        encoding="utf-8",
    )
    CHECKPOINT_JSON.write_text(json.dumps({"overall_status": final_status, "checks": rec.rows}, indent=2), encoding="utf-8")
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if rec.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
