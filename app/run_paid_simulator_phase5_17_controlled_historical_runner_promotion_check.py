"""
run_paid_simulator_phase5_17_controlled_historical_runner_promotion_check.py

Checkpoint script for Phase 5-17 of the Covered Call Simulator.
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
PHASE5_16_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase5_historical_import_engine_runner_candidate.py"
PHASE5_17_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase5_controlled_historical_runner_promotion.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase5_17_controlled_historical_runner_promotion.md"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CHECKPOINT_REPORT = REPORT_DIR / "phase5_17_controlled_historical_runner_promotion_checkpoint_report.txt"
CHECKPOINT_JSON = REPORT_DIR / "phase5_17_controlled_historical_runner_promotion_checkpoint.json"

EXPECTED_OUTPUTS = {
    "promotion_contract_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase5_17_promoted_historical_runner_contract.csv",
    "promoted_path_preview_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase5_17_promoted_historical_runner_path_preview.csv",
    "summary_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase5_17_controlled_historical_runner_promotion_summary.csv",
    "json_report": PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase5_17_controlled_historical_runner_promotion.json",
    "text_report": PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase5_17_controlled_historical_runner_promotion_report.txt",
}


def _import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _record(results: list[dict[str, Any]], passed: bool, label: str, detail: Any = "") -> None:
    status = "PASS" if passed else "FAIL"
    print(f"{status:<10} {label:<70} {detail}")
    results.append({"status": status, "label": label, "detail": str(detail)})


def _positive(value: Any) -> bool:
    try:
        return float(value) > 0
    except Exception:
        return False


def main() -> int:
    print("=" * 100)
    print("Phase 5-17 controlled historical runner promotion check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    results: list[dict[str, Any]] = []
    summary: dict[str, Any] | None = None

    _record(results, DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    _record(results, PHASE5_16_FILE.exists(), "Prior Phase 5-16 runner candidate module exists", PHASE5_16_FILE)
    _record(results, PHASE5_17_FILE.exists(), "Phase 5-17 promotion module exists", PHASE5_17_FILE)
    _record(results, DOC_FILE.exists(), "Phase 5-17 documentation exists", DOC_FILE)

    try:
        py_compile.compile(str(DASHBOARD_FILE), doraise=True)
        _record(results, True, "Dashboard syntax remains valid", "syntax valid")
    except Exception as exc:
        _record(results, False, "Dashboard syntax remains valid", exc)

    try:
        py_compile.compile(str(PHASE5_17_FILE), doraise=True)
        _record(results, True, "Phase 5-17 module syntax valid", "syntax valid")
    except Exception as exc:
        _record(results, False, "Phase 5-17 module syntax valid", exc)

    try:
        module = _import_module(PHASE5_17_FILE, "phase5_controlled_historical_runner_promotion")
        summary = module.build_phase5_17_summary()
        _record(results, isinstance(summary, dict), "Phase 5-17 module imports and builds promotion", type(summary).__name__)
    except Exception as exc:
        _record(results, False, "Phase 5-17 module imports and builds promotion", exc)
        print(traceback.format_exc())

    summary = summary or {}
    _record(results, summary.get("ready_marker") == "PHASE5_17_CONTROLLED_HISTORICAL_RUNNER_PROMOTION_READY", "Promotion has ready marker", summary.get("ready_marker"))
    _record(results, summary.get("release_decision") == "PHASE5_17_CONTROLLED_HISTORICAL_RUNNER_PROMOTED_NO_DASHBOARD_CHANGE", "Promotion has release decision", summary.get("release_decision"))
    _record(results, summary.get("dashboard_change_required") is False, "Promotion confirms no dashboard change", summary.get("dashboard_change_required"))
    _record(results, summary.get("source_mode") == "controlled_historical_runner_promotion", "Promotion uses expected source mode", summary.get("source_mode"))
    _record(results, summary.get("requested_mode") == "historical_import", "Promotion requested historical import", summary.get("requested_mode"))
    _record(results, summary.get("selected_mode") == "historical_import", "Promotion selected historical import", summary.get("selected_mode"))
    _record(results, summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
    _record(results, summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    _record(results, summary.get("controlled_runner_promoted") is True, "Controlled runner promoted", summary.get("controlled_runner_promoted"))
    _record(results, summary.get("engine_runner_candidate_promoted") is True, "Engine-runner candidate promoted", summary.get("engine_runner_candidate_promoted"))
    _record(results, summary.get("live_core_engine_replaced") is False, "No additional live core engine replacement", summary.get("live_core_engine_replaced"))
    _record(results, int(summary.get("historical_path_rows") or 0) >= 1, "Historical path has rows", summary.get("historical_path_rows"))
    _record(results, int(summary.get("runner_contract_rows") or 0) >= 1, "Promoted runner contract has rows", summary.get("runner_contract_rows"))
    _record(results, _positive(summary.get("start_price")), "Start price is positive", summary.get("start_price"))
    _record(results, _positive(summary.get("end_price")), "End price is positive", summary.get("end_price"))
    _record(results, summary.get("overall_status") == "PASS", "Promotion overall status is PASS", summary.get("overall_status"))

    for label, path in EXPECTED_OUTPUTS.items():
        _record(results, path.exists() and path.stat().st_size > 0, f"Output written: {label}", path)

    contract_path = EXPECTED_OUTPUTS["promotion_contract_csv"]
    if contract_path.exists():
        try:
            contract_df = pd.read_csv(contract_path)
            _record(results, len(contract_df) >= 1, "Promoted contract CSV has expected content", f"rows={len(contract_df)}")
        except Exception as exc:
            _record(results, False, "Promoted contract CSV has expected content", exc)
    else:
        _record(results, False, "Promoted contract CSV has expected content", "missing")

    passed = all(row["status"] == "PASS" for row in results)
    overall = "PASS" if passed else "FAIL"

    print()
    print("=" * 100)
    print(f"Overall Phase 5-17 checkpoint status: {overall}")
    print("=" * 100)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_REPORT.write_text(_format_checkpoint_report(results, overall), encoding="utf-8")
    CHECKPOINT_JSON.write_text(json.dumps({"overall_status": overall, "results": results}, indent=2), encoding="utf-8")
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if passed else 1


def _format_checkpoint_report(results: list[dict[str, Any]], overall: str) -> str:
    lines = [
        "Phase 5-17 controlled historical runner promotion checkpoint report",
        "=" * 80,
        f"Overall status: {overall}",
        "",
    ]
    for row in results:
        lines.append(f"{row['status']:<8} {row['label']} -- {row['detail']}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
