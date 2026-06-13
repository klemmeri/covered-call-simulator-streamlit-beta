"""
Phase 5-13 simulator engine integration candidate check.
"""

from __future__ import annotations

import importlib.util
import json
import traceback
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
DASHBOARD_FILE = APP_DIR / "paid_simulator" / "config_form_app.py"
PHASE5_13_FILE = APP_DIR / "paid_simulator" / "phase5_simulator_engine_integration_candidate.py"
CANDIDATE_FILE = APP_DIR / "simulator_phase5_13_candidate.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase5_13_simulator_engine_integration_candidate.md"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

EXPECTED_READY = "PHASE5_13_SIMULATOR_ENGINE_INTEGRATION_CANDIDATE_READY"
EXPECTED_DECISION = "PHASE5_13_SIMULATOR_ENGINE_CANDIDATE_CREATED_NO_LIVE_ENGINE_REPLACEMENT_NO_DASHBOARD_CHANGE"


def _check(results: list[dict[str, Any]], label: str, condition: bool, detail: Any = "") -> None:
    status = "PASS" if condition else "FAIL"
    print(f"{status:<10} {label:<70} {detail}")
    results.append({"status": status, "label": label, "detail": str(detail)})


def _syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
        return True, "syntax valid"
    except Exception as exc:
        return False, str(exc)


def _import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    print("=" * 100)
    print("Phase 5-13 simulator engine integration candidate check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}\n")

    results: list[dict[str, Any]] = []
    summary: dict[str, Any] | None = None

    _check(results, "Dashboard file exists", DASHBOARD_FILE.exists(), DASHBOARD_FILE)
    _check(results, "Phase 5-13 checkpoint module exists", PHASE5_13_FILE.exists(), PHASE5_13_FILE)
    _check(results, "Phase 5-13 simulator candidate exists", CANDIDATE_FILE.exists(), CANDIDATE_FILE)
    _check(results, "Phase 5-13 documentation exists", DOC_FILE.exists(), DOC_FILE)

    for label, path in [
        ("Dashboard syntax remains valid", DASHBOARD_FILE),
        ("Phase 5-13 module syntax valid", PHASE5_13_FILE),
        ("Phase 5-13 candidate syntax valid", CANDIDATE_FILE),
    ]:
        if path.exists():
            ok, detail = _syntax_valid(path)
            _check(results, label, ok, detail)
        else:
            _check(results, label, False, "missing file")

    try:
        module = _import_module(PHASE5_13_FILE, "phase5_simulator_engine_integration_candidate")
        summary = module.build_phase5_13_summary()
        _check(results, "Phase 5-13 module imports and builds summary", isinstance(summary, dict), type(summary).__name__)
    except Exception as exc:
        _check(results, "Phase 5-13 module imports and builds summary", False, exc)
        traceback.print_exc()

    s = summary or {}
    _check(results, "Candidate has ready marker", s.get("ready_marker") == EXPECTED_READY, s.get("ready_marker"))
    _check(results, "Candidate has release decision", s.get("release_decision") == EXPECTED_DECISION, s.get("release_decision"))
    _check(results, "Candidate confirms no dashboard change", s.get("dashboard_change_required") is False, s.get("dashboard_change_required"))
    _check(results, "Candidate confirms no customer workflow change", s.get("customer_workflow_changed") is False, s.get("customer_workflow_changed"))
    _check(results, "Live simulator was not replaced", s.get("live_simulator_replaced") is False, s.get("live_simulator_replaced"))
    _check(results, "Simulation engine candidate created", s.get("simulation_engine_candidate_created") is True, s.get("simulation_engine_candidate_created"))
    _check(results, "Synthetic default preserved", s.get("synthetic_default_preserved") is True, s.get("synthetic_default_preserved"))
    _check(results, "Historical mode remains explicit only", s.get("historical_mode_explicit_only") is True, s.get("historical_mode_explicit_only"))
    _check(results, "Unknown mode falls back to synthetic", s.get("unknown_mode_falls_back_to_synthetic") is True, s.get("unknown_mode_selected"))
    _check(results, "Synthetic candidate produced rows", (s.get("synthetic_candidate_rows") or 0) >= 1, s.get("synthetic_candidate_rows"))
    _check(results, "Historical candidate produced rows", (s.get("historical_candidate_rows") or 0) >= 1, s.get("historical_candidate_rows"))
    _check(results, "Candidate test rows created", (s.get("candidate_test_rows") or 0) >= 3, s.get("candidate_test_rows"))
    _check(results, "Synthetic start price is positive", s.get("start_price_positive") is True, s.get("start_price_positive"))
    _check(results, "Historical start price is positive", s.get("historical_start_price_positive") is True, s.get("historical_start_price_positive"))
    _check(results, "Overall status is PASS", s.get("overall_status") == "PASS", s.get("overall_status"))

    outputs = s.get("outputs", {}) if isinstance(s.get("outputs", {}), dict) else {}
    for key in ["rows_csv", "summary_csv", "json", "report"]:
        out_path = Path(outputs.get(key, "")) if outputs.get(key) else None
        _check(results, f"Output written: {key}", bool(out_path and out_path.exists()), out_path or "")

    overall_pass = all(item["status"] == "PASS" for item in results)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    checkpoint_report = REPORT_DIR / "phase5_13_simulator_engine_integration_candidate_checkpoint_report.txt"
    checkpoint_json = REPORT_DIR / "phase5_13_simulator_engine_integration_candidate_checkpoint.json"

    lines = ["Phase 5-13 simulator engine integration candidate checkpoint", ""]
    lines.extend(f"{item['status']:<10} {item['label']:<70} {item['detail']}" for item in results)
    lines.append("")
    lines.append(f"Overall Phase 5-13 checkpoint status: {'PASS' if overall_pass else 'FAIL'}")
    checkpoint_report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    checkpoint_json.write_text(json.dumps({"overall_status": "PASS" if overall_pass else "FAIL", "checks": results}, indent=2), encoding="utf-8")

    print("\n" + "=" * 100)
    print(f"Overall Phase 5-13 checkpoint status: {'PASS' if overall_pass else 'FAIL'}")
    print("=" * 100)
    print(f"Saved checkpoint report: {checkpoint_report}")
    print(f"Saved checkpoint JSON:   {checkpoint_json}")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
