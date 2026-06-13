"""
run_deployment_step_4_streamlit_cloud_deployment_checklist_check.py

Deployment Step 4 - Streamlit Cloud deployment checklist check.
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

MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "deployment_step_4_streamlit_cloud_deployment_checklist.py"
DOC_FILE = PROJECT_ROOT / "docs" / "deployment_step_4_streamlit_cloud_deployment_checklist.md"
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"
STREAMLIT_CONFIG = PROJECT_ROOT / ".streamlit" / "config.toml"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

CHECKLIST_CSV = OUTPUT_TABLE_DIR / "deployment_step_4_streamlit_cloud_deployment_checklist.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "deployment_step_4_streamlit_cloud_deployment_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "deployment_step_4_streamlit_cloud_deployment_checklist.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "deployment_step_4_streamlit_cloud_deployment_checklist_report.txt"

CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "deployment_step_4_streamlit_cloud_deployment_checklist_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "deployment_step_4_streamlit_cloud_deployment_checklist_checkpoint.json"

READY_MARKER = "DEPLOYMENT_STEP_4_STREAMLIT_CLOUD_DEPLOYMENT_CHECKLIST_READY"
RELEASE_DECISION = "DEPLOYMENT_STEP_4_CHECKLIST_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "streamlit_cloud_deployment_checklist"
ENTRYPOINT = "app/paid_simulator/config_form_app.py"
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
    print("Deployment Step 4 - Streamlit Cloud deployment checklist check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    summary: dict[str, Any] = {}

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(MODULE_FILE.exists(), "Deployment Step 4 module exists", MODULE_FILE)
    rec.add(DOC_FILE.exists(), "Deployment Step 4 documentation exists", DOC_FILE)
    rec.add(REQUIREMENTS_FILE.exists(), "requirements.txt exists", REQUIREMENTS_FILE)
    rec.add(STREAMLIT_CONFIG.exists(), ".streamlit config exists", STREAMLIT_CONFIG)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    ok, detail = _compile_file(MODULE_FILE)
    rec.add(ok, "Deployment Step 4 module syntax valid", detail)

    try:
        module = _import_module(MODULE_FILE, "deployment_step_4_streamlit_cloud_deployment_checklist")
        summary = module.build_deployment_step_4_summary()
        rec.add(isinstance(summary, dict), "Deployment Step 4 module imports and writes outputs", type(summary).__name__)
    except Exception as exc:
        rec.add(False, "Deployment Step 4 module imports and writes outputs", exc)
        traceback.print_exc()

    rec.add(summary.get("ready_marker") == READY_MARKER, "Deployment Step 4 has ready marker", summary.get("ready_marker"))
    rec.add(summary.get("release_decision") == RELEASE_DECISION, "Deployment Step 4 has release decision", summary.get("release_decision"))
    rec.add(summary.get("source_mode") == SOURCE_MODE, "Deployment Step 4 uses expected source mode", summary.get("source_mode"))
    rec.add(summary.get("dashboard_change_required") is False, "No dashboard change required", summary.get("dashboard_change_required"))
    rec.add(summary.get("engine_change_required") is False, "No engine change required", summary.get("engine_change_required"))
    rec.add(summary.get("streamlit_entrypoint") == ENTRYPOINT, "Streamlit entrypoint is set", summary.get("streamlit_entrypoint"))
    rec.add(summary.get("requirements_txt_exists") is True, "requirements.txt confirmed", summary.get("requirements_txt_exists"))
    rec.add(summary.get("streamlit_config_exists") is True, ".streamlit config confirmed", summary.get("streamlit_config_exists"))
    rec.add(summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    rec.add(summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    rec.add(summary.get("historical_data_is_scenario_input_not_forecast") is True, "Historical data is scenario input, not forecast", summary.get("historical_data_is_scenario_input_not_forecast"))
    rec.add(summary.get("no_secrets_committed_required") is True, "No-secrets rule included", summary.get("no_secrets_committed_required"))
    rec.add(summary.get("git_repository_required") is True, "Git repository requirement included", summary.get("git_repository_required"))
    rec.add(summary.get("hosted_smoke_test_next") is True, "Hosted smoke test marked as next", summary.get("hosted_smoke_test_next"))
    rec.add(isinstance(summary.get("checklist_rows"), int) and summary.get("checklist_rows", 0) >= 10, "Checklist has rows", summary.get("checklist_rows"))

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
            checklist_ok = len(df) >= 10 and "Git repository ready" in text and "No secrets committed" in text and "Streamlit entry point selected" in text
            checklist_detail = f"rows={len(df)}"
        except Exception as exc:
            checklist_detail = str(exc)
    rec.add(checklist_ok, "Deployment checklist CSV has expected content", checklist_detail)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall deployment Step 4 status: {final_status}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join(
            [f"{r['status']:<10} {r['label']:<76} {r['detail']}" for r in rec.rows]
            + ["", f"Overall deployment Step 4 status: {final_status}"]
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
