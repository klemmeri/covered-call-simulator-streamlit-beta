"""
Phase 3I-6 customer output/report verification check.
"""

from __future__ import annotations

import ast
import csv
import importlib
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase3i_customer_output_report_verification.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase3i_6_customer_output_report_verification.md"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_FILE = REPORT_DIR / "phase3i_6_customer_output_report_checkpoint_report.txt"
JSON_FILE = REPORT_DIR / "phase3i_6_customer_output_report_checkpoint.json"
CSV_FILE = TABLE_DIR / "phase3i_6_customer_output_report_checklist.csv"
DECISION_FILE = REPORT_DIR / "phase3i_6_customer_output_report_release_decision.txt"

EXPECTED_LABELS = [
    "current price",
    "strike",
    "premium",
    "breakeven",
    "max profit",
    "downside cushion",
    "assignment zone",
    "warning",
]
EXPECTED_TERMS = ["capped", "assignment", "downside", "estimate"]
PRIOR_REPORTS = [
    "phase3h_8_post_activation_completion_checkpoint_report.txt",
    "phase3i_1_post_activation_browser_checkpoint_report.txt",
    "phase3i_2_customer_workflow_smoke_test_checkpoint_report.txt",
    "phase3i_3_save_reload_export_checkpoint_report.txt",
    "phase3i_4_customer_risk_warning_checkpoint_report.txt",
    "phase3i_5_customer_explanation_checkpoint_report.txt",
]


def print_header(title: str) -> None:
    print("=" * 100)
    print(title)
    print("=" * 100)


def add(results: list[dict], passed: bool, name: str, detail: str) -> None:
    status = "PASS" if passed else "FAIL"
    print(f"{status:<10} {name:<70} {detail}")
    results.append({"status": status, "name": name, "detail": detail})


def syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:
        return False, repr(exc)


def main() -> int:
    results: list[dict] = []
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    print_header("Phase 3I-6 customer output/report verification check")
    print(f"Project root: {PROJECT_ROOT}\n")

    add(results, DASHBOARD_FILE.exists(), "Dashboard file exists", str(DASHBOARD_FILE))
    add(results, MODULE_FILE.exists(), "Phase 3I-6 output/report module exists", str(MODULE_FILE))
    add(results, DOC_FILE.exists(), "Phase 3I-6 documentation exists", str(DOC_FILE))

    if DASHBOARD_FILE.exists():
        ok, detail = syntax_valid(DASHBOARD_FILE)
        add(results, ok, "Dashboard syntax remains valid", detail)
        dashboard_text = DASHBOARD_FILE.read_text(encoding="utf-8", errors="ignore")
    else:
        dashboard_text = ""

    if MODULE_FILE.exists():
        ok, detail = syntax_valid(MODULE_FILE)
        add(results, ok, "Phase 3I-6 module syntax valid", detail)
    
    model = {}
    try:
        module = importlib.import_module("app.paid_simulator.phase3i_customer_output_report_verification")
        model = module.render_customer_output_report_verification(streamlit_module=None)
        add(results, isinstance(model, dict), "Fallback render returns dict", type(model).__name__)
    except Exception as exc:
        add(results, False, "Output/report module imports and renders", repr(exc))

    haystack = json.dumps(model).lower() if isinstance(model, dict) else ""
    add(results, model.get("ready_marker") == "PHASE3I_6_CUSTOMER_OUTPUT_REPORT_VERIFICATION_READY", "Output/report model has ready marker", str(model.get("ready_marker")))
    add(results, model.get("release_decision") == "PHASE3I_6_CUSTOMER_OUTPUT_REPORTS_VERIFIED", "Output/report model has release decision", str(model.get("release_decision")))

    for label in EXPECTED_LABELS:
        add(results, label in haystack, f"Customer-facing label present: {label}", label)
    for term in EXPECTED_TERMS:
        add(results, term in haystack, f"Customer report term present: {term}", term)

    add(results, len(model.get("expected_outputs", [])) >= 5, "At least five expected customer outputs present", str(len(model.get("expected_outputs", []))))
    add(results, len(model.get("guardrails", [])) >= 4, "At least four report guardrails present", str(len(model.get("guardrails", []))))

    activation_evidence = (
        "PHASE3H_7_PUBLIC_CUSTOMER_ACTIVATION_ENABLED" in dashboard_text
        or "PHASE3H_COMPLETE_PUBLIC_CUSTOMER_VIEW_CONTROLLED_ACTIVATION_VERIFIED" in dashboard_text
        or (REPORT_DIR / "phase3h_8_post_activation_completion_checkpoint_report.txt").exists()
    )
    add(results, activation_evidence, "Public Customer activation remains controlled-enabled", "controlled activation evidence")
    add(results, "PHASE3E_7C_DEVELOPER_TAB_READY" in dashboard_text, "Phase 3E marker remains present", "PHASE3E_7C_DEVELOPER_TAB_READY")
    add(results, "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY" in dashboard_text, "Phase 3F marker remains present", "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY")

    for filename in PRIOR_REPORTS:
        path = REPORT_DIR / filename
        add(results, path.exists(), f"Prior report exists: {filename}", str(path))

    DECISION_FILE.write_text(model.get("release_decision", ""), encoding="utf-8")
    add(results, DECISION_FILE.exists(), "Release decision file written", str(DECISION_FILE))

    REPORT_FILE.write_text("\n".join(f"{r['status']} {r['name']} - {r['detail']}" for r in results), encoding="utf-8")
    JSON_FILE.write_text(json.dumps(results, indent=2), encoding="utf-8")
    with CSV_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["status", "name", "detail"])
        writer.writeheader()
        writer.writerows(results)

    print("\n" + "=" * 100)
    failed = [r for r in results if r["status"] != "PASS"]
    if failed:
        print("Overall Phase 3I-6 checkpoint status: FAIL")
        return 1
    print("Overall Phase 3I-6 checkpoint status: PASS")
    print("=" * 100)
    print(f"Saved checkpoint report: {REPORT_FILE}")
    print(f"Saved checkpoint JSON:   {JSON_FILE}")
    print(f"Saved checklist CSV:     {CSV_FILE}")
    print(f"Saved release decision:  {DECISION_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
