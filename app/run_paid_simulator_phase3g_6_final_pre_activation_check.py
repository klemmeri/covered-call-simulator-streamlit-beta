"""
Phase 3G-6 final pre-activation decision gate check.

Run from PyCharm or terminal:
    python app/run_paid_simulator_phase3g_6_final_pre_activation_check.py
"""

from __future__ import annotations

import ast
import csv
import importlib
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

CHECKPOINT_REPORT = REPORT_DIR / "phase3g_6_final_pre_activation_checkpoint_report.txt"
CHECKPOINT_JSON = REPORT_DIR / "phase3g_6_final_pre_activation_checkpoint.json"
CHECKLIST_CSV = TABLE_DIR / "phase3g_6_final_pre_activation_checklist.csv"
DECISION_TXT = REPORT_DIR / "phase3g_6_final_pre_activation_release_decision.txt"

DASHBOARD = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase3g_public_customer_final_pre_activation_gate.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase3g_6_final_pre_activation_gate.md"

EXPECTED_PRIOR_REPORTS = [
    REPORT_DIR / "phase3e_9_completion_checkpoint_report.txt",
    REPORT_DIR / "phase3f_8_completion_gate_checkpoint_report.txt",
    REPORT_DIR / "phase3g_1_public_release_gate_checkpoint_report.txt",
    REPORT_DIR / "phase3g_5_public_route_promotion_decision.txt",
]


def valid_python(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:  # pragma: no cover
        return False, repr(exc)


def add_result(results: list[dict], name: str, passed: bool, detail: str):
    results.append({"name": name, "passed": bool(passed), "detail": str(detail)})


def main() -> int:
    results: list[dict] = []

    print("=" * 100)
    print("Phase 3G-6 final pre-activation decision gate check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    add_result(results, "Dashboard file exists", DASHBOARD.exists(), DASHBOARD)
    add_result(results, "Phase 3G-6 module exists", MODULE_FILE.exists(), MODULE_FILE)
    add_result(results, "Phase 3G-6 docs exist", DOC_FILE.exists(), DOC_FILE)

    if DASHBOARD.exists():
        ok, detail = valid_python(DASHBOARD)
        add_result(results, "Dashboard syntax valid", ok, detail)
        dashboard_text = DASHBOARD.read_text(encoding="utf-8", errors="replace")
    else:
        dashboard_text = ""

    if MODULE_FILE.exists():
        ok, detail = valid_python(MODULE_FILE)
        add_result(results, "Phase 3G-6 module syntax valid", ok, detail)

    try:
        mod = importlib.import_module("app.paid_simulator.phase3g_public_customer_final_pre_activation_gate")
        model = mod.build_phase3g_6_final_pre_activation_gate_model()
        data = model.to_dict()
        rendered = mod.render_phase3g_6_final_pre_activation_gate(streamlit_module=None)
        add_result(results, "Phase 3G-6 module imports and renders", isinstance(rendered, dict), type(rendered).__name__)
        add_result(results, "Ready marker present", data.get("marker") == "PHASE3G_6_FINAL_PRE_ACTIVATION_GATE_READY", data.get("marker"))
        add_result(results, "Public Customer view remains disabled", data.get("public_customer_enabled") is False, data.get("public_customer_enabled"))
        add_result(results, "Protected preview remains required", data.get("protected_preview_required") is True, data.get("protected_preview_required"))
        add_result(results, "Release decision is conservative", data.get("release_decision") == "DO_NOT_ENABLE_PUBLIC_CUSTOMER_VIEW_YET", data.get("release_decision"))
        labels = " ".join(data.get("customer_labels", [])).lower()
        for label in ["current price", "breakeven", "max profit", "downside cushion", "assignment zone"]:
            add_result(results, f"Customer label present: {label}", label in labels, label)
        add_result(results, "Guardrails present", len(data.get("guardrails", [])) >= 4, len(data.get("guardrails", [])))
        add_result(results, "Release requirements present", len(data.get("release_requirements", [])) >= 5, len(data.get("release_requirements", [])))
    except Exception as exc:
        add_result(results, "Phase 3G-6 module imports and renders", False, repr(exc))
        data = {}

    marker_checks = {
        "Phase 3D markers remain present": "Phase 3D" in dashboard_text,
        "Phase 3E marker remains present": "PHASE3E_7C_DEVELOPER_TAB_READY" in dashboard_text,
        "Phase 3F marker remains present": "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY" in dashboard_text,
        "Phase 3G-4 public route marker remains present": "PHASE3G_4_PUBLIC_ROUTE_READY" in dashboard_text or "PHASE3G_4_PUBLIC_CUSTOMER_ENABLED" in dashboard_text,
        "Public Customer view is not enabled": "PHASE3G_PUBLIC_CUSTOMER_ENABLED = True" not in dashboard_text and "PUBLIC_CUSTOMER_ENABLED = True" not in dashboard_text,
    }
    for name, passed in marker_checks.items():
        add_result(results, name, passed, "marker search")

    for report_path in EXPECTED_PRIOR_REPORTS:
        add_result(results, f"Prior report exists: {report_path.name}", report_path.exists(), report_path)

    all_pass = all(r["passed"] for r in results)

    with CHECKPOINT_REPORT.open("w", encoding="utf-8") as f:
        f.write("Phase 3G-6 final pre-activation decision gate check\n")
        f.write("=" * 100 + "\n")
        for r in results:
            status = "PASS" if r["passed"] else "FAIL"
            f.write(f"{status:<10} {r['name']:<70} {r['detail']}\n")
        f.write("\n")
        f.write(f"Overall Phase 3G-6 checkpoint status: {'PASS' if all_pass else 'FAIL'}\n")

    CHECKPOINT_JSON.write_text(json.dumps({"passed": all_pass, "results": results, "model": data}, indent=2), encoding="utf-8")

    with CHECKLIST_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "passed", "detail"])
        writer.writeheader()
        writer.writerows(results)

    decision = "DO_NOT_ENABLE_PUBLIC_CUSTOMER_VIEW_YET"
    DECISION_TXT.write_text(
        "Phase 3G-6 public Customer-view release decision\n"
        "================================================\n\n"
        f"Decision: {decision}\n\n"
        "Reason: Phase 3G-6 is a final pre-activation gate. Public activation must be a separate explicit checkpoint/package.\n",
        encoding="utf-8",
    )

    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"{status:<10} {r['name']:<70} {r['detail']}")

    print("\n" + "=" * 100)
    print(f"Overall Phase 3G-6 checkpoint status: {'PASS' if all_pass else 'FAIL'}")
    print("=" * 100)
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")
    print(f"Saved checklist CSV:     {CHECKLIST_CSV}")
    print(f"Saved decision report:   {DECISION_TXT}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
