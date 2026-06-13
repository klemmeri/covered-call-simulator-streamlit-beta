"""
run_paid_simulator_phase5_14_simulator_promotion_check.py

Checkpoint script for Phase 5-14 simulator candidate promotion.
"""

from __future__ import annotations

import importlib.util
import json
import py_compile
import traceback
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
MODULE_FILE = APP_DIR / "paid_simulator" / "phase5_simulator_candidate_promotion.py"
DASHBOARD_FILE = APP_DIR / "paid_simulator" / "config_form_app.py"
LIVE_SIMULATOR_FILE = APP_DIR / "simulator.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase5_14_simulator_candidate_promotion.md"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CHECK_REPORT = REPORT_DIR / "phase5_14_simulator_candidate_promotion_checkpoint_report.txt"
CHECK_JSON = REPORT_DIR / "phase5_14_simulator_candidate_promotion_checkpoint.json"

EXPECTED_READY = "PHASE5_14_SIMULATOR_CANDIDATE_PROMOTION_READY"
EXPECTED_RELEASE = "PHASE5_14_SIMULATOR_PROMOTED_SYNTHETIC_DEFAULT_PROTECTED_NO_DASHBOARD_CHANGE"


def _line(label: str, status: bool, detail: object = "") -> tuple[bool, str]:
    word = "PASS" if status else "FAIL"
    return status, f"{word:<10} {label:<70} {detail}"


def _compile(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
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


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[tuple[bool, str]] = []
    summary = None

    rows.append(_line("Dashboard file exists", DASHBOARD_FILE.exists(), DASHBOARD_FILE))
    rows.append(_line("Live simulator file exists", LIVE_SIMULATOR_FILE.exists(), LIVE_SIMULATOR_FILE))
    rows.append(_line("Phase 5-14 promotion module exists", MODULE_FILE.exists(), MODULE_FILE))
    rows.append(_line("Phase 5-14 documentation exists", DOC_FILE.exists(), DOC_FILE))

    if DASHBOARD_FILE.exists():
        ok, detail = _compile(DASHBOARD_FILE)
        rows.append(_line("Dashboard syntax remains valid", ok, detail))
    else:
        rows.append(_line("Dashboard syntax remains valid", False, "missing dashboard file"))

    if LIVE_SIMULATOR_FILE.exists():
        ok, detail = _compile(LIVE_SIMULATOR_FILE)
        rows.append(_line("Live simulator syntax valid", ok, detail))
    else:
        rows.append(_line("Live simulator syntax valid", False, "missing live simulator file"))

    if MODULE_FILE.exists():
        ok, detail = _compile(MODULE_FILE)
        rows.append(_line("Phase 5-14 module syntax valid", ok, detail))
    else:
        rows.append(_line("Phase 5-14 module syntax valid", False, "missing module"))

    try:
        module = _import_module(MODULE_FILE, "phase5_simulator_candidate_promotion")
        summary = module.build_phase5_14_summary()
        rows.append(_line("Phase 5-14 module imports and builds promotion summary", isinstance(summary, dict), type(summary).__name__))
    except Exception as exc:
        rows.append(_line("Phase 5-14 module imports and builds promotion summary", False, exc))
        rows.append((False, traceback.format_exc()))
        summary = {}

    rows.append(_line("Promotion has ready marker", summary.get("ready_marker") == EXPECTED_READY, summary.get("ready_marker")))
    rows.append(_line("Promotion has release decision", summary.get("release_decision") == EXPECTED_RELEASE, summary.get("release_decision")))
    rows.append(_line("Promotion confirms no dashboard change", summary.get("dashboard_change_required") is False, summary.get("dashboard_change_required")))
    rows.append(_line("Promotion uses simulator promotion mode", summary.get("source_mode") == "simulator_candidate_promotion", summary.get("source_mode")))
    rows.append(_line("Synthetic default remains preserved", summary.get("synthetic_default_preserved") is True, summary.get("synthetic_default_preserved")))
    rows.append(_line("Historical mode remains explicit only", summary.get("historical_mode_explicit_only") is True, summary.get("historical_mode_explicit_only")))
    rows.append(_line("Unknown modes remain safe", summary.get("unknown_modes_safe") is True, summary.get("unknown_modes_safe")))
    rows.append(_line("Live simulator promoted", summary.get("live_simulator_promoted") is True, summary.get("live_simulator_promoted")))
    rows.append(_line("SimulationEngine remains present", summary.get("simulation_engine_present") is True, summary.get("simulation_engine_present")))
    rows.append(_line("run method remains present", summary.get("run_method_present") is True, summary.get("run_method_present")))
    rows.append(_line("Price-path function remains present", summary.get("price_path_function_present") is True, summary.get("price_path_function_present")))
    rows.append(_line("Only simulator core file is marked replaced", summary.get("core_file_replaced") is True, summary.get("replaced_core_file")))
    rows.append(_line("Customer workflow unchanged", summary.get("customer_workflow_changed") is False, summary.get("customer_workflow_changed")))
    rows.append(_line("Contract rows present", (summary.get("contract_rows") or 0) >= 5, summary.get("contract_rows")))

    for key in ["file_status_csv", "contract_csv", "summary_csv", "json_report", "text_report"]:
        path = Path(str(summary.get(key, ""))) if summary.get(key) else None
        rows.append(_line(f"Output written: {key}", bool(path and path.exists()), path or ""))

    overall = all(status for status, _ in rows)
    banner = "=" * 100
    output_lines = [
        banner,
        "Phase 5-14 simulator candidate promotion check",
        banner,
        f"Project root: {PROJECT_ROOT}",
        "",
        *[line for _, line in rows],
        "",
        banner,
        f"Overall Phase 5-14 checkpoint status: {'PASS' if overall else 'FAIL'}",
        banner,
    ]

    CHECK_REPORT.write_text("\n".join(output_lines), encoding="utf-8")
    CHECK_JSON.write_text(json.dumps({"overall_pass": overall, "summary": summary, "rows": [line for _, line in rows]}, indent=2), encoding="utf-8")

    print("\n".join(output_lines))
    print(f"Saved checkpoint report: {CHECK_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECK_JSON}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
