"""
run_paid_simulator_phase6_3_dashboard_mode_selector_patch_check.py

Checkpoint check for Phase 6-3: controlled dashboard mode selector patch.

The script appends a conservative integration block to:

    app/paid_simulator/config_form_app.py

only if the Phase 6-3 marker is absent. The appended block is syntax-safe and
provides an optional Streamlit helper without changing synthetic mode as the
default.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import traceback
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_DIR = APP_DIR / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

DASHBOARD_FILE = PAID_DIR / "config_form_app.py"
MODULE_FILE = PAID_DIR / "phase6_dashboard_mode_selector_patch.py"
DOC_FILE = DOCS_DIR / "phase6_3_dashboard_mode_selector_patch.md"
CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase6_3_dashboard_mode_selector_patch_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase6_3_dashboard_mode_selector_patch_checkpoint.json"

PATCH_MARKER = "PHASE6_3_DASHBOARD_MODE_SELECTOR_PATCH_READY"
PATCH_BEGIN = "# PHASE6_3_DASHBOARD_MODE_SELECTOR_PATCH_BEGIN"
PATCH_END = "# PHASE6_3_DASHBOARD_MODE_SELECTOR_PATCH_END"

PATCH_BLOCK = f'''

{PATCH_BEGIN}
# Controlled dashboard data-mode selector support.
# Synthetic scenarios remain the default. Imported historical data remains
# explicit opt-in only and must not be described as a forecast.
PHASE6_3_DASHBOARD_MODE_SELECTOR_PATCH_READY = "{PATCH_MARKER}"


def render_phase6_3_dashboard_mode_selector(default_mode="synthetic"):
    """
    Optional Phase 6-3 dashboard mode selector helper.

    This helper is deliberately guarded. It returns a normalized selection dict
    when Streamlit or the support module is unavailable, so the existing paid
    dashboard remains safe.
    """

    try:
        from phase6_dashboard_mode_selector_patch import (
            render_phase6_3_dashboard_mode_selector as _phase6_3_renderer,
        )
    except Exception:
        try:
            from app.paid_simulator.phase6_dashboard_mode_selector_patch import (
                render_phase6_3_dashboard_mode_selector as _phase6_3_renderer,
            )
        except Exception:
            requested = str(default_mode).strip().lower()
            selected_mode = "historical_import" if requested in {{
                "historical",
                "historical_import",
                "historical import",
                "imported historical data",
            }} else "synthetic"
            return {{
                "selected_mode": selected_mode,
                "selected_label": (
                    "Imported historical data"
                    if selected_mode == "historical_import"
                    else "Synthetic scenarios"
                ),
                "is_default": selected_mode == "synthetic",
                "historical_mode_explicit_only": True,
                "customer_caution_text": (
                    "Historical data mode uses imported past price behavior as "
                    "an input scenario. It should not be interpreted as a "
                    "forecast or regime oracle."
                ),
            }}

    return _phase6_3_renderer(default_mode=default_mode)
{PATCH_END}
'''


def _status_line(status: str, label: str, detail: Any = "") -> str:
    return f"{status:<10} {label:<70} {detail}"


def _record(results: list[dict[str, Any]], passed: bool, label: str, detail: Any = "") -> None:
    status = "PASS" if passed else "FAIL"
    results.append({"status": status, "label": label, "detail": str(detail)})
    print(_status_line(status, label, detail))


def _syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:
        return False, str(exc)


def _import_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _apply_dashboard_patch() -> tuple[bool, str]:
    if not DASHBOARD_FILE.exists():
        return False, "dashboard file missing"

    text = DASHBOARD_FILE.read_text(encoding="utf-8")
    if PATCH_MARKER in text and PATCH_BEGIN in text and PATCH_END in text:
        return True, "patch marker already present"

    DASHBOARD_FILE.write_text(text.rstrip() + PATCH_BLOCK + "\n", encoding="utf-8")
    return True, "patch block appended"


def main() -> int:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 100)
    print("Phase 6-3 controlled dashboard mode selector patch check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    results: list[dict[str, Any]] = []
    summary: dict[str, Any] | None = None

    _record(results, DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    _record(results, MODULE_FILE.exists(), "Phase 6-3 support module exists", MODULE_FILE)
    _record(results, DOC_FILE.exists(), "Phase 6-3 documentation exists", DOC_FILE)

    if DASHBOARD_FILE.exists():
        patch_ok, patch_detail = _apply_dashboard_patch()
        _record(results, patch_ok, "Dashboard patch applied or already present", patch_detail)
    else:
        _record(results, False, "Dashboard patch applied or already present", "dashboard missing")

    if DASHBOARD_FILE.exists():
        ok, detail = _syntax_valid(DASHBOARD_FILE)
        _record(results, ok, "Dashboard syntax remains valid", detail)

        text = DASHBOARD_FILE.read_text(encoding="utf-8")
        _record(results, PATCH_MARKER in text, "Dashboard contains Phase 6-3 ready marker", PATCH_MARKER if PATCH_MARKER in text else "missing")
        _record(results, PATCH_BEGIN in text and PATCH_END in text, "Dashboard contains bounded Phase 6-3 patch block", "present" if PATCH_BEGIN in text and PATCH_END in text else "missing")
        _record(results, "def render_phase6_3_dashboard_mode_selector" in text, "Dashboard exposes Phase 6-3 helper function", "present" if "def render_phase6_3_dashboard_mode_selector" in text else "missing")

    if MODULE_FILE.exists():
        ok, detail = _syntax_valid(MODULE_FILE)
        _record(results, ok, "Phase 6-3 support module syntax valid", detail)

        try:
            module = _import_module(MODULE_FILE, "phase6_dashboard_mode_selector_patch")
            summary = module.write_phase6_3_outputs(PROJECT_ROOT)
            _record(results, isinstance(summary, dict), "Phase 6-3 module imports and writes outputs", type(summary).__name__)
        except Exception as exc:
            _record(results, False, "Phase 6-3 module imports and writes outputs", exc)
            traceback.print_exc()

    if isinstance(summary, dict):
        _record(results, summary.get("ready_marker") == PATCH_MARKER, "Mode selector patch has ready marker", summary.get("ready_marker"))
        _record(results, summary.get("release_decision") == "PHASE6_3_CONTROLLED_DASHBOARD_MODE_SELECTOR_PATCH_READY", "Mode selector patch has release decision", summary.get("release_decision"))
        _record(results, summary.get("dashboard_patch_required") is True, "Dashboard patch is explicitly required", summary.get("dashboard_patch_required"))
        _record(results, summary.get("dashboard_patch_applied_by_check") is True, "Dashboard patch applied by check script", summary.get("dashboard_patch_applied_by_check"))
        _record(results, summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
        _record(results, summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
        _record(results, summary.get("unknown_mode_falls_back_to_synthetic") is True, "Unknown modes fall back to synthetic", summary.get("unknown_mode_falls_back_to_synthetic"))
        _record(results, summary.get("default_mode") == "synthetic", "Default mode is synthetic", summary.get("default_mode"))
        _record(results, summary.get("historical_mode") == "historical_import", "Historical mode key is historical_import", summary.get("historical_mode"))
        caution = str(summary.get("customer_caution_text", "")).lower()
        _record(results, "not be interpreted as a forecast" in caution or "not a forecast" in caution, "Customer wording avoids forecast claim", summary.get("customer_caution_text"))

        output_paths = summary.get("output_paths", {})
        for name, value in output_paths.items():
            path = Path(value)
            _record(results, path.exists(), f"Output written: {name}", path)

    modes_csv = OUTPUT_TABLE_DIR / "phase6_3_dashboard_mode_selector_modes.csv"
    if modes_csv.exists():
        try:
            modes_df = pd.read_csv(modes_csv)
            has_synthetic = "synthetic" in set(modes_df.get("mode", []))
            has_historical = "historical_import" in set(modes_df.get("mode", []))
            _record(results, has_synthetic and has_historical, "Mode table has synthetic and historical modes", f"rows={len(modes_df)}")
        except Exception as exc:
            _record(results, False, "Mode table has synthetic and historical modes", exc)

    overall_pass = all(row["status"] == "PASS" for row in results)

    print()
    print("=" * 100)
    print(f"Overall Phase 6-3 checkpoint status: {'PASS' if overall_pass else 'FAIL'}")
    print("=" * 100)

    report_lines = [
        "Phase 6-3 controlled dashboard mode selector patch checkpoint report",
        "=" * 100,
        f"Project root: {PROJECT_ROOT}",
        "",
    ]
    report_lines.extend(_status_line(row["status"], row["label"], row["detail"]) for row in results)
    report_lines.extend(["", f"Overall Phase 6-3 checkpoint status: {'PASS' if overall_pass else 'FAIL'}"])
    CHECKPOINT_REPORT.write_text("\n".join(report_lines), encoding="utf-8")

    CHECKPOINT_JSON.write_text(
        json.dumps(
            {
                "overall_status": "PASS" if overall_pass else "FAIL",
                "project_root": str(PROJECT_ROOT),
                "results": results,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
