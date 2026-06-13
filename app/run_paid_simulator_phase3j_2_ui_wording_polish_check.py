"""
run_paid_simulator_phase3j_2_ui_wording_polish_check.py

Checkpoint for Phase 3J-2 production UI wording and polish checklist.
"""

from __future__ import annotations

import ast
import csv
import importlib
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase3j_production_ui_wording_polish.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase3j_2_production_ui_wording_polish.md"

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

PRIOR_REPORTS = [
    "phase3h_8_post_activation_completion_checkpoint_report.txt",
    "phase3i_7_completion_gate_checkpoint_report.txt",
    "phase3j_1_production_polish_checkpoint_report.txt",
]


def syntax_valid(path: Path) -> bool:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True
    except Exception:
        return False


def record(rows: list[dict], passed: bool, label: str, detail: str = "") -> None:
    rows.append({"status": "PASS" if passed else "FAIL", "label": label, "detail": detail})
    print(f"{'PASS' if passed else 'FAIL':<10} {label:<70} {detail}")


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 100)
    print("Phase 3J-2 production UI wording and polish check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}\n")

    rows: list[dict] = []

    record(rows, DASHBOARD_FILE.exists(), "Dashboard file exists", str(DASHBOARD_FILE))
    record(rows, MODULE_FILE.exists(), "Phase 3J-2 wording/polish module exists", str(MODULE_FILE))
    record(rows, DOC_FILE.exists(), "Phase 3J-2 documentation exists", str(DOC_FILE))

    if DASHBOARD_FILE.exists():
        record(rows, syntax_valid(DASHBOARD_FILE), "Dashboard syntax remains valid", "syntax valid")
    else:
        record(rows, False, "Dashboard syntax remains valid", "dashboard missing")

    if MODULE_FILE.exists():
        record(rows, syntax_valid(MODULE_FILE), "Phase 3J-2 module syntax valid", "syntax valid")
    else:
        record(rows, False, "Phase 3J-2 module syntax valid", "module missing")

    model = {}
    try:
        module = importlib.import_module("app.paid_simulator.phase3j_production_ui_wording_polish")
        model = module.render_ui_wording_polish(streamlit_module=None)
        record(rows, isinstance(model, dict), "Fallback render returns dict", "dict")
    except Exception as exc:
        record(rows, False, "Phase 3J-2 module imports and renders", repr(exc))

    text = json.dumps(model, indent=2).lower() if model else ""
    record(rows, model.get("marker") == "PHASE3J_2_PRODUCTION_UI_WORDING_POLISH_READY", "Wording model has ready marker", str(model.get("marker")))
    record(rows, model.get("release_decision") == "PHASE3J_2_UI_WORDING_POLISH_CHECKLIST_CREATED_NO_DASHBOARD_CHANGE", "Wording model has release decision", str(model.get("release_decision")))
    record(rows, model.get("dashboard_changed") is False, "Wording model declares no dashboard change", str(model.get("dashboard_changed")))

    for label in EXPECTED_LABELS:
        record(rows, label in text, f"Customer-facing label present: {label}", label)

    record(rows, len(model.get("polish_areas", [])) >= 4, "At least four polish areas present", str(len(model.get("polish_areas", []))))
    record(rows, len(model.get("guardrails", [])) >= 3, "At least three production guardrails present", str(len(model.get("guardrails", []))))

    dashboard_text = DASHBOARD_FILE.read_text(encoding="utf-8", errors="replace") if DASHBOARD_FILE.exists() else ""
    for marker, label in [
        ("PHASE3E_7C_DEVELOPER_TAB_READY", "Phase 3E marker remains present"),
        ("PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY", "Phase 3F marker remains present"),
        ("PHASE3H", "Phase 3H marker/evidence remains present"),
    ]:
        record(rows, marker in dashboard_text, label, marker)

    for report_name in PRIOR_REPORTS:
        report_path = REPORT_DIR / report_name
        record(rows, report_path.exists(), f"Prior report exists: {report_name}", str(report_path))

    report_path = REPORT_DIR / "phase3j_2_ui_wording_polish_checkpoint_report.txt"
    json_path = REPORT_DIR / "phase3j_2_ui_wording_polish_checkpoint.json"
    csv_path = TABLE_DIR / "phase3j_2_ui_wording_polish_checklist.csv"
    decision_path = REPORT_DIR / "phase3j_2_ui_wording_polish_release_decision.txt"

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["status", "label", "detail"])
        writer.writeheader()
        writer.writerows(rows)

    status = "PASS" if all(row["status"] == "PASS" for row in rows) else "FAIL"
    report_text = [
        "Phase 3J-2 production UI wording and polish check",
        f"Overall Phase 3J-2 checkpoint status: {status}",
        "",
    ]
    report_text.extend(f"{row['status']:<8} {row['label']} {row['detail']}" for row in rows)
    report_path.write_text("\n".join(report_text), encoding="utf-8")
    json_path.write_text(json.dumps({"status": status, "checks": rows, "model": model}, indent=2), encoding="utf-8")
    decision_path.write_text(str(model.get("release_decision", "PHASE3J_2_CHECK_FAILED")), encoding="utf-8")

    print("\n" + "=" * 100)
    print(f"Overall Phase 3J-2 checkpoint status: {status}")
    print("=" * 100)
    print(f"Saved checkpoint report: {report_path}")
    print(f"Saved checkpoint JSON:   {json_path}")
    print(f"Saved checklist CSV:     {csv_path}")
    print(f"Saved release decision:  {decision_path}")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
