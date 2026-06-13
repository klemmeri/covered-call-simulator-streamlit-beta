"""
run_paid_simulator_phase6_6_dashboard_historical_input_panel_patch_check.py
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
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase6_dashboard_historical_input_panel_patch.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase6_6_dashboard_historical_input_panel_patch.md"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase6_6_dashboard_historical_input_panel_patch_summary.csv"
CONTRACT_CSV = OUTPUT_TABLE_DIR / "phase6_6_dashboard_historical_input_panel_patch_contract.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase6_6_dashboard_historical_input_panel_patch.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase6_6_dashboard_historical_input_panel_patch_report.txt"
CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase6_6_dashboard_historical_input_panel_patch_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase6_6_dashboard_historical_input_panel_patch_checkpoint.json"

PATCH_START = "# === PHASE 6-6 DASHBOARD HISTORICAL INPUT PANEL PATCH START ==="
PATCH_END = "# === PHASE 6-6 DASHBOARD HISTORICAL INPUT PANEL PATCH END ==="
READY_MARKER = "PHASE6_6_DASHBOARD_HISTORICAL_INPUT_PANEL_PATCH_READY"
HELPER_NAME = "phase6_6_build_historical_input_panel_contract"
CAUTION = "Historical data is scenario input, not forecast"

PATCH_BLOCK = """
# === PHASE 6-6 DASHBOARD HISTORICAL INPUT PANEL PATCH START ===
PHASE6_6_DASHBOARD_HISTORICAL_INPUT_PANEL_PATCH_READY = "PHASE6_6_DASHBOARD_HISTORICAL_INPUT_PANEL_PATCH_READY"

def phase6_6_build_historical_input_panel_contract(selected_mode="Synthetic scenarios"):
    # Passive dashboard helper for the historical-data input panel.
    # Synthetic scenarios remain the default. Imported historical data remains
    # explicit opt-in only. Historical data is scenario input, not forecast.
    allowed_modes = ["Synthetic scenarios", "Imported historical data"]
    if selected_mode not in allowed_modes:
        selected_mode = "Synthetic scenarios"

    is_historical = selected_mode == "Imported historical data"

    return {
        "selected_mode": selected_mode,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "unknown_modes_fall_back_to_synthetic": True,
        "historical_mode_selected": is_historical,
        "historical_price_file_label": "Historical price file",
        "option_chain_file_label": "Option-chain file",
        "scenario_input_not_forecast": True,
        "customer_caution": "Historical data is scenario input, not forecast",
    }
# === PHASE 6-6 DASHBOARD HISTORICAL INPUT PANEL PATCH END ===
"""


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


def _apply_patch() -> str:
    text = DASHBOARD_FILE.read_text(encoding="utf-8")
    if PATCH_START in text and PATCH_END in text:
        return "patch block already present"
    DASHBOARD_FILE.write_text(text.rstrip() + "\n\n" + PATCH_BLOCK.strip() + "\n", encoding="utf-8")
    return "patch block appended"


def main() -> int:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 100)
    print("Phase 6-6 controlled dashboard historical input panel patch check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    summary: dict[str, Any] = {}

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(MODULE_FILE.exists(), "Phase 6-6 support module exists", MODULE_FILE)
    rec.add(DOC_FILE.exists(), "Phase 6-6 documentation exists", DOC_FILE)

    try:
        patch_detail = _apply_patch()
        rec.add(True, "Dashboard historical input-panel patch applied or already present", patch_detail)
    except Exception as exc:
        rec.add(False, "Dashboard historical input-panel patch applied or already present", exc)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    dashboard_text = DASHBOARD_FILE.read_text(encoding="utf-8") if DASHBOARD_FILE.exists() else ""
    rec.add(READY_MARKER in dashboard_text, "Dashboard contains Phase 6-6 ready marker", READY_MARKER if READY_MARKER in dashboard_text else None)
    rec.add(PATCH_START in dashboard_text and PATCH_END in dashboard_text, "Dashboard contains bounded Phase 6-6 patch block", "present" if PATCH_START in dashboard_text and PATCH_END in dashboard_text else None)
    rec.add(HELPER_NAME in dashboard_text, "Dashboard exposes Phase 6-6 helper function", "present" if HELPER_NAME in dashboard_text else None)
    rec.add(CAUTION in dashboard_text, "Dashboard contains historical-data caution wording", "present" if CAUTION in dashboard_text else None)

    ok, detail = _compile_file(MODULE_FILE)
    rec.add(ok, "Phase 6-6 support module syntax valid", detail)

    try:
        module = _import_module(MODULE_FILE, "phase6_dashboard_historical_input_panel_patch")
        summary = module.build_phase6_6_summary()
        rec.add(isinstance(summary, dict), "Phase 6-6 module imports and writes outputs", type(summary).__name__)
    except Exception as exc:
        rec.add(False, "Phase 6-6 module imports and writes outputs", exc)
        traceback.print_exc()

    rec.add(summary.get("ready_marker") == READY_MARKER, "Patch support has ready marker", summary.get("ready_marker"))
    rec.add(summary.get("release_decision") == "PHASE6_6_DASHBOARD_HISTORICAL_INPUT_PANEL_PATCH_CREATED_GUARDED_DASHBOARD_HELPER", "Patch support has release decision", summary.get("release_decision"))
    rec.add(summary.get("source_mode") == "dashboard_historical_input_panel_patch", "Patch support uses expected source mode", summary.get("source_mode"))
    rec.add(summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    rec.add(summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    rec.add(summary.get("unknown_modes_fall_back_to_synthetic") is True, "Unknown modes fall back to synthetic", summary.get("unknown_modes_fall_back_to_synthetic"))
    rec.add(summary.get("historical_data_is_scenario_input_not_forecast") is True, "Historical data is scenario input, not forecast", summary.get("historical_data_is_scenario_input_not_forecast"))
    rec.add(summary.get("dashboard_customer_workflow_changed") is False, "Customer workflow remains unchanged", summary.get("dashboard_customer_workflow_changed"))
    rec.add(isinstance(summary.get("contract_rows"), int) and summary.get("contract_rows", 0) >= 5, "Patch contract has rows", summary.get("contract_rows"))

    for label, path in [
        ("contract_csv", CONTRACT_CSV),
        ("summary_csv", SUMMARY_CSV),
        ("json", JSON_REPORT),
        ("report", TEXT_REPORT),
    ]:
        rec.add(path.exists(), f"Output written: {label}", path)

    contract_ok = False
    contract_detail = "missing"
    if CONTRACT_CSV.exists():
        try:
            df = pd.read_csv(CONTRACT_CSV)
            text = df.astype(str).to_string(index=False)
            contract_ok = len(df) >= 5 and "Imported historical data" in text and CAUTION in text
            contract_detail = f"rows={len(df)}"
        except Exception as exc:
            contract_detail = str(exc)
    rec.add(contract_ok, "Patch contract CSV has expected content", contract_detail)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall Phase 6-6 checkpoint status: {final_status}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join([f"{r['status']:<10} {r['label']:<72} {r['detail']}" for r in rec.rows] + ["", f"Overall Phase 6-6 checkpoint status: {final_status}"]) + "\n",
        encoding="utf-8",
    )
    CHECKPOINT_JSON.write_text(json.dumps({"overall_status": final_status, "checks": rec.rows}, indent=2), encoding="utf-8")
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if rec.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
