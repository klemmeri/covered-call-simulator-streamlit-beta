"""
Phase 3H-5 activation-readiness checkpoint for the Covered Call Simulator.

Run from PyCharm or the project root:
    python app/run_paid_simulator_phase3h_5_activation_readiness_check.py
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)

DASHBOARD_FILE = APP_DIR / "paid_simulator" / "config_form_app.py"
MODULE_FILE = APP_DIR / "paid_simulator" / "phase3h_activation_readiness_report.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase3h_5_activation_readiness_report.md"

REPORT_FILE = REPORT_DIR / "phase3h_5_activation_readiness_checkpoint_report.txt"
JSON_FILE = REPORT_DIR / "phase3h_5_activation_readiness_checkpoint.json"
CSV_FILE = TABLE_DIR / "phase3h_5_activation_readiness_checklist.csv"
DECISION_FILE = REPORT_DIR / "phase3h_5_activation_readiness_release_decision.txt"

PRIOR_REPORTS = [
    "phase3e_9_completion_checkpoint_report.txt",
    "phase3f_8_completion_gate_checkpoint_report.txt",
    "phase3g_8_completion_gate_checkpoint_report.txt",
    "phase3h_1_activation_switch_checkpoint_report.txt",
    "phase3h_2_activation_route_checkpoint_report.txt",
    "phase3h_3_activation_route_smoke_test_checkpoint_report.txt",
    "phase3h_4_pre_activation_validation_checkpoint_report.txt",
]


def check_syntax(path: Path):
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def import_module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def add(results, status: bool, label: str, detail: str = ""):
    results.append({"status": "PASS" if status else "FAIL", "label": label, "detail": detail})


def main() -> int:
    results = []
    print("=" * 100)
    print("Phase 3H-5 activation-readiness check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}\n")

    add(results, DASHBOARD_FILE.exists(), "Dashboard file exists", str(DASHBOARD_FILE))
    add(results, MODULE_FILE.exists(), "Phase 3H-5 activation-readiness module exists", str(MODULE_FILE))
    add(results, DOC_FILE.exists(), "Phase 3H-5 documentation exists", str(DOC_FILE))

    dashboard_text = DASHBOARD_FILE.read_text(encoding="utf-8") if DASHBOARD_FILE.exists() else ""

    try:
        check_syntax(DASHBOARD_FILE)
        add(results, True, "Dashboard syntax remains valid", "syntax valid")
    except Exception as exc:
        add(results, False, "Dashboard syntax remains valid", repr(exc))

    for marker, label in [
        ("Phase 3D", "Phase 3D markers remain present"),
        ("PHASE3E_7C_DEVELOPER_TAB_READY", "Phase 3E marker remains present"),
        ("PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY", "Phase 3F marker remains present"),
        ("PHASE3G_4", "Phase 3G route-readiness evidence remains present"),
        ("PHASE3H_2_PUBLIC_CUSTOMER_ENABLED = False", "Phase 3H public Customer route remains disabled"),
    ]:
        add(results, marker in dashboard_text, label, marker)

    try:
        check_syntax(MODULE_FILE)
        add(results, True, "Phase 3H-5 module syntax valid", "syntax valid")
        module = import_module_from_path("phase3h_activation_readiness_report_check", MODULE_FILE)
        model = module.render_activation_readiness_report(streamlit_module=None)
        add(results, isinstance(model, dict), "Fallback render returns dict", type(model).__name__)
        add(results, model.get("marker") == "PHASE3H_5_ACTIVATION_READINESS_READY", "Readiness model has ready marker", str(model.get("marker")))
        add(results, model.get("public_customer_enabled") is False, "Readiness model keeps public Customer view disabled", str(model.get("public_customer_enabled")))
        add(results, model.get("release_decision") == "PHASE3H_5_READY_FOR_FINAL_ACTIVATION_REVIEW_PUBLIC_CUSTOMER_VIEW_DISABLED", "Readiness model has conservative release decision", str(model.get("release_decision")))
        add(results, len(model.get("guardrails", [])) >= 5, "Readiness model has guardrails", str(len(model.get("guardrails", []))))
        add(results, len(model.get("readiness_requirements", [])) >= 5, "Readiness model has readiness requirements", str(len(model.get("readiness_requirements", []))))
        labels = " ".join(model.get("customer_facing_labels", [])).lower()
        for label in ["current price", "breakeven", "max profit", "downside cushion", "assignment zone", "warning"]:
            add(results, label in labels, f"Customer-facing label present: {label}", label)
    except Exception as exc:
        add(results, False, "Phase 3H-5 module imports and renders", repr(exc))
        model = {}

    for report in PRIOR_REPORTS:
        path = REPORT_DIR / report
        add(results, path.exists(), f"Prior report exists: {report}", str(path))

    decision = model.get("release_decision", "NO_DECISION") if isinstance(model, dict) else "NO_DECISION"
    DECISION_FILE.write_text(decision + "\n", encoding="utf-8")
    add(results, DECISION_FILE.exists(), "Activation-readiness release-decision file written", str(DECISION_FILE))

    lines = []
    for item in results:
        print(f"{item['status']:<10} {item['label']:<70} {item['detail']}")
        lines.append(f"{item['status']:<10} {item['label']:<70} {item['detail']}")

    overall = all(item["status"] == "PASS" for item in results)
    status_line = f"Overall Phase 3H-5 checkpoint status: {'PASS' if overall else 'FAIL'}"
    print("\n" + "=" * 100)
    print(status_line)
    print("=" * 100)

    REPORT_FILE.write_text("Phase 3H-5 activation-readiness check\n" + "=" * 100 + "\n" + "\n".join(lines) + "\n\n" + status_line + "\n", encoding="utf-8")
    JSON_FILE.write_text(json.dumps({"created_at": datetime.now().isoformat(timespec="seconds"), "overall_pass": overall, "results": results}, indent=2), encoding="utf-8")
    CSV_FILE.write_text("status,label,detail\n" + "\n".join(f"{r['status']},{json.dumps(r['label'])},{json.dumps(r['detail'])}" for r in results) + "\n", encoding="utf-8")

    print(f"Saved checkpoint report: {REPORT_FILE}")
    print(f"Saved checkpoint JSON:   {JSON_FILE}")
    print(f"Saved checklist CSV:     {CSV_FILE}")
    print(f"Saved release decision:  {DECISION_FILE}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
