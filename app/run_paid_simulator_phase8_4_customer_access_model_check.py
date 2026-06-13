"""
run_paid_simulator_phase8_4_customer_access_model_check.py

Phase 8-4 customer access model check.
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
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase8_customer_access_model.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase8_4_customer_access_model.md"
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

ACCESS_MODEL_CSV = OUTPUT_TABLE_DIR / "phase8_4_customer_access_model_options.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase8_4_customer_access_model_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase8_4_customer_access_model.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase8_4_customer_access_model_report.txt"

CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase8_4_customer_access_model_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase8_4_customer_access_model_checkpoint.json"

READY_MARKER = "PHASE8_4_CUSTOMER_ACCESS_MODEL_READY"
RELEASE_DECISION = "PHASE8_4_CUSTOMER_ACCESS_MODEL_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "customer_access_model"


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
    print("Phase 8-4 customer access model check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    summary: dict[str, Any] = {}

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(MODULE_FILE.exists(), "Phase 8-4 customer access module exists", MODULE_FILE)
    rec.add(DOC_FILE.exists(), "Phase 8-4 documentation exists", DOC_FILE)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    ok, detail = _compile_file(MODULE_FILE)
    rec.add(ok, "Phase 8-4 module syntax valid", detail)

    try:
        module = _import_module(MODULE_FILE, "phase8_customer_access_model")
        summary = module.build_phase8_4_summary()
        rec.add(isinstance(summary, dict), "Phase 8-4 module imports and writes outputs", type(summary).__name__)
    except Exception as exc:
        rec.add(False, "Phase 8-4 module imports and writes outputs", exc)
        traceback.print_exc()

    rec.add(summary.get("ready_marker") == READY_MARKER, "Customer access model has ready marker", summary.get("ready_marker"))
    rec.add(summary.get("release_decision") == RELEASE_DECISION, "Customer access model has release decision", summary.get("release_decision"))
    rec.add(summary.get("source_mode") == SOURCE_MODE, "Customer access model uses expected source mode", summary.get("source_mode"))
    rec.add(summary.get("dashboard_change_required") is False, "No dashboard change required", summary.get("dashboard_change_required"))
    rec.add(summary.get("engine_change_required") is False, "No engine change required", summary.get("engine_change_required"))
    rec.add(summary.get("customer_access_model_created") is True, "Customer access model created", summary.get("customer_access_model_created"))
    rec.add(summary.get("payment_integration_not_implemented") is True, "Payment integration flagged as not implemented", summary.get("payment_integration_not_implemented"))
    rec.add(summary.get("access_control_not_implemented") is True, "Access control flagged as not implemented", summary.get("access_control_not_implemented"))
    rec.add(summary.get("manual_private_beta_supported") is True, "Manual private beta supported", summary.get("manual_private_beta_supported"))
    rec.add(summary.get("password_gated_mvp_supported") is True, "Password-gated MVP supported", summary.get("password_gated_mvp_supported"))
    rec.add(summary.get("full_subscription_system_deferred") is True, "Full subscription system deferred", summary.get("full_subscription_system_deferred"))
    rec.add(summary.get("streamlit_mvp_path_supported") is True, "Streamlit MVP path supported", summary.get("streamlit_mvp_path_supported"))
    rec.add(isinstance(summary.get("access_option_rows"), int) and summary.get("access_option_rows", 0) >= 5, "Access model table has rows", summary.get("access_option_rows"))
    rec.add(isinstance(summary.get("recommended_first_step_count"), int) and summary.get("recommended_first_step_count", 0) >= 1, "At least one first-step access model recommended", summary.get("recommended_first_step_count"))
    rec.add(summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    rec.add(summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    rec.add(summary.get("historical_data_is_scenario_input_not_forecast") is True, "Historical data is scenario input, not forecast", summary.get("historical_data_is_scenario_input_not_forecast"))

    for label, path in [
        ("access_model_csv", ACCESS_MODEL_CSV),
        ("summary_csv", SUMMARY_CSV),
        ("json", JSON_REPORT),
        ("report", TEXT_REPORT),
    ]:
        rec.add(path.exists(), f"Output written: {label}", path)

    access_ok = False
    access_detail = "missing"
    if ACCESS_MODEL_CSV.exists():
        try:
            df = pd.read_csv(ACCESS_MODEL_CSV)
            text = df.astype(str).to_string(index=False)
            access_ok = len(df) >= 5 and "manual private beta" in text and "password-gated" in text and "recommended_first_step" in df.columns
            access_detail = f"rows={len(df)}"
        except Exception as exc:
            access_detail = str(exc)
    rec.add(access_ok, "Customer access CSV has expected content", access_detail)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall Phase 8-4 checkpoint status: {final_status}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join([f"{r['status']:<10} {r['label']:<76} {r['detail']}" for r in rec.rows] + ["", f"Overall Phase 8-4 checkpoint status: {final_status}"]) + "\n",
        encoding="utf-8",
    )
    CHECKPOINT_JSON.write_text(json.dumps({"overall_status": final_status, "checks": rec.rows}, indent=2), encoding="utf-8")
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if rec.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
