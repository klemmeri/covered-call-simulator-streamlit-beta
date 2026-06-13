"""
run_paid_simulator_phase3h_4_pre_activation_validation_check.py

Phase 3H-4 protected pre-activation validation check.
"""
from __future__ import annotations

import ast
import csv
import importlib
import json
from pathlib import Path
import sys
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase3h_protected_pre_activation_validation.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase3h_4_protected_pre_activation_validation.md"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_FILE = REPORT_DIR / "phase3h_4_pre_activation_validation_checkpoint_report.txt"
JSON_FILE = REPORT_DIR / "phase3h_4_pre_activation_validation_checkpoint.json"
CSV_FILE = TABLE_DIR / "phase3h_4_pre_activation_validation_checklist.csv"
DECISION_FILE = REPORT_DIR / "phase3h_4_pre_activation_validation_release_decision.txt"

REQUIRED_REPORTS = [
    "phase3g_8_completion_gate_checkpoint_report.txt",
    "phase3h_1_activation_switch_checkpoint_report.txt",
    "phase3h_2_activation_route_checkpoint_report.txt",
    "phase3h_3_activation_route_smoke_test_checkpoint_report.txt",
]


def syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:
        return False, repr(exc)


def contains(path: Path, text: str) -> bool:
    if not path.exists():
        return False
    return text in path.read_text(encoding="utf-8", errors="ignore")


def add(results, ok: bool, label: str, detail: str = ""):
    results.append({"status": "PASS" if ok else "FAIL", "label": label, "detail": detail})


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    add(results, DASHBOARD_FILE.exists(), "Dashboard file exists", str(DASHBOARD_FILE))
    add(results, MODULE_FILE.exists(), "Phase 3H-4 validation module exists", str(MODULE_FILE))
    add(results, DOC_FILE.exists(), "Phase 3H-4 documentation exists", str(DOC_FILE))

    if DASHBOARD_FILE.exists():
        ok, detail = syntax_valid(DASHBOARD_FILE)
        add(results, ok, "Dashboard syntax remains valid", detail)
        dashboard_text = DASHBOARD_FILE.read_text(encoding="utf-8", errors="ignore")
        add(results, "PHASE3H_2_PUBLIC_CUSTOMER_ENABLED = False" in dashboard_text or "PHASE3H_2_PUBLIC_CUSTOMER_ENABLED=False" in dashboard_text,
            "Phase 3H public Customer view remains disabled", "customer protected")
        add(results, "PHASE3H" in dashboard_text, "Phase 3H dashboard evidence remains present", "Phase 3H marker search")
        add(results, "PHASE3G" in dashboard_text, "Phase 3G marker remains present", "Phase 3G marker search")
        add(results, "PHASE3F" in dashboard_text, "Phase 3F marker remains present", "Phase 3F marker search")
        add(results, "PHASE3E" in dashboard_text, "Phase 3E marker remains present", "Phase 3E marker search")
        add(results, "Phase 3D" in dashboard_text or "phase3d" in dashboard_text.lower(), "Phase 3D markers remain present", "Phase 3D marker search")

    if MODULE_FILE.exists():
        ok, detail = syntax_valid(MODULE_FILE)
        add(results, ok, "Phase 3H-4 module syntax valid", detail)
        try:
            module = importlib.import_module("app.paid_simulator.phase3h_protected_pre_activation_validation")
            model = module.render_phase3h_4_validation(streamlit_module=None)
            add(results, isinstance(model, dict), "Fallback render returns dict", type(model).__name__)
            add(results, model.get("marker") == "PHASE3H_4_PROTECTED_PRE_ACTIVATION_READY", "Validation model has ready marker", str(model.get("marker")))
            add(results, model.get("public_customer_enabled") is False, "Validation model keeps public Customer view disabled", str(model.get("public_customer_enabled")))
            add(results, model.get("release_decision") == "PHASE3H_4_PRE_ACTIVATION_VALIDATED_PUBLIC_CUSTOMER_VIEW_DISABLED", "Validation model has conservative release decision", str(model.get("release_decision")))
            guardrails = model.get("guardrails", [])
            add(results, isinstance(guardrails, list) and len(guardrails) >= 5, "Validation model has guardrails", str(len(guardrails)))
            labels_text = " ".join(model.get("customer_labels", [])).lower()
            for label in ["current price", "breakeven", "max profit", "downside cushion", "assignment zone", "warning"]:
                add(results, label in labels_text, f"Customer-facing label present: {label}", label)
            DECISION_FILE.write_text(model.get("release_decision", ""), encoding="utf-8")
            add(results, DECISION_FILE.exists(), "Release-decision file written", str(DECISION_FILE))
        except Exception as exc:
            add(results, False, "Phase 3H-4 module imports and renders", repr(exc))

    for report_name in REQUIRED_REPORTS:
        report_path = REPORT_DIR / report_name
        add(results, report_path.exists(), f"Prior report exists: {report_name}", str(report_path))

    passed = all(row["status"] == "PASS" for row in results)

    lines = []
    title = "Phase 3H-4 protected pre-activation validation check"
    lines.append("=" * 100)
    lines.append(title)
    lines.append("=" * 100)
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append("")
    for row in results:
        lines.append(f"{row['status']:<10} {row['label']:<70} {row['detail']}")
    lines.append("")
    lines.append("=" * 100)
    lines.append(f"Overall Phase 3H-4 checkpoint status: {'PASS' if passed else 'FAIL'}")
    lines.append("=" * 100)

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
    JSON_FILE.write_text(json.dumps({"passed": passed, "results": results, "timestamp": datetime.now().isoformat()}, indent=2), encoding="utf-8")
    with CSV_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["status", "label", "detail"])
        writer.writeheader()
        writer.writerows(results)

    print("\n".join(lines))
    print(f"Saved checkpoint report: {REPORT_FILE}")
    print(f"Saved checkpoint JSON:   {JSON_FILE}")
    print(f"Saved checklist CSV:     {CSV_FILE}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
