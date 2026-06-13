"""
run_paid_simulator_phase3h_7_public_activation_check.py

Checkpoint for Phase 3H-7 controlled public Customer-view activation.
"""

from __future__ import annotations

import ast
import csv
import importlib
import json
from pathlib import Path
import py_compile
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
BACKUP_DIR = PROJECT_ROOT / "outputs" / "backups" / "paid_simulator"

REPORT_PATH = REPORT_DIR / "phase3h_7_public_activation_checkpoint_report.txt"
JSON_PATH = REPORT_DIR / "phase3h_7_public_activation_checkpoint.json"
CSV_PATH = TABLE_DIR / "phase3h_7_public_activation_checklist.csv"
DECISION_PATH = REPORT_DIR / "phase3h_7_public_activation_release_decision.txt"

CHECKS = []


def add_check(name: str, passed: bool, detail: str = "") -> None:
    CHECKS.append({"name": name, "passed": bool(passed), "detail": str(detail)})


def has_text(path: Path, needle: str) -> bool:
    return path.exists() and needle in path.read_text(encoding="utf-8", errors="ignore")


def main() -> int:
    print("=" * 100)
    print("Phase 3H-7 controlled public Customer-view activation check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}\n")

    add_check("Dashboard file exists", DASHBOARD_FILE.exists(), DASHBOARD_FILE)
    try:
        py_compile.compile(str(DASHBOARD_FILE), doraise=True)
        ast.parse(DASHBOARD_FILE.read_text(encoding="utf-8"))
        add_check("Dashboard syntax remains valid", True, "syntax valid")
    except Exception as exc:
        add_check("Dashboard syntax remains valid", False, repr(exc))

    module_path = PROJECT_ROOT / "app" / "paid_simulator" / "phase3h_public_customer_activation.py"
    doc_path = PROJECT_ROOT / "docs" / "phase3h_7_public_customer_activation.md"
    add_check("Phase 3H-7 activation module exists", module_path.exists(), module_path)
    add_check("Phase 3H-7 documentation exists", doc_path.exists(), doc_path)

    model = {}
    try:
        module = importlib.import_module("app.paid_simulator.phase3h_public_customer_activation")
        model = module.render_phase3h_7_public_customer_activation(streamlit_module=None)
        add_check("Activation module imports and renders", isinstance(model, dict), type(model).__name__)
    except Exception as exc:
        add_check("Activation module imports and renders", False, repr(exc))

    add_check(
        "Activation model has ready marker",
        model.get("marker") == "PHASE3H_7_PUBLIC_CUSTOMER_ACTIVATION_READY",
        model.get("marker"),
    )
    add_check(
        "Activation model enables public Customer view",
        model.get("public_customer_enabled") is True,
        model.get("public_customer_enabled"),
    )
    add_check(
        "Activation model has controlled release decision",
        model.get("release_decision") == "PHASE3H_7_PUBLIC_CUSTOMER_VIEW_CONTROLLED_ACTIVATION_ENABLED",
        model.get("release_decision"),
    )
    add_check("Activation model has guardrails", len(model.get("guardrails", [])) >= 5, len(model.get("guardrails", [])))

    dashboard_text = DASHBOARD_FILE.read_text(encoding="utf-8", errors="ignore") if DASHBOARD_FILE.exists() else ""
    add_check("Dashboard has Phase 3H-7 activation marker", "PHASE3H_7_PUBLIC_CUSTOMER_ACTIVATION_READY" in dashboard_text, "marker search")
    add_check("Dashboard has Phase 3H-7 public enabled flag", "PHASE3H_7_PUBLIC_CUSTOMER_ENABLED = True" in dashboard_text, "enabled flag")
    add_check("Dashboard has Phase 3H-7 helper function", "_render_phase3h_7_public_customer_activation" in dashboard_text, "helper function")

    for marker_name, marker in [
        ("Phase 3H-2 route marker/evidence remains present", "PHASE3H_2_PUBLIC_CUSTOMER_ENABLED"),
        ("Phase 3G route-readiness marker remains present", "PHASE3G_4_PUBLIC_CUSTOMER_ENABLED"),
        ("Phase 3F marker remains present", "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY"),
        ("Phase 3E marker remains present", "PHASE3E_7C_DEVELOPER_TAB_READY"),
        ("Phase 3D markers remain present", "Phase 3D"),
    ]:
        add_check(marker_name, marker in dashboard_text, marker)

    labels_text = " ".join(model.get("customer_labels", [])).lower()
    for label in ["current price", "breakeven", "max profit", "downside cushion", "assignment zone", "warning"]:
        add_check(f"Customer-facing label present: {label}", label in labels_text, label)

    backup_exists = any(BACKUP_DIR.glob("config_form_app_before_phase3h_7_*.py")) if BACKUP_DIR.exists() else False
    add_check("Timestamped Phase 3H-7 dashboard backup exists", backup_exists, BACKUP_DIR)

    decision = model.get("release_decision", "UNKNOWN")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("=" * 100)
    lines.append("Phase 3H-7 controlled public Customer-view activation check")
    lines.append("=" * 100)
    for check in CHECKS:
        status = "PASS" if check["passed"] else "FAIL"
        lines.append(f"{status:<10} {check['name']:<70} {check['detail']}")
    overall = all(c["passed"] for c in CHECKS)
    lines.append("")
    lines.append("=" * 100)
    lines.append(f"Overall Phase 3H-7 checkpoint status: {'PASS' if overall else 'FAIL'}")
    lines.append("=" * 100)
    report_text = "\n".join(lines)
    REPORT_PATH.write_text(report_text, encoding="utf-8")
    JSON_PATH.write_text(json.dumps({"overall_pass": overall, "checks": CHECKS, "release_decision": decision}, indent=2), encoding="utf-8")
    DECISION_PATH.write_text(decision + "\n", encoding="utf-8")
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "passed", "detail"])
        writer.writeheader()
        writer.writerows(CHECKS)

    print(report_text)
    print(f"Saved checkpoint report: {REPORT_PATH}")
    print(f"Saved checkpoint JSON:   {JSON_PATH}")
    print(f"Saved checklist CSV:     {CSV_PATH}")
    print(f"Saved release decision:  {DECISION_PATH}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
