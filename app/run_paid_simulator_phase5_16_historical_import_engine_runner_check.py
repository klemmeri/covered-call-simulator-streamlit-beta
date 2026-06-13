"""
run_paid_simulator_phase5_16_historical_import_engine_runner_check.py

Checkpoint check for Phase 5-16 historical import engine-runner candidate.
"""

from __future__ import annotations

import importlib.util
import py_compile
import traceback
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_DIR = APP_DIR / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

DASHBOARD_FILE = PAID_DIR / "config_form_app.py"
PRIOR_PHASE5_15_MODULE = PAID_DIR / "phase5_full_engine_regression_after_simulator_promotion.py"
PHASE5_16_FILE = PAID_DIR / "phase5_historical_import_engine_runner_candidate.py"
PHASE5_16_DOC = DOCS_DIR / "phase5_16_historical_import_engine_runner_candidate.md"

EXPECTED_OUTPUTS = {
    "path_preview_csv": OUTPUT_TABLE_DIR / "phase5_16_historical_import_engine_runner_path_preview.csv",
    "runner_contract_csv": OUTPUT_TABLE_DIR / "phase5_16_historical_import_engine_runner_contract.csv",
    "summary_csv": OUTPUT_TABLE_DIR / "phase5_16_historical_import_engine_runner_summary.csv",
    "json": OUTPUT_REPORT_DIR / "phase5_16_historical_import_engine_runner_candidate.json",
    "report": OUTPUT_REPORT_DIR / "phase5_16_historical_import_engine_runner_candidate_report.txt",
}

CHECK_REPORT = OUTPUT_REPORT_DIR / "phase5_16_historical_import_engine_runner_checkpoint_report.txt"
CHECK_JSON = OUTPUT_REPORT_DIR / "phase5_16_historical_import_engine_runner_checkpoint.json"

results: list[dict[str, Any]] = []


def record(status: bool, label: str, detail: Any = "") -> None:
    results.append({"status": "PASS" if status else "FAIL", "label": label, "detail": str(detail)})
    print(f"{'PASS' if status else 'FAIL':<10} {label:<70} {detail}")


def compile_file(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "syntax valid"
    except Exception as exc:
        return False, str(exc)


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    print("=" * 100)
    print("Phase 5-16 historical import engine-runner candidate check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    record(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    record(PRIOR_PHASE5_15_MODULE.exists(), "Prior Phase 5-15 regression module exists", PRIOR_PHASE5_15_MODULE)
    record(PHASE5_16_FILE.exists(), "Phase 5-16 runner candidate module exists", PHASE5_16_FILE)
    record(PHASE5_16_DOC.exists(), "Phase 5-16 documentation exists", PHASE5_16_DOC)

    if DASHBOARD_FILE.exists():
        ok, detail = compile_file(DASHBOARD_FILE)
        record(ok, "Dashboard syntax remains valid", detail)

    if PHASE5_16_FILE.exists():
        ok, detail = compile_file(PHASE5_16_FILE)
        record(ok, "Phase 5-16 module syntax valid", detail)

    summary = None
    try:
        module = import_module(PHASE5_16_FILE, "phase5_historical_import_engine_runner_candidate")
        summary = module.build_phase5_16_summary()
        record(isinstance(summary, dict), "Phase 5-16 module imports and builds runner candidate", type(summary).__name__)
    except Exception as exc:
        record(False, "Phase 5-16 module imports and builds runner candidate", exc)
        traceback.print_exc()

    if not isinstance(summary, dict):
        summary = {}

    record(
        summary.get("ready_marker") == "PHASE5_16_HISTORICAL_IMPORT_ENGINE_RUNNER_CANDIDATE_READY",
        "Runner candidate has ready marker",
        summary.get("ready_marker"),
    )
    record(
        summary.get("release_decision") == "PHASE5_16_HISTORICAL_IMPORT_ENGINE_RUNNER_CANDIDATE_CREATED_NO_DASHBOARD_CHANGE",
        "Runner candidate has release decision",
        summary.get("release_decision"),
    )
    record(summary.get("dashboard_change_required") is False, "Runner candidate confirms no dashboard change", summary.get("dashboard_change_required"))
    record(summary.get("source_mode") == "historical_import_engine_runner_candidate", "Runner candidate uses expected source mode", summary.get("source_mode"))
    record(summary.get("requested_mode") == "historical_import", "Runner candidate requested historical import", summary.get("requested_mode"))
    record(summary.get("selected_mode") == "historical_import", "Runner candidate selected historical import", summary.get("selected_mode"))
    record(summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    record(summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    record(summary.get("engine_runner_candidate_created") is True, "Engine-runner candidate created", summary.get("engine_runner_candidate_created"))
    record(summary.get("live_core_engine_replaced") is False, "No live core engine replacement in this checkpoint", summary.get("live_core_engine_replaced"))
    record((summary.get("historical_path_rows") or 0) >= 1, "Historical path has rows", summary.get("historical_path_rows"))
    record((summary.get("runner_contract_rows") or 0) >= 5, "Runner contract has rows", summary.get("runner_contract_rows"))
    record((summary.get("start_price") or 0) > 0, "Start price is positive", summary.get("start_price"))
    record((summary.get("end_price") or 0) > 0, "End price is positive", summary.get("end_price"))
    record(summary.get("overall_status") == "PASS", "Runner candidate overall status is PASS", summary.get("overall_status"))

    for label, path in EXPECTED_OUTPUTS.items():
        record(path.exists(), f"Output written: {label}", path)

    overall = all(row["status"] == "PASS" for row in results)

    print()
    print("=" * 100)
    print(f"Overall Phase 5-16 checkpoint status: {'PASS' if overall else 'FAIL'}")
    print("=" * 100)

    import json
    CHECK_REPORT.write_text(
        "\n".join([f"{r['status']:<10} {r['label']:<70} {r['detail']}" for r in results])
        + f"\n\nOverall Phase 5-16 checkpoint status: {'PASS' if overall else 'FAIL'}\n",
        encoding="utf-8",
    )
    CHECK_JSON.write_text(json.dumps({"overall_status": "PASS" if overall else "FAIL", "results": results}, indent=2), encoding="utf-8")

    print(f"Saved checkpoint report: {CHECK_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECK_JSON}")

    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
