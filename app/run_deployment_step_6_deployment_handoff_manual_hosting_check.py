"""
run_deployment_step_6_deployment_handoff_manual_hosting_check.py

Deployment Step 6 handoff and manual hosting instructions check.
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

MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "deployment_step_6_deployment_handoff_manual_hosting.py"
DOC_FILE = PROJECT_ROOT / "docs" / "deployment_step_6_deployment_handoff_manual_hosting.md"
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"
STREAMLIT_CONFIG_FILE = PROJECT_ROOT / ".streamlit" / "config.toml"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

HANDOFF_CSV = OUTPUT_TABLE_DIR / "deployment_step_6_deployment_handoff_manual_hosting.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "deployment_step_6_deployment_handoff_manual_hosting_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "deployment_step_6_deployment_handoff_manual_hosting.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "deployment_step_6_deployment_handoff_manual_hosting_report.txt"

CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "deployment_step_6_deployment_handoff_manual_hosting_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "deployment_step_6_deployment_handoff_manual_hosting_checkpoint.json"

READY_MARKER = "DEPLOYMENT_STEP_6_HANDOFF_MANUAL_HOSTING_READY"
RELEASE_DECISION = "DEPLOYMENT_STEP_6_HANDOFF_MANUAL_HOSTING_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "deployment_handoff_manual_hosting"
ENTRY_POINT = "app/paid_simulator/config_form_app.py"
LOCAL_COMMAND = "streamlit run app/paid_simulator/config_form_app.py"
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
    print("Deployment Step 6 handoff and manual hosting instructions check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    summary: dict[str, Any] = {}

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(REQUIREMENTS_FILE.exists(), "requirements.txt exists", REQUIREMENTS_FILE)
    rec.add(STREAMLIT_CONFIG_FILE.exists(), ".streamlit config exists", STREAMLIT_CONFIG_FILE)
    rec.add(MODULE_FILE.exists(), "Deployment Step 6 handoff module exists", MODULE_FILE)
    rec.add(DOC_FILE.exists(), "Deployment Step 6 documentation exists", DOC_FILE)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    ok, detail = _compile_file(MODULE_FILE)
    rec.add(ok, "Deployment Step 6 module syntax valid", detail)

    try:
        module = _import_module(MODULE_FILE, "deployment_step_6_deployment_handoff_manual_hosting")
        summary = module.build_deployment_step_6_summary()
        rec.add(isinstance(summary, dict), "Deployment Step 6 module imports and writes outputs", type(summary).__name__)
    except Exception as exc:
        rec.add(False, "Deployment Step 6 module imports and writes outputs", exc)
        traceback.print_exc()

    rec.add(summary.get("ready_marker") == READY_MARKER, "Deployment Step 6 has ready marker", summary.get("ready_marker"))
    rec.add(summary.get("release_decision") == RELEASE_DECISION, "Deployment Step 6 has release decision", summary.get("release_decision"))
    rec.add(summary.get("source_mode") == SOURCE_MODE, "Deployment Step 6 uses expected source mode", summary.get("source_mode"))
    rec.add(summary.get("dashboard_change_required") is False, "No dashboard change required", summary.get("dashboard_change_required"))
    rec.add(summary.get("engine_change_required") is False, "No engine change required", summary.get("engine_change_required"))
    rec.add(summary.get("deployment_handoff_created") is True, "Deployment handoff created", summary.get("deployment_handoff_created"))
    rec.add(summary.get("streamlit_entry_point") == ENTRY_POINT, "Streamlit entry point recorded", summary.get("streamlit_entry_point"))
    rec.add(summary.get("local_streamlit_command") == LOCAL_COMMAND, "Local Streamlit command recorded", summary.get("local_streamlit_command"))
    rec.add(summary.get("streamlit_mvp_path_supported") is True, "Streamlit MVP path supported", summary.get("streamlit_mvp_path_supported"))
    rec.add(summary.get("customer_access_control_required") is True, "Customer access control required", summary.get("customer_access_control_required"))
    rec.add(summary.get("hosted_smoke_test_required") is True, "Hosted smoke test required", summary.get("hosted_smoke_test_required"))
    rec.add(summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    rec.add(summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    rec.add(summary.get("unknown_modes_fall_back_to_synthetic") is True, "Unknown modes fall back to synthetic", summary.get("unknown_modes_fall_back_to_synthetic"))
    rec.add(summary.get("historical_data_is_scenario_input_not_forecast") is True, "Historical data is scenario input, not forecast", summary.get("historical_data_is_scenario_input_not_forecast"))
    rec.add(isinstance(summary.get("handoff_rows"), int) and summary.get("handoff_rows", 0) >= 10, "Deployment handoff has rows", summary.get("handoff_rows"))
    rec.add(isinstance(summary.get("required_handoff_steps"), int) and summary.get("required_handoff_steps", 0) >= 10, "Required handoff steps present", summary.get("required_handoff_steps"))

    for label, path in [
        ("handoff_csv", HANDOFF_CSV),
        ("summary_csv", SUMMARY_CSV),
        ("json", JSON_REPORT),
        ("report", TEXT_REPORT),
    ]:
        rec.add(path.exists(), f"Output written: {label}", path)

    handoff_ok = False
    handoff_detail = "missing"
    if HANDOFF_CSV.exists():
        try:
            df = pd.read_csv(HANDOFF_CSV)
            text = df.astype(str).to_string(index=False)
            handoff_ok = len(df) >= 10 and "Streamlit entry point" in text and "Hosted launch" in text and "Customer access control" in text
            handoff_detail = f"rows={len(df)}"
        except Exception as exc:
            handoff_detail = str(exc)
    rec.add(handoff_ok, "Deployment handoff CSV has expected content", handoff_detail)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall deployment Step 6 status: {final_status}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join(
            [f"{r['status']:<10} {r['label']:<76} {r['detail']}" for r in rec.rows]
            + ["", f"Overall deployment Step 6 status: {final_status}"]
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
