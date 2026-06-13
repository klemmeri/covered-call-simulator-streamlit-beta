"""
Phase 3I-5 customer explanation and wording verification check.
"""

from __future__ import annotations

import ast
import csv
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)

CHECKPOINT_REPORT = REPORT_DIR / "phase3i_5_customer_explanation_checkpoint_report.txt"
CHECKPOINT_JSON = REPORT_DIR / "phase3i_5_customer_explanation_checkpoint.json"
CHECKLIST_CSV = TABLE_DIR / "phase3i_5_customer_explanation_checklist.csv"
RELEASE_DECISION_FILE = REPORT_DIR / "phase3i_5_customer_explanation_release_decision.txt"

results: list[dict] = []


def add_result(status: str, item: str, detail: str = "") -> None:
    results.append({"status": status, "item": item, "detail": detail})
    print(f"{status:<10} {item:<70} {detail}")


def syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:  # pragma: no cover
        return False, repr(exc)


def contains_any(text: str, terms: list[str]) -> bool:
    lower = text.lower()
    return any(term.lower() in lower for term in terms)


def main() -> int:
    print("=" * 100)
    print("Phase 3I-5 customer explanation and wording verification check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}\n")

    dashboard = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
    module_path = PROJECT_ROOT / "app" / "paid_simulator" / "phase3i_customer_explanation_verification.py"
    doc_path = PROJECT_ROOT / "docs" / "phase3i_5_customer_explanation_verification.md"

    for label, path in [
        ("Dashboard file exists", dashboard),
        ("Phase 3I-5 explanation module exists", module_path),
        ("Phase 3I-5 documentation exists", doc_path),
    ]:
        add_result("PASS" if path.exists() else "FAIL", label, str(path))

    if dashboard.exists():
        ok, detail = syntax_valid(dashboard)
        add_result("PASS" if ok else "FAIL", "Dashboard syntax remains valid", detail)
        dashboard_text = dashboard.read_text(encoding="utf-8", errors="replace")
    else:
        dashboard_text = ""

    if module_path.exists():
        ok, detail = syntax_valid(module_path)
        add_result("PASS" if ok else "FAIL", "Phase 3I-5 module syntax valid", detail)

    try:
        from app.paid_simulator.phase3i_customer_explanation_verification import (
            READY_MARKER,
            RELEASE_DECISION,
            render_customer_explanation_verification,
        )

        model = render_customer_explanation_verification(streamlit_module=None)
        add_result("PASS" if isinstance(model, dict) else "FAIL", "Fallback render returns dict", type(model).__name__)
        text_blob = json.dumps(model, indent=2).lower()
        add_result("PASS" if model.get("ready_marker") == READY_MARKER else "FAIL", "Explanation model has ready marker", model.get("ready_marker", ""))
        add_result("PASS" if model.get("release_decision") == RELEASE_DECISION else "FAIL", "Explanation model has release decision", model.get("release_decision", ""))
        add_result("PASS" if len(model.get("explanations", [])) >= 6 else "FAIL", "At least six customer explanations present", str(len(model.get("explanations", []))))
        add_result("PASS" if len(model.get("readability_guardrails", [])) >= 4 else "FAIL", "At least four readability guardrails present", str(len(model.get("readability_guardrails", []))))

        for label in ["current price", "strike", "premium", "breakeven", "max profit", "downside cushion", "assignment zone", "warning"]:
            add_result("PASS" if label in text_blob else "FAIL", f"Customer-facing label explained: {label}", label)

        for term in ["capped", "assignment", "downside", "estimate", "not guarantees"]:
            add_result("PASS" if term in text_blob else "FAIL", f"Plain-language risk/explanation term present: {term}", term)

        RELEASE_DECISION_FILE.write_text(model.get("release_decision", ""), encoding="utf-8")
        add_result("PASS", "Release decision file written", str(RELEASE_DECISION_FILE))
    except Exception as exc:
        add_result("FAIL", "Explanation module imports and renders", repr(exc))

    # Existing project markers and controlled activation evidence.
    marker_checks = [
        ("Phase 3E marker remains present", ["PHASE3E_7C_DEVELOPER_TAB_READY"]),
        ("Phase 3F marker remains present", ["PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY"]),
        ("Controlled public activation evidence remains present", [
            "PHASE3H_7_PUBLIC_CUSTOMER_ACTIVATION_ENABLED",
            "PHASE3H_7_PUBLIC_CUSTOMER_VIEW_CONTROLLED_ACTIVATION_ENABLED",
            "PHASE3H_COMPLETE_PUBLIC_CUSTOMER_VIEW_CONTROLLED_ACTIVATION_VERIFIED",
            "controlled activation",
        ]),
    ]
    for label, terms in marker_checks:
        add_result("PASS" if contains_any(dashboard_text, terms) else "FAIL", label, terms[0])

    prior_reports = [
        "phase3h_8_post_activation_completion_checkpoint_report.txt",
        "phase3i_1_post_activation_browser_checkpoint_report.txt",
        "phase3i_2_customer_workflow_smoke_test_checkpoint_report.txt",
        "phase3i_3_save_reload_export_checkpoint_report.txt",
        "phase3i_4_customer_risk_warning_checkpoint_report.txt",
    ]
    for report in prior_reports:
        path = REPORT_DIR / report
        add_result("PASS" if path.exists() else "FAIL", f"Prior/current report exists: {report}", str(path))

    CHECKPOINT_REPORT.write_text("\n".join(f"{r['status']:<10} {r['item']:<70} {r['detail']}" for r in results), encoding="utf-8")
    CHECKPOINT_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
    with CHECKLIST_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["status", "item", "detail"])
        writer.writeheader()
        writer.writerows(results)

    print("\n" + "=" * 100)
    failed = [r for r in results if r["status"] != "PASS"]
    if failed:
        print("Overall Phase 3I-5 checkpoint status: FAIL")
        return 1
    print("Overall Phase 3I-5 checkpoint status: PASS")
    print("=" * 100)
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")
    print(f"Saved checklist CSV:     {CHECKLIST_CSV}")
    print(f"Saved release decision:  {RELEASE_DECISION_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
