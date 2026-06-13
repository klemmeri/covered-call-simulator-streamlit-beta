"""
run_paid_simulator_phase6_2_dashboard_mode_selector_candidate_check.py

Checkpoint check for Phase 6-2 of the Covered Call Simulator paid simulator.
"""

from __future__ import annotations

import importlib.util
import json
import py_compile
import traceback
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
PHASE6_1_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase6_dashboard_integration_readiness.py"
PHASE6_2_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase6_dashboard_mode_selector_candidate.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase6_2_dashboard_mode_selector_candidate.md"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CHECK_REPORT = OUTPUT_REPORT_DIR / "phase6_2_dashboard_mode_selector_candidate_checkpoint_report.txt"
CHECK_JSON = OUTPUT_REPORT_DIR / "phase6_2_dashboard_mode_selector_candidate_checkpoint.json"

EXPECTED_OUTPUTS = {
    "modes_csv": OUTPUT_TABLE_DIR / "phase6_2_dashboard_mode_selector_modes.csv",
    "guardrails_csv": OUTPUT_TABLE_DIR / "phase6_2_dashboard_mode_selector_guardrails.csv",
    "customer_copy_csv": OUTPUT_TABLE_DIR / "phase6_2_dashboard_mode_selector_customer_copy.csv",
    "summary_csv": OUTPUT_TABLE_DIR / "phase6_2_dashboard_mode_selector_candidate_summary.csv",
    "json": OUTPUT_REPORT_DIR / "phase6_2_dashboard_mode_selector_candidate.json",
    "report": OUTPUT_REPORT_DIR / "phase6_2_dashboard_mode_selector_candidate_report.txt",
}


def _record(results: list[dict[str, Any]], passed: bool, label: str, detail: Any = "") -> None:
    status = "PASS" if passed else "FAIL"
    results.append({"status": status, "label": label, "detail": str(detail)})
    print(f"{status:<10} {label:<70} {detail}")


def _compile(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "syntax valid"
    except Exception as exc:
        return False, str(exc)


def _import_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    print("=" * 100)
    print("Phase 6-2 dashboard mode selector candidate check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    summary: dict[str, Any] | None = None

    _record(results, DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    _record(results, PHASE6_1_FILE.exists(), "Prior Phase 6-1 readiness module exists", PHASE6_1_FILE)
    _record(results, PHASE6_2_FILE.exists(), "Phase 6-2 mode selector candidate module exists", PHASE6_2_FILE)
    _record(results, DOC_FILE.exists(), "Phase 6-2 documentation exists", DOC_FILE)

    if DASHBOARD_FILE.exists():
        ok, detail = _compile(DASHBOARD_FILE)
        _record(results, ok, "Dashboard syntax remains valid", detail)

    if PHASE6_2_FILE.exists():
        ok, detail = _compile(PHASE6_2_FILE)
        _record(results, ok, "Phase 6-2 module syntax valid", detail)
        if ok:
            try:
                module = _import_module(PHASE6_2_FILE, "phase6_dashboard_mode_selector_candidate")
                summary = module.build_phase6_2_summary()
                _record(results, isinstance(summary, dict), "Phase 6-2 module imports and builds selector candidate", type(summary).__name__)
            except Exception as exc:
                _record(results, False, "Phase 6-2 module imports and builds selector candidate", exc)
                traceback.print_exc()

    if isinstance(summary, dict):
        _record(results, summary.get("ready_marker") == "PHASE6_2_DASHBOARD_MODE_SELECTOR_CANDIDATE_READY", "Mode selector has ready marker", summary.get("ready_marker"))
        _record(results, summary.get("release_decision") == "PHASE6_2_DASHBOARD_MODE_SELECTOR_CANDIDATE_CREATED_NO_DASHBOARD_CHANGE", "Mode selector has release decision", summary.get("release_decision"))
        _record(results, summary.get("dashboard_changed") is False, "Mode selector confirms no dashboard change", summary.get("dashboard_changed"))
        _record(results, summary.get("source_mode") == "dashboard_mode_selector_candidate", "Mode selector uses expected source mode", summary.get("source_mode"))
        _record(results, summary.get("default_mode") == "synthetic", "Synthetic mode remains dashboard default", summary.get("default_mode"))
        _record(results, summary.get("synthetic_default_preserved") is True, "Synthetic default preserved flag true", summary.get("synthetic_default_preserved"))
        _record(results, summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
        _record(results, summary.get("unknown_mode_falls_back_to_synthetic") is True, "Unknown mode falls back to synthetic", summary.get("unknown_mode_falls_back_to_synthetic"))
        _record(results, summary.get("mode_selector_candidate_created") is True, "Mode selector candidate created", summary.get("mode_selector_candidate_created"))
        _record(results, (summary.get("mode_definition_rows") or 0) >= 2, "Mode definitions have rows", summary.get("mode_definition_rows"))
        _record(results, (summary.get("guardrail_rows") or 0) >= 4, "Guardrails have rows", summary.get("guardrail_rows"))
        _record(results, (summary.get("customer_copy_rows") or 0) >= 2, "Customer copy has rows", summary.get("customer_copy_rows"))
        _record(results, summary.get("overall_status") == "PASS", "Mode selector overall status is PASS", summary.get("overall_status"))
    else:
        _record(results, False, "Mode selector summary produced", "summary was not a dict")

    for label, path in EXPECTED_OUTPUTS.items():
        _record(results, path.exists(), f"Output written: {label}", path)

    modes_path = EXPECTED_OUTPUTS["modes_csv"]
    if modes_path.exists():
        try:
            modes_df = pd.read_csv(modes_path)
            has_modes = {"synthetic", "historical_import"}.issubset(set(modes_df.get("mode_key", [])))
            _record(results, has_modes, "Mode CSV includes synthetic and historical_import", f"rows={len(modes_df)}")
        except Exception as exc:
            _record(results, False, "Mode CSV includes synthetic and historical_import", exc)

    overall_pass = all(item["status"] == "PASS" for item in results)
    print()
    print("=" * 100)
    print(f"Overall Phase 6-2 checkpoint status: {'PASS' if overall_pass else 'FAIL'}")
    print("=" * 100)

    CHECK_REPORT.write_text(
        "\n".join([f"{item['status']:<10} {item['label']:<70} {item['detail']}" for item in results])
        + f"\n\nOverall Phase 6-2 checkpoint status: {'PASS' if overall_pass else 'FAIL'}\n",
        encoding="utf-8",
    )
    CHECK_JSON.write_text(json.dumps({"overall_status": "PASS" if overall_pass else "FAIL", "results": results}, indent=2), encoding="utf-8")
    print(f"Saved checkpoint report: {CHECK_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECK_JSON}")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
