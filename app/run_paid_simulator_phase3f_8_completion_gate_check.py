"""
run_paid_simulator_phase3f_8_completion_gate_check.py

Phase 3F-8 completion-gate checkpoint for the Covered Call Simulator.

This validation confirms that Phase 3F can be treated as complete as a protected
customer-preview layer, while the ordinary Customer view remains disabled.
"""

from __future__ import annotations

import ast
import csv
import importlib
import json
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)

CHECKPOINT_REPORT = REPORT_DIR / "phase3f_8_completion_gate_checkpoint_report.txt"
CHECKPOINT_JSON = REPORT_DIR / "phase3f_8_completion_gate_checkpoint.json"
CHECKLIST_CSV = TABLE_DIR / "phase3f_8_completion_gate_checklist.csv"

DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
COMPLETION_MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase3f_customer_preview_completion_gate.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase3f_8_customer_preview_completion_gate.md"

PRIOR_REPORTS = [
    PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3e_9_completion_checkpoint_report.txt",
    PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3f_3_customer_preview_route_checkpoint_report.txt",
    PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3f_4_preview_visual_checkpoint_report.txt",
    PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3f_6_release_readiness_checkpoint_report.txt",
]


def _syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:
        return False, repr(exc)


def _contains(path: Path, text: str) -> bool:
    if not path.exists():
        return False
    return text in path.read_text(encoding="utf-8", errors="ignore")


def _record(results: list[dict[str, Any]], passed: bool, label: str, detail: str = "") -> None:
    results.append({"status": "PASS" if passed else "FAIL", "label": label, "detail": detail})


def main() -> int:
    results: list[dict[str, Any]] = []

    print("=" * 100)
    print("Phase 3F-8 customer-preview completion gate check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    _record(results, COMPLETION_MODULE_FILE.exists(), "phase3f_customer_preview_completion_gate.py", str(COMPLETION_MODULE_FILE))
    _record(results, Path(__file__).exists(), "run_paid_simulator_phase3f_8_completion_gate_check.py", str(Path(__file__)))
    _record(results, DOC_FILE.exists(), "phase3f_8_customer_preview_completion_gate.md", str(DOC_FILE))

    if DASHBOARD_FILE.exists():
        ok, detail = _syntax_valid(DASHBOARD_FILE)
        _record(results, ok, "Dashboard syntax valid", detail)
    else:
        _record(results, False, "Dashboard file exists", str(DASHBOARD_FILE))

    if COMPLETION_MODULE_FILE.exists():
        ok, detail = _syntax_valid(COMPLETION_MODULE_FILE)
        _record(results, ok, "Completion gate module syntax valid", detail)
    else:
        _record(results, False, "Completion gate module syntax valid", "missing file")

    try:
        module = importlib.import_module("app.paid_simulator.phase3f_customer_preview_completion_gate")
        model = module.build_phase3f_completion_gate_model()
        model_dict = model.to_dict()
        fallback = module.render_phase3f_completion_gate(streamlit_module=None)
        _record(results, model_dict.get("marker") == "PHASE3F_8_COMPLETION_GATE_READY", "Completion model has ready marker", str(model_dict.get("marker")))
        _record(results, model_dict.get("protected_preview_enabled") is True, "Protected preview remains enabled", str(model_dict.get("protected_preview_enabled")))
        _record(results, model_dict.get("public_customer_enabled") is False, "Public Customer release remains disabled", str(model_dict.get("public_customer_enabled")))
        _record(results, len(model_dict.get("guardrails", [])) >= 4, "Completion model has guardrails", str(len(model_dict.get("guardrails", []))))
        _record(results, len(model_dict.get("next_release_requirements", [])) >= 3, "Completion model has release requirements", str(len(model_dict.get("next_release_requirements", []))))
        _record(results, isinstance(fallback, dict), "Fallback render returns dictionary", type(fallback).__name__)
    except Exception as exc:
        _record(results, False, "Completion module imports and renders", repr(exc))

    dashboard_text = DASHBOARD_FILE.read_text(encoding="utf-8", errors="ignore") if DASHBOARD_FILE.exists() else ""
    _record(results, "PHASE3E_7C_DEVELOPER_TAB_READY" in dashboard_text, "Phase 3E Developer marker still present", "Phase 3E marker search")
    _record(results, "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY" in dashboard_text, "Phase 3F preview route marker still present", "Phase 3F marker search")
    _record(results, "Phase 3D" in dashboard_text or "phase3d" in dashboard_text.lower(), "Phase 3D markers still present", "Phase 3D marker search")
    _record(results, "Customer" in dashboard_text or "customer" in dashboard_text.lower(), "Customer-view markers still present", "Customer marker search")
    _record(results, "PHASE3F_PUBLIC_CUSTOMER_ENABLED = True" not in dashboard_text, "Public Customer view not enabled by Phase 3F", "customer protected")

    existing_prior = [str(path) for path in PRIOR_REPORTS if path.exists()]
    _record(results, len(existing_prior) >= 2, "Prior Phase 3E/3F reports available", f"{len(existing_prior)} found")

    with CHECKLIST_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["status", "label", "detail"])
        writer.writeheader()
        writer.writerows(results)

    passed_all = all(item["status"] == "PASS" for item in results)

    lines = []
    lines.append("=" * 100)
    lines.append("Phase 3F-8 customer-preview completion gate check")
    lines.append("=" * 100)
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append("")
    for item in results:
        lines.append(f"{item['status']:<10} {item['label']:<65} {item['detail']}")
    lines.append("")
    lines.append("=" * 100)
    lines.append(f"Overall Phase 3F-8 checkpoint status: {'PASS' if passed_all else 'FAIL'}")
    lines.append("=" * 100)

    CHECKPOINT_REPORT.write_text("\n".join(lines), encoding="utf-8")
    CHECKPOINT_JSON.write_text(json.dumps({"passed": passed_all, "results": results}, indent=2), encoding="utf-8")

    for line in lines:
        print(line)
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")
    print(f"Saved checklist CSV:     {CHECKLIST_CSV}")

    return 0 if passed_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
