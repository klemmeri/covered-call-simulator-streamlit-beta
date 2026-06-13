"""
Phase 5-19 engine-level option-premium integration plan checkpoint check.
"""

from __future__ import annotations

import importlib.util
import json
import py_compile
import sys
import traceback
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase5_engine_option_premium_integration_plan.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase5_19_engine_option_premium_integration_plan.md"
CHECKPOINT_REPORT = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase5_19_engine_option_premium_integration_plan_checkpoint_report.txt"
CHECKPOINT_JSON = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase5_19_engine_option_premium_integration_plan_checkpoint.json"

EXPECTED_OUTPUTS = {
    "summary_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase5_19_engine_option_premium_integration_plan_summary.csv",
    "touchpoints_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase5_19_option_premium_engine_touchpoints.csv",
    "patch_order_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase5_19_option_premium_patch_order.csv",
    "prior_artifacts_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase5_19_prior_option_artifact_status.csv",
    "json": PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase5_19_engine_option_premium_integration_plan.json",
    "report": PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase5_19_engine_option_premium_integration_plan_report.txt",
}


def _status_line(ok: bool, label: str, detail: object = "") -> str:
    status = "PASS" if ok else "FAIL"
    return f"{status:<10} {label:<72} {detail}"


def _import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    results: list[dict[str, object]] = []
    lines: list[str] = []

    def check(label: str, ok: bool, detail: object = "") -> None:
        results.append({"label": label, "ok": bool(ok), "detail": str(detail)})
        lines.append(_status_line(ok, label, detail))

    lines.append("=" * 100)
    lines.append("Phase 5-19 engine-level option-premium integration plan check")
    lines.append("=" * 100)
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append("")

    check("Dashboard file exists", DASHBOARD_FILE.exists(), DASHBOARD_FILE)
    check("Phase 5-19 integration-plan module exists", MODULE_FILE.exists(), MODULE_FILE)
    check("Phase 5-19 documentation exists", DOC_FILE.exists(), DOC_FILE)

    try:
        py_compile.compile(str(DASHBOARD_FILE), doraise=True)
        check("Dashboard syntax remains valid", True, "syntax valid")
    except Exception as exc:
        check("Dashboard syntax remains valid", False, exc)

    try:
        py_compile.compile(str(MODULE_FILE), doraise=True)
        check("Phase 5-19 module syntax valid", True, "syntax valid")
    except Exception as exc:
        check("Phase 5-19 module syntax valid", False, exc)

    summary = None
    try:
        module = _import_module(MODULE_FILE, "phase5_engine_option_premium_integration_plan")
        summary = module.build_phase5_19_summary()
        check("Phase 5-19 module imports and builds integration plan", isinstance(summary, dict), type(summary).__name__)
    except Exception as exc:
        check("Phase 5-19 module imports and builds integration plan", False, exc)
        lines.append(traceback.format_exc())

    if not isinstance(summary, dict):
        summary = {}

    check("Integration plan has ready marker", summary.get("ready_marker") == "PHASE5_19_ENGINE_OPTION_PREMIUM_INTEGRATION_PLAN_READY", summary.get("ready_marker"))
    check("Integration plan has release decision", summary.get("release_decision") == "PHASE5_19_ENGINE_OPTION_PREMIUM_INTEGRATION_PLAN_CREATED_NO_DASHBOARD_CHANGE", summary.get("release_decision"))
    check("Integration plan confirms no dashboard change", summary.get("dashboard_change_required") is False, summary.get("dashboard_change_required"))
    check("Integration plan confirms no core engine patch", summary.get("core_engine_patched") is False, summary.get("core_engine_patched"))
    check("Synthetic default remains preserved", summary.get("synthetic_default_preserved") is True, summary.get("synthetic_default_preserved"))
    check("Historical mode remains explicit only", summary.get("historical_mode_explicit_only") is True, summary.get("historical_mode_explicit_only"))
    check("Option-premium integration plan created", summary.get("option_premium_integration_plan_created") is True, summary.get("option_premium_integration_plan_created"))
    check("Engine touchpoints identified", int(summary.get("engine_touchpoint_rows") or 0) >= 4, summary.get("engine_touchpoint_rows"))
    check("Patch order identified", int(summary.get("recommended_patch_order_rows") or 0) >= 3, summary.get("recommended_patch_order_rows"))
    check("Phase 5 completion is next checkpoint", summary.get("next_recommended_checkpoint") == "PHASE5_20_COMPLETION_HANDOFF", summary.get("next_recommended_checkpoint"))
    check("Integration-plan overall status is PASS", summary.get("overall_status") == "PASS", summary.get("overall_status"))

    for label, path in EXPECTED_OUTPUTS.items():
        check(f"Output written: {label}", path.exists(), path)

    try:
        touchpoints_rows = len(pd.read_csv(EXPECTED_OUTPUTS["touchpoints_csv"]))
        check("Touchpoints CSV has expected content", touchpoints_rows >= 4, f"rows={touchpoints_rows}")
    except Exception as exc:
        check("Touchpoints CSV has expected content", False, exc)

    overall_ok = all(item["ok"] for item in results)
    lines.append("")
    lines.append("=" * 100)
    lines.append(f"Overall Phase 5-19 checkpoint status: {'PASS' if overall_ok else 'FAIL'}")
    lines.append("=" * 100)

    CHECKPOINT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    CHECKPOINT_JSON.write_text(json.dumps({"overall_status": "PASS" if overall_ok else "FAIL", "checks": results}, indent=2), encoding="utf-8")

    print("\n".join(lines))
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")
    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
