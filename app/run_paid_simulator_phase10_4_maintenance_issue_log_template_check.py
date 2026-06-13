"""
run_paid_simulator_phase10_4_maintenance_issue_log_template_check.py

Phase 10-4 maintenance and issue-log template check.
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

MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase10_maintenance_issue_log_template.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase10_4_maintenance_issue_log_template.md"
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

ISSUE_LOG_CSV = OUTPUT_TABLE_DIR / "phase10_4_maintenance_issue_log_template.csv"
MAINTENANCE_CHECKLIST_CSV = OUTPUT_TABLE_DIR / "phase10_4_maintenance_checklist.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase10_4_maintenance_issue_log_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase10_4_maintenance_issue_log_template.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase10_4_maintenance_issue_log_template_report.txt"

CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase10_4_maintenance_issue_log_template_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase10_4_maintenance_issue_log_template_checkpoint.json"

READY_MARKER = "PHASE10_4_MAINTENANCE_ISSUE_LOG_TEMPLATE_READY"
RELEASE_DECISION = "PHASE10_4_MAINTENANCE_ISSUE_LOG_TEMPLATE_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "maintenance_issue_log_template"


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
    print("Phase 10-4 maintenance and issue-log template check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    summary: dict[str, Any] = {}

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(MODULE_FILE.exists(), "Phase 10-4 maintenance module exists", MODULE_FILE)
    rec.add(DOC_FILE.exists(), "Phase 10-4 documentation exists", DOC_FILE)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    ok, detail = _compile_file(MODULE_FILE)
    rec.add(ok, "Phase 10-4 module syntax valid", detail)

    try:
        module = _import_module(MODULE_FILE, "phase10_maintenance_issue_log_template")
        summary = module.build_phase10_4_summary()
        rec.add(isinstance(summary, dict), "Phase 10-4 module imports and writes outputs", type(summary).__name__)
    except Exception as exc:
        rec.add(False, "Phase 10-4 module imports and writes outputs", exc)
        traceback.print_exc()

    rec.add(summary.get("ready_marker") == READY_MARKER, "Maintenance template has ready marker", summary.get("ready_marker"))
    rec.add(summary.get("release_decision") == RELEASE_DECISION, "Maintenance template has release decision", summary.get("release_decision"))
    rec.add(summary.get("source_mode") == SOURCE_MODE, "Maintenance template uses expected source mode", summary.get("source_mode"))
    rec.add(summary.get("dashboard_change_required") is False, "No dashboard change required", summary.get("dashboard_change_required"))
    rec.add(summary.get("engine_change_required") is False, "No engine change required", summary.get("engine_change_required"))
    rec.add(summary.get("maintenance_issue_log_template_created") is True, "Issue-log template created", summary.get("maintenance_issue_log_template_created"))
    rec.add(summary.get("maintenance_checklist_created") is True, "Maintenance checklist created", summary.get("maintenance_checklist_created"))
    rec.add(isinstance(summary.get("issue_log_rows"), int) and summary.get("issue_log_rows", 0) >= 10, "Issue-log template has rows", summary.get("issue_log_rows"))
    rec.add(isinstance(summary.get("maintenance_checklist_rows"), int) and summary.get("maintenance_checklist_rows", 0) >= 8, "Maintenance checklist has rows", summary.get("maintenance_checklist_rows"))
    rec.add(summary.get("version_policy_reference") == "Phase 10-3", "Version policy referenced", summary.get("version_policy_reference"))
    rec.add(summary.get("backup_policy_reference") == "Phase 10-3", "Backup policy referenced", summary.get("backup_policy_reference"))
    rec.add(summary.get("final_smoke_test_next") is True, "Final smoke test identified as next step", summary.get("final_smoke_test_next"))
    rec.add(summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    rec.add(summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    rec.add(summary.get("historical_data_is_scenario_input_not_forecast") is True, "Historical data is scenario input, not forecast", summary.get("historical_data_is_scenario_input_not_forecast"))
    rec.add(summary.get("regime_detection_probabilistic_not_oracle") is True, "Regime detection remains probabilistic, not oracle", summary.get("regime_detection_probabilistic_not_oracle"))
    rec.add(summary.get("no_guaranteed_profit_wording") is True, "No guaranteed-profit wording rule preserved", summary.get("no_guaranteed_profit_wording"))

    for label, path in [
        ("issue_log_csv", ISSUE_LOG_CSV),
        ("maintenance_checklist_csv", MAINTENANCE_CHECKLIST_CSV),
        ("summary_csv", SUMMARY_CSV),
        ("json", JSON_REPORT),
        ("report", TEXT_REPORT),
    ]:
        rec.add(path.exists(), f"Output written: {label}", path)

    issue_ok = False
    issue_detail = "missing"
    if ISSUE_LOG_CSV.exists():
        try:
            df = pd.read_csv(ISSUE_LOG_CSV)
            text = df.astype(str).to_string(index=False)
            issue_ok = len(df) >= 10 and "issue_id" in text and "severity" in text and "version_fixed" in text
            issue_detail = f"rows={len(df)}"
        except Exception as exc:
            issue_detail = str(exc)
    rec.add(issue_ok, "Issue-log CSV has expected content", issue_detail)

    checklist_ok = False
    checklist_detail = "missing"
    if MAINTENANCE_CHECKLIST_CSV.exists():
        try:
            df = pd.read_csv(MAINTENANCE_CHECKLIST_CSV)
            text = df.astype(str).to_string(index=False)
            checklist_ok = len(df) >= 8 and "Backups" in text and "Regression checks" in text and "Disclaimer review" in text
            checklist_detail = f"rows={len(df)}"
        except Exception as exc:
            checklist_detail = str(exc)
    rec.add(checklist_ok, "Maintenance checklist CSV has expected content", checklist_detail)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall Phase 10-4 checkpoint status: {final_status}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join(
            [f"{r['status']:<10} {r['label']:<76} {r['detail']}" for r in rec.rows]
            + ["", f"Overall Phase 10-4 checkpoint status: {final_status}"]
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
