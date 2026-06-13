"""
Phase 3I-1 post-activation browser verification check.

Read-only validation for the controlled public Customer-view activation path.
"""
from pathlib import Path
import ast
import csv
import json
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DASHBOARD = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
MODULE = PROJECT_ROOT / "app" / "paid_simulator" / "phase3i_post_activation_browser_verification.py"
DOC = PROJECT_ROOT / "docs" / "phase3i_1_post_activation_browser_verification.md"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT = REPORT_DIR / "phase3i_1_post_activation_browser_checkpoint_report.txt"
JSON_REPORT = REPORT_DIR / "phase3i_1_post_activation_browser_checkpoint.json"
CSV_REPORT = TABLE_DIR / "phase3i_1_post_activation_browser_checklist.csv"
BROWSER_CHECKLIST = REPORT_DIR / "phase3i_1_browser_customer_workflow_checklist.md"

checks = []


def add(name, passed, detail=""):
    checks.append({"name": name, "passed": bool(passed), "detail": str(detail)})


def syntax_valid(path):
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:
        return False, repr(exc)


def contains(text, pattern):
    return pattern in text


def main():
    print("=" * 100)
    print("Phase 3I-1 post-activation browser/customer workflow verification check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    add("Dashboard file exists", DASHBOARD.exists(), DASHBOARD)
    add("Phase 3I-1 verification module exists", MODULE.exists(), MODULE)
    add("Phase 3I-1 documentation exists", DOC.exists(), DOC)

    dashboard_text = DASHBOARD.read_text(encoding="utf-8") if DASHBOARD.exists() else ""
    module_text = MODULE.read_text(encoding="utf-8") if MODULE.exists() else ""

    if DASHBOARD.exists():
        ok, detail = syntax_valid(DASHBOARD)
        add("Dashboard syntax remains valid", ok, detail)

    if MODULE.exists():
        ok, detail = syntax_valid(MODULE)
        add("Phase 3I-1 module syntax valid", ok, detail)

    add("Phase 3H controlled activation marker present", contains(dashboard_text, "PHASE3H_7_PUBLIC_CUSTOMER_VIEW_CONTROLLED_ACTIVATION_ENABLED") or contains(dashboard_text, "PHASE3H_7"), "Phase 3H activation marker search")
    add("Phase 3G marker remains present", contains(dashboard_text, "PHASE3G") or contains(dashboard_text, "Phase 3G"), "Phase 3G marker search")
    add("Phase 3F marker remains present", contains(dashboard_text, "PHASE3F") or contains(dashboard_text, "Phase 3F"), "Phase 3F marker search")
    add("Phase 3E marker remains present", contains(dashboard_text, "PHASE3E") or contains(dashboard_text, "Phase 3E"), "Phase 3E marker search")
    add("Phase 3D markers remain present", contains(dashboard_text, "Phase 3D") or contains(dashboard_text, "phase3d"), "Phase 3D marker search")

    try:
        from app.paid_simulator.phase3i_post_activation_browser_verification import build_phase3i_1_model, render_phase3i_1_model
        model = build_phase3i_1_model()
        rendered = render_phase3i_1_model(streamlit_module=None)
        add("Phase 3I-1 model imports", True, "module imported")
        add("Fallback render returns dict", isinstance(rendered, dict), type(rendered).__name__)
        add("Model has ready marker", model.get("marker") == "PHASE3I_1_POST_ACTIVATION_BROWSER_VERIFICATION_READY", model.get("marker"))
        add("Model expects public activation after Phase 3H", model.get("public_customer_activation_expected") is True, model.get("public_customer_activation_expected"))
        add("Model makes no dashboard changes", model.get("dashboard_changes_made") is False, model.get("dashboard_changes_made"))
        add("Model has guardrails", len(model.get("guardrails", [])) >= 4, len(model.get("guardrails", [])))
        labels = " ".join(model.get("customer_labels", [])).lower()
        for label in ["current price", "breakeven", "max profit", "downside cushion", "assignment zone", "warning"]:
            add(f"Customer-facing label present: {label}", label in labels, label)
    except Exception as exc:
        model = {}
        add("Phase 3I-1 model imports", False, repr(exc))

    checklist_lines = [
        "# Phase 3I-1 Browser Customer Workflow Checklist",
        "",
        "Run:",
        "",
        "```text",
        "streamlit run app\\paid_simulator\\config_form_app.py",
        "```",
        "",
        "Confirm these manually:",
        "",
        "1. Dashboard opens without a red traceback.",
        "2. Public Customer-view controlled activation is visible after Phase 3H-7.",
        "3. Customer-facing payoff labels are visible: current price, strike, premium, breakeven, max profit, downside cushion, assignment zone.",
        "4. Warning/risk language is visible for risky setups.",
        "5. Developer-view Phase 3D/3E/3F material remains protected and available where expected.",
    ]
    BROWSER_CHECKLIST.write_text("\n".join(checklist_lines), encoding="utf-8")
    add("Browser checklist written", True, BROWSER_CHECKLIST)

    for c in checks:
        status = "PASS" if c["passed"] else "FAIL"
        print(f"{status:<10} {c['name']:<70} {c['detail']}")

    all_pass = all(c["passed"] for c in checks)
    print()
    print("=" * 100)
    print(f"Overall Phase 3I-1 checkpoint status: {'PASS' if all_pass else 'FAIL'}")
    print("=" * 100)

    REPORT.write_text("\n".join([f"{'PASS' if c['passed'] else 'FAIL'}\t{c['name']}\t{c['detail']}" for c in checks]) + f"\n\nOverall Phase 3I-1 checkpoint status: {'PASS' if all_pass else 'FAIL'}\n", encoding="utf-8")
    JSON_REPORT.write_text(json.dumps({"checks": checks, "overall_pass": all_pass}, indent=2), encoding="utf-8")
    with CSV_REPORT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "passed", "detail"])
        writer.writeheader()
        writer.writerows(checks)

    print(f"Saved checkpoint report: {REPORT}")
    print(f"Saved checkpoint JSON:   {JSON_REPORT}")
    print(f"Saved checklist CSV:     {CSV_REPORT}")
    print(f"Saved browser checklist: {BROWSER_CHECKLIST}")
    raise SystemExit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
