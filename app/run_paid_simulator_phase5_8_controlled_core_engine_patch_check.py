"""
Checkpoint runner for Phase 5-8 controlled core-engine patch.
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
PHASE5_8_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase5_controlled_core_engine_patch.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase5_8_controlled_core_engine_patch.md"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CHECKPOINT_REPORT = REPORT_DIR / "phase5_8_controlled_core_engine_patch_checkpoint_report.txt"
CHECKPOINT_JSON = REPORT_DIR / "phase5_8_controlled_core_engine_patch_checkpoint.json"


def _status_line(status: str, label: str, detail: Any = "") -> str:
    return f"{status:<10} {label:<70} {detail}"


def _record(results: list[dict[str, Any]], passed: bool, label: str, detail: Any = "") -> None:
    results.append({"passed": bool(passed), "label": label, "detail": str(detail)})
    print(_status_line("PASS" if passed else "FAIL", label, detail))


def _compile(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "syntax valid"
    except Exception as exc:
        return False, str(exc)


def _import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    summary: dict[str, Any] | None = None

    print("=" * 100)
    print("Phase 5-8 controlled core-engine patch check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    _record(results, DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    _record(results, PHASE5_8_FILE.exists(), "Phase 5-8 controlled core-engine patch module exists", PHASE5_8_FILE)
    _record(results, DOC_FILE.exists(), "Phase 5-8 documentation exists", DOC_FILE)

    if DASHBOARD_FILE.exists():
        ok, detail = _compile(DASHBOARD_FILE)
        _record(results, ok, "Dashboard syntax remains valid", detail)
    else:
        _record(results, False, "Dashboard syntax remains valid", "dashboard file missing")

    if PHASE5_8_FILE.exists():
        ok, detail = _compile(PHASE5_8_FILE)
        _record(results, ok, "Phase 5-8 module syntax valid", detail)
    else:
        _record(results, False, "Phase 5-8 module syntax valid", "module missing")

    try:
        module = _import_module(PHASE5_8_FILE, "phase5_controlled_core_engine_patch")
        summary = module.build_phase5_8_summary()
        _record(results, isinstance(summary, dict), "Phase 5-8 module imports and builds patch contract", type(summary).__name__)
    except Exception as exc:
        _record(results, False, "Phase 5-8 module imports and builds patch contract", exc)
        traceback.print_exc()

    if not isinstance(summary, dict):
        summary = {}

    _record(results, summary.get("ready_marker") == "PHASE5_8_CONTROLLED_CORE_ENGINE_PATCH_READY", "Core-engine patch has ready marker", summary.get("ready_marker"))
    _record(results, summary.get("release_decision") == "PHASE5_8_CONTROLLED_CORE_ENGINE_PATCH_CREATED_SYNTHETIC_DEFAULT_PROTECTED", "Core-engine patch has release decision", summary.get("release_decision"))
    _record(results, summary.get("dashboard_change_required") is False, "Core-engine patch confirms no dashboard change", summary.get("dashboard_change_required"))
    _record(results, summary.get("source_mode") == "controlled_core_engine_patch", "Core-engine patch uses controlled patch mode", summary.get("source_mode"))
    _record(results, summary.get("default_engine_mode") == "synthetic", "Synthetic remains default engine mode", summary.get("default_engine_mode"))
    _record(results, summary.get("synthetic_default_preserved") is True, "Synthetic default preserved", summary.get("synthetic_default_preserved"))
    _record(results, summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
    _record(results, summary.get("core_engine_files_replaced") is False, "No core engine files replaced yet", summary.get("core_engine_files_replaced"))
    _record(results, summary.get("safe_patch_contract_created") is True, "Safe patch contract created", summary.get("safe_patch_contract_created"))
    _record(results, int(summary.get("patch_contract_rows") or 0) >= 5, "Patch contract has rows", summary.get("patch_contract_rows"))
    _record(results, int(summary.get("mode_matrix_rows") or 0) >= 2, "Engine mode matrix has rows", summary.get("mode_matrix_rows"))
    _record(results, int(summary.get("historical_engine_ready_path_rows") or 0) >= 1, "Historical engine-ready path has rows", summary.get("historical_engine_ready_path_rows"))
    _record(results, int(summary.get("positive_price_rows") or 0) >= 1, "Historical engine-ready path has positive prices", summary.get("positive_price_rows"))

    outputs = summary.get("outputs", {}) if isinstance(summary.get("outputs"), dict) else {}
    for key in ["patch_contract_csv", "engine_mode_matrix_csv", "patch_preview_csv", "summary_csv", "json", "report"]:
        p = Path(outputs.get(key, ""))
        _record(results, p.exists(), f"Output written: {key}", p)

    contract_csv = Path(outputs.get("patch_contract_csv", ""))
    if contract_csv.exists():
        try:
            df = pd.read_csv(contract_csv)
            _record(results, len(df) >= 5, "Patch contract CSV has expected content", f"rows={len(df)}")
        except Exception as exc:
            _record(results, False, "Patch contract CSV has expected content", exc)
    else:
        _record(results, False, "Patch contract CSV has expected content", "missing")

    overall_pass = all(item["passed"] for item in results)
    print()
    print("=" * 100)
    print(f"Overall Phase 5-8 checkpoint status: {'PASS' if overall_pass else 'FAIL'}")
    print("=" * 100)

    report_lines = [
        "Phase 5-8 controlled core-engine patch checkpoint report",
        "=" * 100,
        f"Project root: {PROJECT_ROOT}",
        "",
    ]
    report_lines.extend(_status_line("PASS" if r["passed"] else "FAIL", r["label"], r["detail"]) for r in results)
    report_lines.extend(["", f"Overall Phase 5-8 checkpoint status: {'PASS' if overall_pass else 'FAIL'}", ""])
    CHECKPOINT_REPORT.write_text("\n".join(report_lines), encoding="utf-8")
    CHECKPOINT_JSON.write_text(json.dumps({"passed": overall_pass, "results": results}, indent=2), encoding="utf-8")
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
