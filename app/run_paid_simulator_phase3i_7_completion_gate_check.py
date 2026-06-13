"""
run_paid_simulator_phase3i_7_completion_gate_check.py

Checkpoint script for Phase 3I-7 customer workflow completion gate.
"""

from __future__ import annotations

import ast
import csv
import importlib
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

CHECKS: list[dict[str, str]] = []


def add_check(name: str, passed: bool, detail: str = "") -> None:
    CHECKS.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})


def print_section(title: str) -> None:
    print("\n" + title)
    print("-" * 100)


def file_has_valid_syntax(path: Path) -> bool:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True
    except Exception:
        return False


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def main() -> int:
    print("=" * 100)
    print("Phase 3I-7 customer workflow completion gate check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")

    dashboard_file = APP_DIR / "paid_simulator" / "config_form_app.py"
    module_file = APP_DIR / "paid_simulator" / "phase3i_customer_workflow_completion_gate.py"
    doc_file = PROJECT_ROOT / "docs" / "phase3i_7_customer_workflow_completion_gate.md"

    print_section("Expected files")
    for label, path in [
        ("Dashboard file exists", dashboard_file),
        ("Phase 3I-7 completion module exists", module_file),
        ("Phase 3I-7 documentation exists", doc_file),
    ]:
        exists = path.exists()
        add_check(label, exists, str(path))
        print(f"{'PASS' if exists else 'FAIL':<10} {label:<70} {path}")

    print_section("Syntax and import checks")
    dashboard_syntax = dashboard_file.exists() and file_has_valid_syntax(dashboard_file)
    module_syntax = module_file.exists() and file_has_valid_syntax(module_file)
    add_check("Dashboard syntax remains valid", dashboard_syntax, "syntax valid" if dashboard_syntax else "syntax invalid")
    add_check("Phase 3I-7 module syntax valid", module_syntax, "syntax valid" if module_syntax else "syntax invalid")

    model = {}
    try:
        mod = importlib.import_module("app.paid_simulator.phase3i_customer_workflow_completion_gate")
        model = mod.render_customer_workflow_completion_gate(streamlit_module=None)
        add_check("Phase 3I-7 module imports and fallback renders", isinstance(model, dict), type(model).__name__)
    except Exception as exc:
        add_check("Phase 3I-7 module imports and fallback renders", False, repr(exc))

    print_section("Completion model checks")
    expected_marker = "PHASE3I_7_CUSTOMER_WORKFLOW_COMPLETION_READY"
    expected_decision = "PHASE3I_COMPLETE_CUSTOMER_WORKFLOW_VERIFIED"
    add_check("Completion model has ready marker", model.get("ready_marker") == expected_marker, str(model.get("ready_marker")))
    add_check("Completion model has release decision", model.get("release_decision") == expected_decision, str(model.get("release_decision")))
    add_check("Completion model expects public customer workflow", model.get("public_customer_workflow_expected") is True, str(model.get("public_customer_workflow_expected")))
    add_check("Completion model has at least five guardrails", len(model.get("guardrails", [])) >= 5, str(len(model.get("guardrails", []))))
    add_check("Completion model has at least six completed checks", len(model.get("completed_checks", [])) >= 6, str(len(model.get("completed_checks", []))))

    flattened_model = json.dumps(model, indent=2).lower()
    for term in ["current price", "strike", "premium", "breakeven", "max profit", "downside cushion", "assignment zone", "warning", "capped", "assignment", "downside", "estimate"]:
        add_check(f"Customer completion term present: {term}", term in flattened_model, term)

    print_section("Dashboard marker checks")
    dashboard_text = read_text(dashboard_file)
    marker_checks = [
        ("Phase 3H controlled activation evidence present", ["PHASE3H_7", "PUBLIC_CUSTOMER", "CONTROLLED", "ACTIVATION"]),
        ("Phase 3E marker remains present", ["PHASE3E_7C_DEVELOPER_TAB_READY"]),
        ("Phase 3F marker remains present", ["PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY"]),
        ("Phase 3G marker remains present", ["PHASE3G"]),
        ("Phase 3D marker remains present", ["Phase 3D"]),
    ]
    for label, terms in marker_checks:
        ok = all(term.lower() in dashboard_text.lower() for term in terms)
        add_check(label, ok, ", ".join(terms))

    print_section("Prior report checks")
    required_reports = model.get("required_reports", []) or [
        "phase3i_1_post_activation_browser_checkpoint_report.txt",
        "phase3i_2_customer_workflow_smoke_test_checkpoint_report.txt",
        "phase3i_3_save_reload_export_checkpoint_report.txt",
        "phase3i_4_customer_risk_warning_checkpoint_report.txt",
        "phase3i_5_customer_explanation_checkpoint_report.txt",
        "phase3i_6_customer_output_report_checkpoint_report.txt",
    ]
    for filename in required_reports:
        path = REPORTS_DIR / filename
        exists = path.exists()
        add_check(f"Prior report exists: {filename}", exists, str(path))

    # Write outputs.
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / "phase3i_7_completion_gate_checkpoint_report.txt"
    json_path = REPORTS_DIR / "phase3i_7_completion_gate_checkpoint.json"
    csv_path = TABLES_DIR / "phase3i_7_completion_gate_checklist.csv"
    decision_path = REPORTS_DIR / "phase3i_7_completion_release_decision.txt"

    passed = all(item["status"] == "PASS" for item in CHECKS)

    lines = [
        "Phase 3I-7 customer workflow completion gate check",
        f"Project root: {PROJECT_ROOT}",
        "",
    ]
    lines.extend(f"{item['status']:<6} {item['name']} - {item['detail']}" for item in CHECKS)
    lines.extend(["", f"Overall Phase 3I-7 checkpoint status: {'PASS' if passed else 'FAIL'}"])
    report_path.write_text("\n".join(lines), encoding="utf-8")
    json_path.write_text(json.dumps({"passed": passed, "checks": CHECKS, "model": model}, indent=2), encoding="utf-8")
    decision_path.write_text(model.get("release_decision", expected_decision), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["status", "name", "detail"])
        writer.writeheader()
        writer.writerows(CHECKS)

    for item in CHECKS:
        print(f"{item['status']:<10} {item['name']:<70} {item['detail']}")

    print("\n" + "=" * 100)
    print(f"Overall Phase 3I-7 checkpoint status: {'PASS' if passed else 'FAIL'}")
    print("=" * 100)
    print(f"Saved checkpoint report: {report_path}")
    print(f"Saved checkpoint JSON:   {json_path}")
    print(f"Saved checklist CSV:     {csv_path}")
    print(f"Saved release decision:  {decision_path}")

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
