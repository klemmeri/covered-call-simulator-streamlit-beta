"""
Phase 6-4 dashboard mode selector visibility smoke-test check.
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
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase6_dashboard_mode_selector_visibility_smoke.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase6_4_dashboard_mode_selector_visibility_smoke.md"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CHECKPOINT_REPORT = REPORT_DIR / "phase6_4_dashboard_mode_selector_visibility_checkpoint_report.txt"
CHECKPOINT_JSON = REPORT_DIR / "phase6_4_dashboard_mode_selector_visibility_checkpoint.json"


def _status(label: str, passed: bool, detail: Any = "") -> dict[str, Any]:
    status = "PASS" if passed else "FAIL"
    print(f"{status:<10} {label:<70} {detail}")
    return {"label": label, "passed": passed, "detail": str(detail)}


def _compile(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "syntax valid"
    except Exception as exc:  # pragma: no cover
        return False, str(exc)


def _import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    print("=" * 100)
    print("Phase 6-4 dashboard mode selector visibility smoke test check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    checks: list[dict[str, Any]] = []

    checks.append(_status("Dashboard file exists", DASHBOARD_FILE.exists(), DASHBOARD_FILE))
    checks.append(_status("Phase 6-4 visibility module exists", MODULE_FILE.exists(), MODULE_FILE))
    checks.append(_status("Phase 6-4 documentation exists", DOC_FILE.exists(), DOC_FILE))

    if DASHBOARD_FILE.exists():
        ok, detail = _compile(DASHBOARD_FILE)
        checks.append(_status("Dashboard syntax remains valid", ok, detail))
        dashboard_text = DASHBOARD_FILE.read_text(encoding="utf-8", errors="replace")
        checks.append(_status("Dashboard contains Phase 6-3 ready marker", "PHASE6_3_DASHBOARD_MODE_SELECTOR_PATCH_READY" in dashboard_text, "marker check"))
        checks.append(_status("Dashboard exposes Phase 6-3 helper function", "phase6_3_resolve_dashboard_data_mode" in dashboard_text, "helper check"))

    if MODULE_FILE.exists():
        ok, detail = _compile(MODULE_FILE)
        checks.append(_status("Phase 6-4 module syntax valid", ok, detail))

    summary = None
    if MODULE_FILE.exists():
        try:
            module = _import_module(MODULE_FILE, "phase6_dashboard_mode_selector_visibility_smoke")
            summary = module.build_phase6_4_summary()
            checks.append(_status("Phase 6-4 module imports and writes outputs", isinstance(summary, dict), type(summary).__name__))
        except Exception as exc:
            checks.append(_status("Phase 6-4 module imports and writes outputs", False, exc))
            traceback.print_exc()

    if isinstance(summary, dict):
        checks.append(_status("Visibility smoke has ready marker", summary.get("ready_marker") == "PHASE6_4_DASHBOARD_MODE_SELECTOR_VISIBILITY_SMOKE_READY", summary.get("ready_marker")))
        checks.append(_status("Visibility smoke has release decision", summary.get("release_decision") == "PHASE6_4_DASHBOARD_MODE_SELECTOR_VISIBILITY_SMOKE_CREATED_NO_DASHBOARD_CHANGE", summary.get("release_decision")))
        checks.append(_status("Visibility smoke confirms no dashboard change", summary.get("dashboard_change_required") is False, summary.get("dashboard_change_required")))
        checks.append(_status("Visibility smoke uses expected source mode", summary.get("source_mode") == "dashboard_mode_selector_visibility_smoke", summary.get("source_mode")))
        checks.append(_status("Synthetic default remains preserved", summary.get("synthetic_default_preserved") is True, summary.get("synthetic_default_preserved")))
        checks.append(_status("Historical mode remains explicit only", summary.get("historical_mode_explicit_only") is True, summary.get("historical_mode_explicit_only")))
        checks.append(_status("Dashboard selector markers are visible", summary.get("dashboard_selector_markers_present") is True, summary.get("dashboard_selector_markers_present")))
        checks.append(_status("Marker table has rows", (summary.get("marker_rows") or 0) >= 5, summary.get("marker_rows")))
        for key, path_text in summary.get("outputs", {}).items():
            path = Path(path_text)
            checks.append(_status(f"Output written: {key}", path.exists(), path))

    overall = all(item["passed"] for item in checks)
    print()
    print("=" * 100)
    print(f"Overall Phase 6-4 checkpoint status: {'PASS' if overall else 'FAIL'}")
    print("=" * 100)

    payload = {"overall_status": "PASS" if overall else "FAIL", "checks": checks}
    CHECKPOINT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    CHECKPOINT_REPORT.write_text("\n".join([f"{c['label']}: {'PASS' if c['passed'] else 'FAIL'} -- {c['detail']}" for c in checks]) + "\n", encoding="utf-8")
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
