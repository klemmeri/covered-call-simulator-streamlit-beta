"""
run_paid_simulator_phase5_7_synthetic_default_regression_guard_check.py

Checkpoint runner for Phase 5-7 synthetic-default regression guard.
"""

from __future__ import annotations

import importlib.util
import json
import py_compile
import sys
import traceback
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
PHASE5_7_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase5_synthetic_default_regression_guard.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase5_7_synthetic_default_regression_guard.md"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CHECKPOINT_REPORT = REPORT_DIR / "phase5_7_synthetic_default_regression_guard_checkpoint_report.txt"
CHECKPOINT_JSON = REPORT_DIR / "phase5_7_synthetic_default_regression_guard_checkpoint.json"


def _print_header() -> None:
    print("=" * 100)
    print("Phase 5-7 synthetic-default regression guard check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()


def _check(results: list[dict[str, Any]], label: str, passed: bool, detail: Any = "") -> None:
    status = "PASS" if passed else "FAIL"
    print(f"{status:<10} {label:<70} {detail}")
    results.append({"status": status, "label": label, "detail": str(detail)})


def _compile(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "syntax valid"
    except Exception as exc:
        return False, str(exc)


def _import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to create import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    _print_header()
    results: list[dict[str, Any]] = []
    summary: dict[str, Any] | None = None

    _check(results, "Dashboard file exists", DASHBOARD_FILE.exists(), DASHBOARD_FILE)
    _check(results, "Phase 5-7 regression guard module exists", PHASE5_7_FILE.exists(), PHASE5_7_FILE)
    _check(results, "Phase 5-7 documentation exists", DOC_FILE.exists(), DOC_FILE)

    if DASHBOARD_FILE.exists():
        passed, detail = _compile(DASHBOARD_FILE)
        _check(results, "Dashboard syntax remains valid", passed, detail)

    if PHASE5_7_FILE.exists():
        passed, detail = _compile(PHASE5_7_FILE)
        _check(results, "Phase 5-7 module syntax valid", passed, detail)
        if passed:
            try:
                module = _import_module(PHASE5_7_FILE, "phase5_synthetic_default_regression_guard")
                summary = module.build_phase5_7_summary()
                _check(results, "Phase 5-7 module imports and builds guard", isinstance(summary, dict), type(summary).__name__)
            except Exception as exc:
                _check(results, "Phase 5-7 module imports and builds guard", False, exc)
                traceback.print_exc()

    if isinstance(summary, dict):
        _check(results, "Regression guard has ready marker", summary.get("ready_marker") == "PHASE5_7_SYNTHETIC_DEFAULT_REGRESSION_GUARD_READY", summary.get("ready_marker"))
        _check(results, "Regression guard has release decision", summary.get("release_decision") == "PHASE5_7_SYNTHETIC_DEFAULT_REGRESSION_GUARD_CREATED_NO_ENGINE_PATCH_NO_DASHBOARD_CHANGE", summary.get("release_decision"))
        _check(results, "Regression guard confirms no dashboard change", summary.get("dashboard_change_required") is False, summary.get("dashboard_change_required"))
        _check(results, "Regression guard confirms no engine patch", summary.get("engine_patch_applied") is False, summary.get("engine_patch_applied"))
        _check(results, "Regression guard uses expected mode", summary.get("source_mode") == "synthetic_default_regression_guard", summary.get("source_mode"))
        _check(results, "Synthetic default remains preserved", summary.get("synthetic_default_preserved") is True, summary.get("synthetic_default_preserved"))
        _check(results, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only") is True, summary.get("historical_mode_explicit_only"))
        _check(results, "Historical import is not default-enabled", summary.get("historical_import_default_enabled") is False, summary.get("historical_import_default_enabled"))
        _check(results, "Regression guard was created", summary.get("regression_guard_created") is True, summary.get("regression_guard_created"))
        _check(results, "Core engine files are inventoried", int(summary.get("engine_file_count", 0)) >= 5, summary.get("engine_file_count"))
        _check(results, "Regression guards are inventoried", int(summary.get("guard_count", 0)) >= 5, summary.get("guard_count"))
        _check(results, "All regression guards pass", summary.get("guard_count") == summary.get("passing_guard_count"), f"{summary.get('passing_guard_count')}/{summary.get('guard_count')}")
        _check(results, "Regression guard overall status is PASS", summary.get("overall_status") == "PASS", summary.get("overall_status"))

        outputs = summary.get("outputs", {})
        for key in ["engine_status_csv", "prior_artifact_csv", "guard_csv", "summary_csv", "json", "report"]:
            path = Path(outputs.get(key, ""))
            _check(results, f"Output written: {key}", path.exists() and path.stat().st_size > 0, path)

        guard_csv = Path(outputs.get("guard_csv", ""))
        if guard_csv.exists():
            df = pd.read_csv(guard_csv)
            _check(results, "Regression guard CSV has expected content", len(df) >= 5, f"rows={len(df)}")

    overall_pass = all(row["status"] == "PASS" for row in results)
    print()
    print("=" * 100)
    print(f"Overall Phase 5-7 checkpoint status: {'PASS' if overall_pass else 'FAIL'}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join(f"{row['status']:<10} {row['label']:<70} {row['detail']}" for row in results)
        + f"\n\nOverall Phase 5-7 checkpoint status: {'PASS' if overall_pass else 'FAIL'}\n",
        encoding="utf-8",
    )
    CHECKPOINT_JSON.write_text(json.dumps({"overall_pass": overall_pass, "results": results}, indent=2), encoding="utf-8")
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
