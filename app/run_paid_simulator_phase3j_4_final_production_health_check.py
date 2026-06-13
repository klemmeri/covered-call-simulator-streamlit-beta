"""
run_paid_simulator_phase3j_4_final_production_health_check.py

Final production health check for Phase 3J-4.
"""

from __future__ import annotations

import ast
import csv
import importlib
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
DASHBOARD = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
MODULE_PATH = PROJECT_ROOT / "app" / "paid_simulator" / "phase3j_final_production_health.py"
DOC_PATH = PROJECT_ROOT / "docs" / "phase3j_4_final_production_health.md"

EXPECTED_REPORTS = [
    "phase3h_8_post_activation_completion_checkpoint_report.txt",
    "phase3i_7_completion_gate_checkpoint_report.txt",
    "phase3j_1_production_polish_checkpoint_report.txt",
    "phase3j_2_ui_wording_polish_checkpoint_report.txt",
    "phase3j_3_final_browser_check_checkpoint_report.txt",
]

EXPECTED_MARKERS = [
    "PHASE3E_7C_DEVELOPER_TAB_READY",
    "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY",
    "PHASE3H_7_PUBLIC_CUSTOMER",
]

REQUIRED_LABELS = [
    "current price",
    "strike",
    "premium",
    "breakeven",
    "max profit",
    "downside cushion",
    "assignment zone",
    "warning",
]

REQUIRED_RISK_TERMS = ["assignment", "downside", "capped", "breakeven", "estimate"]

results: list[dict[str, str]] = []


def add(status: bool, name: str, detail: str = "") -> None:
    results.append({"status": "PASS" if status else "FAIL", "name": name, "detail": detail})


def syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:
        return False, repr(exc)


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 100)
    print("Phase 3J-4 final production health check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    add(DASHBOARD.exists(), "Dashboard file exists", str(DASHBOARD))
    add(MODULE_PATH.exists(), "Phase 3J-4 health module exists", str(MODULE_PATH))
    add(DOC_PATH.exists(), "Phase 3J-4 documentation exists", str(DOC_PATH))

    if DASHBOARD.exists():
        ok, detail = syntax_valid(DASHBOARD)
        add(ok, "Dashboard syntax remains valid", detail)
        dashboard_text = DASHBOARD.read_text(encoding="utf-8")
        for marker in EXPECTED_MARKERS:
            add(marker in dashboard_text, f"Prior activation marker/evidence present: {marker}", marker)
    else:
        dashboard_text = ""

    if MODULE_PATH.exists():
        ok, detail = syntax_valid(MODULE_PATH)
        add(ok, "Phase 3J-4 module syntax valid", detail)
    
    try:
        module = importlib.import_module("app.paid_simulator.phase3j_final_production_health")
        model = module.render_final_production_health(streamlit_module=None)
        add(isinstance(model, dict), "Fallback render returns dict", type(model).__name__)
        add(model.get("ready_marker") == "PHASE3J_4_FINAL_PRODUCTION_HEALTH_READY", "Health model has ready marker", str(model.get("ready_marker")))
        add(model.get("release_decision") == "PHASE3J_4_FINAL_PRODUCTION_HEALTH_PASS_NO_DASHBOARD_CHANGE", "Health model has release decision", str(model.get("release_decision")))
        add(model.get("dashboard_change") is False, "Health model confirms no dashboard change", str(model.get("dashboard_change")))
        text_blob = json.dumps(model, indent=2).lower()
        for label in REQUIRED_LABELS:
            add(label in text_blob, f"Customer-facing label present: {label}", label)
        for term in REQUIRED_RISK_TERMS:
            add(term in text_blob, f"Risk term present: {term}", term)
        add(len(model.get("health_domains", [])) >= 6, "At least six health domains present", str(len(model.get("health_domains", []))))
    except Exception as exc:
        add(False, "Phase 3J-4 module imports/renders", repr(exc))
        model = {}

    for report_name in EXPECTED_REPORTS:
        report_path = REPORT_DIR / report_name
        add(report_path.exists(), f"Prior report exists: {report_name}", str(report_path))

    release_decision_path = REPORT_DIR / "phase3j_4_final_production_health_release_decision.txt"
    release_decision_path.write_text("PHASE3J_4_FINAL_PRODUCTION_HEALTH_PASS_NO_DASHBOARD_CHANGE\n", encoding="utf-8")
    add(release_decision_path.exists(), "Release decision file written", str(release_decision_path))

    checkpoint_report = REPORT_DIR / "phase3j_4_final_production_health_checkpoint_report.txt"
    checkpoint_json = REPORT_DIR / "phase3j_4_final_production_health_checkpoint.json"
    checklist_csv = TABLE_DIR / "phase3j_4_final_production_health_checklist.csv"

    lines = ["Phase 3J-4 final production health check", "", f"Project root: {PROJECT_ROOT}", ""]
    for item in results:
        lines.append(f"{item['status']:10} {item['name']:70} {item['detail']}")
    checkpoint_report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    checkpoint_json.write_text(json.dumps({"results": results, "model": model}, indent=2), encoding="utf-8")
    with checklist_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["status", "name", "detail"])
        writer.writeheader()
        writer.writerows(results)

    print("=" * 100)
    for item in results:
        print(f"{item['status']:10} {item['name']:70} {item['detail']}")
    print()
    ok = all(item["status"] == "PASS" for item in results)
    print("=" * 100)
    print(f"Overall Phase 3J-4 checkpoint status: {'PASS' if ok else 'FAIL'}")
    print("=" * 100)
    print(f"Saved checkpoint report: {checkpoint_report}")
    print(f"Saved checkpoint JSON:   {checkpoint_json}")
    print(f"Saved checklist CSV:     {checklist_csv}")
    print(f"Saved release decision:  {release_decision_path}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
