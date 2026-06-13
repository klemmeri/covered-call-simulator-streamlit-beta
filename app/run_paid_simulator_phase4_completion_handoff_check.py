"""
run_paid_simulator_phase4_completion_handoff_check.py

Checkpoint runner for Phase 4 completion and Phase 5 planning handoff.
"""

from __future__ import annotations

import importlib.util
import json
import py_compile
import traceback
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
PHASE4_COMPLETION_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase4_completion_handoff.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase4_completion_handoff.md"
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"

EXPECTED_OUTPUTS = {
    "artifact_status_csv": TABLES_DIR / "phase4_completion_handoff_artifact_status.csv",
    "summary_csv": TABLES_DIR / "phase4_completion_handoff_summary.csv",
    "json": REPORTS_DIR / "phase4_completion_handoff.json",
    "report": REPORTS_DIR / "phase4_completion_handoff_report.txt",
}

PRIOR_PHASE_FILES = {
    "Phase 4-2 scaffold": PROJECT_ROOT / "app" / "paid_simulator" / "phase4_market_data_input_scaffold.py",
    "Phase 4-3 loader-validator": PROJECT_ROOT / "app" / "paid_simulator" / "phase4_market_data_loader_validator.py",
    "Phase 4-4 historical-path adapter": PROJECT_ROOT / "app" / "paid_simulator" / "phase4_historical_price_path_adapter.py",
    "Phase 4-5 option-chain lookup": PROJECT_ROOT / "app" / "paid_simulator" / "phase4_option_chain_premium_lookup.py",
    "Phase 4-6 calibration report": PROJECT_ROOT / "app" / "paid_simulator" / "phase4_premium_model_calibration_report.py",
    "Phase 4-7 imported-data comparison": PROJECT_ROOT / "app" / "paid_simulator" / "phase4_strategy_comparison_imported_data.py",
}


def print_header(title: str) -> None:
    print("=" * 100)
    print(title)
    print("=" * 100)


def record(results: list[dict[str, Any]], passed: bool, label: str, detail: Any = "") -> None:
    status = "PASS" if passed else "FAIL"
    results.append({"status": status, "label": label, "detail": str(detail)})
    print(f"{status:<10} {label:<70} {detail}")


def compile_file(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "syntax valid"
    except Exception as exc:
        return False, str(exc)


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    results: list[dict[str, Any]] = []
    print_header("Phase 4 completion handoff checkpoint")
    print(f"Project root: {PROJECT_ROOT}\n")

    record(results, DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    for label, path in PRIOR_PHASE_FILES.items():
        record(results, path.exists(), f"Prior {label} module exists", path)
    record(results, PHASE4_COMPLETION_FILE.exists(), "Phase 4 completion handoff module exists", PHASE4_COMPLETION_FILE)
    record(results, DOC_FILE.exists(), "Phase 4 completion documentation exists", DOC_FILE)

    if DASHBOARD_FILE.exists():
        ok, detail = compile_file(DASHBOARD_FILE)
        record(results, ok, "Dashboard syntax remains valid", detail)
    if PHASE4_COMPLETION_FILE.exists():
        ok, detail = compile_file(PHASE4_COMPLETION_FILE)
        record(results, ok, "Phase 4 completion module syntax valid", detail)

    summary = None
    if PHASE4_COMPLETION_FILE.exists():
        try:
            module = import_module(PHASE4_COMPLETION_FILE, "phase4_completion_handoff")
            summary = module.build_phase4_completion_summary()
            record(results, isinstance(summary, dict), "Phase 4 completion module imports and builds summary", type(summary).__name__)
        except Exception as exc:
            record(results, False, "Phase 4 completion module imports and builds summary", exc)
            traceback.print_exc()

    if isinstance(summary, dict):
        record(results, summary.get("ready_marker") == "PHASE4_COMPLETION_HANDOFF_READY", "Phase 4 completion has ready marker", summary.get("ready_marker"))
        record(results, summary.get("release_decision") == "PHASE4_COMPLETE_READY_FOR_PHASE5_INTEGRATION_OR_ENGINE_UPGRADE", "Phase 4 completion has release decision", summary.get("release_decision"))
        record(results, summary.get("dashboard_change_required") is False, "Phase 4 completion confirms no dashboard change", summary.get("dashboard_change_required"))
        record(results, summary.get("overall_status") == "PASS", "Phase 4 completion overall status is PASS", summary.get("overall_status"))
        record(results, summary.get("phase4_completed") is True, "Phase 4 completed flag is true", summary.get("phase4_completed"))
        record(results, summary.get("source_mode") == "phase4_completion_handoff", "Phase 4 source mode correct", summary.get("source_mode"))

    for label, path in EXPECTED_OUTPUTS.items():
        record(results, path.exists(), f"Output written: {label}", path)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / "phase4_completion_handoff_checkpoint_report.txt"
    json_path = REPORTS_DIR / "phase4_completion_handoff_checkpoint.json"

    overall_pass = all(item["status"] == "PASS" for item in results)
    final_status = "PASS" if overall_pass else "FAIL"

    lines = [
        "Phase 4 completion handoff checkpoint report",
        "=" * 100,
        f"Overall status: {final_status}",
        "",
    ]
    for item in results:
        lines.append(f"{item['status']:<10} {item['label']:<70} {item['detail']}")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    json_path.write_text(json.dumps({"overall_status": final_status, "results": results}, indent=2), encoding="utf-8")

    print("\n" + "=" * 100)
    print(f"Overall Phase 4 completion checkpoint status: {final_status}")
    print("=" * 100)
    print(f"Saved checkpoint report: {report_path}")
    print(f"Saved checkpoint JSON:   {json_path}")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
