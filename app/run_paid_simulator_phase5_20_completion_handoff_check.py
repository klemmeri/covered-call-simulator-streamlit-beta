"""
run_paid_simulator_phase5_20_completion_handoff_check.py

Checkpoint runner for Phase 5-20 completion handoff.
"""

from __future__ import annotations

import importlib.util
import json
import py_compile
import sys
import traceback
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_SIM_DIR = APP_DIR / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

PHASE5_20_FILE = PAID_SIM_DIR / "phase5_completion_handoff.py"
DOC_FILE = DOCS_DIR / "phase5_20_completion_handoff.md"
DASHBOARD_FILE = PAID_SIM_DIR / "config_form_app.py"

CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase5_20_completion_handoff_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase5_20_completion_handoff_checkpoint.json"

EXPECTED_OUTPUTS = {
    "artifact_status_csv": OUTPUT_TABLE_DIR / "phase5_20_completion_artifact_status.csv",
    "core_engine_status_csv": OUTPUT_TABLE_DIR / "phase5_20_core_engine_file_status.csv",
    "prior_output_status_csv": OUTPUT_TABLE_DIR / "phase5_20_prior_output_status.csv",
    "phase6_plan_csv": OUTPUT_TABLE_DIR / "phase5_20_phase6_recommended_plan.csv",
    "summary_csv": OUTPUT_TABLE_DIR / "phase5_20_completion_handoff_summary.csv",
    "json": OUTPUT_REPORT_DIR / "phase5_20_completion_handoff.json",
    "report": OUTPUT_REPORT_DIR / "phase5_20_completion_handoff_report.txt",
}


def _print_header(title: str) -> None:
    print("=" * 100)
    print(title)
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()


def _record(results: list[dict[str, Any]], passed: bool, label: str, detail: Any = "") -> None:
    status = "PASS" if passed else "FAIL"
    print(f"{status:<10} {label:<70} {detail}")
    results.append({"status": status, "label": label, "detail": str(detail)})


def _compile_file(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "syntax valid"
    except Exception as exc:
        return False, str(exc)


def _import_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    summary: dict[str, Any] | None = None

    _print_header("Phase 5-20 completion handoff check")

    _record(results, DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    _record(results, PHASE5_20_FILE.exists(), "Phase 5-20 completion module exists", PHASE5_20_FILE)
    _record(results, DOC_FILE.exists(), "Phase 5-20 documentation exists", DOC_FILE)

    for label, path in [
        ("Dashboard syntax remains valid", DASHBOARD_FILE),
        ("Phase 5-20 module syntax valid", PHASE5_20_FILE),
    ]:
        if path.exists():
            ok, detail = _compile_file(path)
            _record(results, ok, label, detail)
        else:
            _record(results, False, label, "file missing")

    try:
        module = _import_module(PHASE5_20_FILE, "phase5_completion_handoff")
        summary = module.build_phase5_20_summary()
        _record(results, isinstance(summary, dict), "Phase 5-20 module imports and builds handoff", type(summary).__name__)
    except Exception as exc:
        _record(results, False, "Phase 5-20 module imports and builds handoff", exc)
        traceback.print_exc()

    if isinstance(summary, dict):
        _record(results, summary.get("ready_marker") == "PHASE5_20_COMPLETION_HANDOFF_READY", "Completion handoff has ready marker", summary.get("ready_marker"))
        _record(results, summary.get("release_decision") == "PHASE5_COMPLETE_READY_FOR_PHASE6_DASHBOARD_INTEGRATION", "Completion handoff has release decision", summary.get("release_decision"))
        _record(results, summary.get("dashboard_change_required") is False, "Completion handoff confirms no dashboard change", summary.get("dashboard_change_required"))
        _record(results, summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
        _record(results, summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
        _record(results, summary.get("phase5_complete") is True, "Phase 5 marked complete", summary.get("phase5_complete"))
        _record(results, summary.get("ready_for_phase6") is True, "Ready for Phase 6", summary.get("ready_for_phase6"))
        _record(results, int(summary.get("phase5_artifact_count", 0)) >= 19, "Phase 5 artifact count is plausible", summary.get("phase5_artifact_count"))
        _record(results, int(summary.get("phase6_recommendation_count", 0)) >= 1, "Phase 6 recommendations are present", summary.get("phase6_recommendation_count"))
    else:
        _record(results, False, "Completion summary produced", "summary was not a dict")

    for label, path in EXPECTED_OUTPUTS.items():
        _record(results, path.exists(), f"Output written: {label}", path)

    overall_pass = all(row["status"] == "PASS" for row in results)

    print()
    print("=" * 100)
    print(f"Overall Phase 5-20 checkpoint status: {'PASS' if overall_pass else 'FAIL'}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join([f"{row['status']:<10} {row['label']:<70} {row['detail']}" for row in results])
        + f"\n\nOverall Phase 5-20 checkpoint status: {'PASS' if overall_pass else 'FAIL'}\n",
        encoding="utf-8",
    )
    CHECKPOINT_JSON.write_text(json.dumps({"overall_pass": overall_pass, "results": results}, indent=2), encoding="utf-8")

    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
