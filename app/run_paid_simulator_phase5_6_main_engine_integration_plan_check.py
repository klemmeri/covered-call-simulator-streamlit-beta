"""
run_paid_simulator_phase5_6_main_engine_integration_plan_check.py

Checkpoint check for Phase 5-6 - Main engine integration planning.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import traceback
from pathlib import Path
from typing import Any

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]

DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
PRIOR_PHASE5_5_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase5_historical_mode_simulation_smoke_test.py"
PHASE5_6_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase5_main_engine_integration_plan.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase5_6_main_engine_integration_plan.md"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

CHECK_REPORT_PATH = OUTPUT_REPORT_DIR / "phase5_6_main_engine_integration_plan_checkpoint_report.txt"
CHECK_JSON_PATH = OUTPUT_REPORT_DIR / "phase5_6_main_engine_integration_plan_checkpoint.json"

EXPECTED_OUTPUTS = {
    "engine_status_csv": OUTPUT_TABLE_DIR / "phase5_6_engine_file_status.csv",
    "artifact_status_csv": OUTPUT_TABLE_DIR / "phase5_6_prior_artifact_status.csv",
    "integration_touchpoints_csv": OUTPUT_TABLE_DIR / "phase5_6_engine_integration_touchpoints.csv",
    "recommended_patch_order_csv": OUTPUT_TABLE_DIR / "phase5_6_recommended_patch_order.csv",
    "summary_csv": OUTPUT_TABLE_DIR / "phase5_6_main_engine_integration_plan_summary.csv",
    "json": OUTPUT_REPORT_DIR / "phase5_6_main_engine_integration_plan.json",
    "report": OUTPUT_REPORT_DIR / "phase5_6_main_engine_integration_plan_report.txt",
}


class CheckRecorder:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(self, passed: bool, label: str, detail: Any = "") -> None:
        self.rows.append({"passed": bool(passed), "label": label, "detail": "" if detail is None else str(detail)})
        status = "PASS" if passed else "FAIL"
        print(f"{status:<10} {label:<70} {'' if detail is None else detail}")

    @property
    def ok(self) -> bool:
        return all(row["passed"] for row in self.rows)


def _syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:
        return False, str(exc)


def _import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _csv_rows(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        return int(len(pd.read_csv(path)))
    except Exception:
        return None


def main() -> int:
    print("=" * 100)
    print("Phase 5-6 main engine integration plan check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    rec = CheckRecorder()
    summary: dict[str, Any] | None = None

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(PRIOR_PHASE5_5_FILE.exists(), "Prior Phase 5-5 smoke-test module exists", PRIOR_PHASE5_5_FILE)
    rec.add(PHASE5_6_FILE.exists(), "Phase 5-6 integration-plan module exists", PHASE5_6_FILE)
    rec.add(DOC_FILE.exists(), "Phase 5-6 documentation exists", DOC_FILE)

    if DASHBOARD_FILE.exists():
        ok, detail = _syntax_valid(DASHBOARD_FILE)
        rec.add(ok, "Dashboard syntax remains valid", detail)
    else:
        rec.add(False, "Dashboard syntax remains valid", "dashboard file missing")

    if PHASE5_6_FILE.exists():
        ok, detail = _syntax_valid(PHASE5_6_FILE)
        rec.add(ok, "Phase 5-6 module syntax valid", detail)
        if ok:
            try:
                module = _import_module(PHASE5_6_FILE, "phase5_main_engine_integration_plan")
                summary = module.build_phase5_6_summary()
                rec.add(isinstance(summary, dict), "Phase 5-6 module imports and builds plan", type(summary).__name__)
            except Exception as exc:
                rec.add(False, "Phase 5-6 module imports and builds plan", exc)
                traceback.print_exc()
    else:
        rec.add(False, "Phase 5-6 module syntax valid", "module missing")

    if summary is None:
        summary = {}

    rec.add(
        summary.get("ready_marker") == "PHASE5_6_MAIN_ENGINE_INTEGRATION_PLAN_READY",
        "Integration plan has ready marker",
        summary.get("ready_marker"),
    )
    rec.add(
        summary.get("release_decision") == "PHASE5_6_MAIN_ENGINE_INTEGRATION_PLAN_CREATED_NO_ENGINE_PATCH_NO_DASHBOARD_CHANGE",
        "Integration plan has release decision",
        summary.get("release_decision"),
    )
    rec.add(summary.get("dashboard_change_required") is False, "Integration plan confirms no dashboard change", summary.get("dashboard_change_required"))
    rec.add(summary.get("engine_patch_applied") is False, "No engine patch applied yet", summary.get("engine_patch_applied"))
    rec.add(summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    rec.add(summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    rec.add(summary.get("source_mode") == "engine_integration_planning", "Integration plan uses planning mode", summary.get("source_mode"))
    rec.add(summary.get("planning_artifact_created") is True, "Planning artifact created", summary.get("planning_artifact_created"))
    rec.add((summary.get("integration_touchpoint_rows") or 0) >= 5, "Integration plan lists engine touchpoints", summary.get("integration_touchpoint_rows"))
    rec.add((summary.get("recommended_patch_order_rows") or 0) >= 5, "Integration plan lists recommended patch order", summary.get("recommended_patch_order_rows"))
    rec.add(summary.get("required_engine_columns_present") is True, "Integration plan lists required engine columns", summary.get("required_engine_columns_present"))

    for label, path in EXPECTED_OUTPUTS.items():
        rec.add(path.exists(), f"Output written: {label}", path)

    integration_rows = _csv_rows(EXPECTED_OUTPUTS["integration_touchpoints_csv"])
    patch_order_rows = _csv_rows(EXPECTED_OUTPUTS["recommended_patch_order_csv"])
    rec.add((integration_rows or 0) >= 5, "Integration touchpoints CSV has expected content", f"rows={integration_rows}")
    rec.add((patch_order_rows or 0) >= 5, "Recommended patch order CSV has expected content", f"rows={patch_order_rows}")

    overall = "PASS" if rec.ok else "FAIL"
    print()
    print("=" * 100)
    print(f"Overall Phase 5-6 checkpoint status: {overall}")
    print("=" * 100)

    report_lines = [
        "Phase 5-6 main engine integration plan checkpoint report",
        "=" * 80,
        f"Overall status: {overall}",
        "",
    ]
    for row in rec.rows:
        status = "PASS" if row["passed"] else "FAIL"
        report_lines.append(f"{status:<8} {row['label']} - {row['detail']}")
    CHECK_REPORT_PATH.write_text("\n".join(report_lines), encoding="utf-8")
    CHECK_JSON_PATH.write_text(json.dumps({"overall_status": overall, "checks": rec.rows, "summary": summary}, indent=2), encoding="utf-8")

    print(f"Saved checkpoint report: {CHECK_REPORT_PATH}")
    print(f"Saved checkpoint JSON:   {CHECK_JSON_PATH}")

    return 0 if rec.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
