"""
Phase 3H-6 final activation-review gate check.
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

DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase3h_final_activation_review_gate.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase3h_6_final_activation_review_gate.md"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_FILE = REPORT_DIR / "phase3h_6_final_activation_review_checkpoint_report.txt"
JSON_FILE = REPORT_DIR / "phase3h_6_final_activation_review_checkpoint.json"
CSV_FILE = TABLE_DIR / "phase3h_6_final_activation_review_checklist.csv"
DECISION_FILE = REPORT_DIR / "phase3h_6_final_activation_review_release_decision.txt"

EXPECTED_DECISION = "PHASE3H_6_FINAL_REVIEW_READY_PUBLIC_CUSTOMER_VIEW_STILL_DISABLED"

PRIOR_REPORTS = [
    "phase3g_8_completion_gate_checkpoint_report.txt",
    "phase3h_1_activation_switch_checkpoint_report.txt",
    "phase3h_2_activation_route_checkpoint_report.txt",
    "phase3h_3_activation_route_smoke_test_checkpoint_report.txt",
    "phase3h_4_pre_activation_validation_checkpoint_report.txt",
    "phase3h_5_activation_readiness_checkpoint_report.txt",
]


def syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:  # pragma: no cover
        return False, repr(exc)


def add(rows: list[dict], label: str, passed: bool, detail: str) -> None:
    rows.append({"label": label, "status": "PASS" if passed else "FAIL", "detail": detail})


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []

    print("=" * 100)
    print("Phase 3H-6 final activation-review gate check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    add(rows, "Dashboard file exists", DASHBOARD_FILE.exists(), str(DASHBOARD_FILE))
    add(rows, "Phase 3H-6 module exists", MODULE_FILE.exists(), str(MODULE_FILE))
    add(rows, "Phase 3H-6 documentation exists", DOC_FILE.exists(), str(DOC_FILE))

    if DASHBOARD_FILE.exists():
        ok, detail = syntax_valid(DASHBOARD_FILE)
        add(rows, "Dashboard syntax remains valid", ok, detail)
        text = DASHBOARD_FILE.read_text(encoding="utf-8")
        add(rows, "Public Customer view remains disabled", "PUBLIC_CUSTOMER_ENABLED = True" not in text and "PHASE3H_2_PUBLIC_CUSTOMER_ENABLED = False" in text, "customer protected")
        add(rows, "Phase 3H route marker/evidence present", "PHASE3H" in text or (REPORT_DIR / "phase3h_2_activation_route_checkpoint_report.txt").exists(), "Phase 3H evidence")
        add(rows, "Phase 3G marker remains present", "PHASE3G" in text, "Phase 3G marker search")
        add(rows, "Phase 3F marker remains present", "PHASE3F" in text, "Phase 3F marker search")
        add(rows, "Phase 3E marker remains present", "PHASE3E" in text, "Phase 3E marker search")
        add(rows, "Phase 3D markers remain present", "Phase 3D" in text or "phase3d" in text.lower(), "Phase 3D marker search")

    if MODULE_FILE.exists():
        ok, detail = syntax_valid(MODULE_FILE)
        add(rows, "Phase 3H-6 module syntax valid", ok, detail)

    try:
        module = importlib.import_module("app.paid_simulator.phase3h_final_activation_review_gate")
        model = module.render_phase3h_6_final_activation_review(streamlit_module=None)
        add(rows, "Phase 3H-6 module imports and renders", isinstance(model, dict), type(model).__name__)
        add(rows, "Final-review model has ready marker", model.get("marker") == "PHASE3H_6_FINAL_ACTIVATION_REVIEW_READY", str(model.get("marker")))
        add(rows, "Final-review model keeps public Customer view disabled", model.get("public_customer_enabled") is False, str(model.get("public_customer_enabled")))
        add(rows, "Final-review model has conservative release decision", model.get("release_decision") == EXPECTED_DECISION, str(model.get("release_decision")))
        add(rows, "Final-review model has guardrails", len(model.get("guardrails", [])) >= 5, str(len(model.get("guardrails", []))))
        for label in ["current price", "breakeven", "max profit", "downside cushion", "assignment zone", "warning"]:
            labels = " ".join(model.get("customer_labels", [])).lower()
            add(rows, f"Customer-facing label present: {label}", label in labels, label)
    except Exception as exc:
        add(rows, "Phase 3H-6 module imports and renders", False, repr(exc))
        model = {}

    for filename in PRIOR_REPORTS:
        path = REPORT_DIR / filename
        add(rows, f"Prior report exists: {filename}", path.exists(), str(path))

    DECISION_FILE.write_text(EXPECTED_DECISION + "\n", encoding="utf-8")
    add(rows, "Final activation-review decision file written", DECISION_FILE.exists(), str(DECISION_FILE))

    passed = all(row["status"] == "PASS" for row in rows)

    with REPORT_FILE.open("w", encoding="utf-8") as f:
        f.write("Phase 3H-6 final activation-review gate check\n")
        f.write("=" * 100 + "\n")
        for row in rows:
            f.write(f"{row['status']:<10} {row['label']:<70} {row['detail']}\n")
        f.write("\n")
        f.write(f"Overall Phase 3H-6 checkpoint status: {'PASS' if passed else 'FAIL'}\n")

    JSON_FILE.write_text(json.dumps({"passed": passed, "rows": rows, "release_decision": EXPECTED_DECISION}, indent=2), encoding="utf-8")
    with CSV_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["status", "label", "detail"])
        writer.writeheader()
        writer.writerows(rows)

    for row in rows:
        print(f"{row['status']:<10} {row['label']:<70} {row['detail']}")
    print()
    print("=" * 100)
    print(f"Overall Phase 3H-6 checkpoint status: {'PASS' if passed else 'FAIL'}")
    print("=" * 100)
    print(f"Saved checkpoint report: {REPORT_FILE}")
    print(f"Saved checkpoint JSON:   {JSON_FILE}")
    print(f"Saved checklist CSV:     {CSV_FILE}")
    print(f"Saved release decision:  {DECISION_FILE}")

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
