"""
run_deployment_step_8_github_create_push_instructions_check.py

Deployment Step 8 GitHub create/push instructions check.
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
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "deployment_step_8_github_create_push_instructions.py"
DOC_FILE = PROJECT_ROOT / "docs" / "deployment_step_8_github_create_push_instructions.md"
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"
STREAMLIT_CONFIG = PROJECT_ROOT / ".streamlit" / "config.toml"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

CHECKLIST_CSV = OUTPUT_TABLE_DIR / "deployment_step_8_github_create_push_instructions.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "deployment_step_8_github_create_push_instructions_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "deployment_step_8_github_create_push_instructions.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "deployment_step_8_github_create_push_instructions_report.txt"
CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "deployment_step_8_github_create_push_instructions_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "deployment_step_8_github_create_push_instructions_checkpoint.json"

READY_MARKER = "DEPLOYMENT_STEP_8_GITHUB_CREATE_PUSH_INSTRUCTIONS_READY"
RELEASE_DECISION = "DEPLOYMENT_STEP_8_GITHUB_INSTRUCTIONS_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "github_create_push_instructions"


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
    print("Deployment Step 8 GitHub create/push instructions check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    summary: dict[str, Any] = {}

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(REQUIREMENTS_FILE.exists(), "requirements.txt exists", REQUIREMENTS_FILE)
    rec.add(STREAMLIT_CONFIG.exists(), ".streamlit config exists", STREAMLIT_CONFIG)
    rec.add(MODULE_FILE.exists(), "Deployment Step 8 module exists", MODULE_FILE)
    rec.add(DOC_FILE.exists(), "Deployment Step 8 documentation exists", DOC_FILE)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    ok, detail = _compile_file(MODULE_FILE)
    rec.add(ok, "Deployment Step 8 module syntax valid", detail)

    try:
        module = _import_module(MODULE_FILE, "deployment_step_8_github_create_push_instructions")
        summary = module.build_deployment_step_8_summary()
        rec.add(isinstance(summary, dict), "Deployment Step 8 module imports and writes outputs", type(summary).__name__)
    except Exception as exc:
        rec.add(False, "Deployment Step 8 module imports and writes outputs", exc)
        traceback.print_exc()

    rec.add(summary.get("ready_marker") == READY_MARKER, "GitHub instructions have ready marker", summary.get("ready_marker"))
    rec.add(summary.get("release_decision") == RELEASE_DECISION, "GitHub instructions have release decision", summary.get("release_decision"))
    rec.add(summary.get("source_mode") == SOURCE_MODE, "GitHub instructions use expected source mode", summary.get("source_mode"))
    rec.add(summary.get("dashboard_change_required") is False, "No dashboard change required", summary.get("dashboard_change_required"))
    rec.add(summary.get("engine_change_required") is False, "No engine change required", summary.get("engine_change_required"))
    rec.add(summary.get("github_create_push_instructions_created") is True, "GitHub create/push instructions created", summary.get("github_create_push_instructions_created"))
    rec.add(summary.get("private_repository_recommended_first") is True, "Private repository recommended first", summary.get("private_repository_recommended_first"))
    rec.add(summary.get("streamlit_entrypoint") == "app/paid_simulator/config_form_app.py", "Streamlit entry point confirmed", summary.get("streamlit_entrypoint"))
    rec.add(summary.get("final_backup_recommended_before_push") is True, "Final backup recommended before push", summary.get("final_backup_recommended_before_push"))
    rec.add(summary.get("secrets_exclusion_required") is True, "Secrets exclusion required", summary.get("secrets_exclusion_required"))
    rec.add(isinstance(summary.get("checklist_rows"), int) and summary.get("checklist_rows", 0) >= 8, "Checklist has rows", summary.get("checklist_rows"))

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
            checklist_ok = len(df) >= 8 and "GitHub" in text and "config_form_app.py" in text and "secrets" in text.lower()
            checklist_detail = f"rows={len(df)}"
        except Exception as exc:
            checklist_detail = str(exc)
    rec.add(checklist_ok, "GitHub instructions CSV has expected content", checklist_detail)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall deployment Step 8 status: {final_status}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join(
            [f"{r['status']:<10} {r['label']:<76} {r['detail']}" for r in rec.rows]
            + ["", f"Overall deployment Step 8 status: {final_status}"]
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
