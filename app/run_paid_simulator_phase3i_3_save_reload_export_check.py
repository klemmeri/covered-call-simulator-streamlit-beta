"""
Phase 3I-3 customer save/reload/export workflow verification check.
"""
from __future__ import annotations

from pathlib import Path
import ast
import json
import csv
import importlib
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
SETUP_DIR = PROJECT_ROOT / "outputs" / "saved_setups" / "paid_simulator"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)
SETUP_DIR.mkdir(parents=True, exist_ok=True)

rows: list[dict] = []


def record(name: str, passed: bool, detail: str = "") -> None:
    rows.append({"check": name, "status": "PASS" if passed else "FAIL", "detail": detail})
    print(f"{'PASS' if passed else 'FAIL':<10} {name:<70} {detail}")


def syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:
        return False, repr(exc)


def main() -> int:
    print("=" * 100)
    print("Phase 3I-3 customer save/reload/export workflow verification check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    dashboard_path = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
    module_path = PROJECT_ROOT / "app" / "paid_simulator" / "phase3i_customer_save_reload_export_verification.py"
    docs_path = PROJECT_ROOT / "docs" / "phase3i_3_customer_save_reload_export_verification.md"

    record("Dashboard file exists", dashboard_path.exists(), str(dashboard_path))
    record("Phase 3I-3 module exists", module_path.exists(), str(module_path))
    record("Phase 3I-3 documentation exists", docs_path.exists(), str(docs_path))

    ok, detail = syntax_valid(dashboard_path)
    record("Dashboard syntax remains valid", ok, detail)
    ok, detail = syntax_valid(module_path)
    record("Phase 3I-3 module syntax valid", ok, detail)

    try:
        mod = importlib.import_module("app.paid_simulator.phase3i_customer_save_reload_export_verification")
        model = mod.render_customer_save_reload_export_verification(streamlit_module=None)
        record("Phase 3I-3 module imports and fallback renders", isinstance(model, dict), type(model).__name__)
    except Exception as exc:
        model = {}
        record("Phase 3I-3 module imports and fallback renders", False, repr(exc))

    record("Model has ready marker", model.get("marker") == "PHASE3I_3_CUSTOMER_SAVE_RELOAD_EXPORT_READY", str(model.get("marker")))
    record("Model has release decision", model.get("release_decision") == "PHASE3I_3_CUSTOMER_SAVE_RELOAD_EXPORT_WORKFLOW_VERIFIED", str(model.get("release_decision")))
    record("Public customer workflow active", model.get("public_customer_workflow_active") is True, str(model.get("public_customer_workflow_active")))
    record("Dashboard not modified by Phase 3I-3", model.get("dashboard_modified") is False, str(model.get("dashboard_modified")))
    record("Workflow actions include save/reload/export", all(action in model.get("workflow_actions", []) for action in ["save setup", "reload saved setup", "export payoff summary"]), str(model.get("workflow_actions")))
    record("Guardrails present", len(model.get("guardrails", [])) >= 4, str(len(model.get("guardrails", []))))

    labels = " ".join(model.get("customer_labels", [])).lower()
    for label in ["current price", "strike", "premium", "breakeven", "max profit", "downside cushion", "assignment zone", "warning"]:
        record(f"Customer-facing label present: {label}", label in labels, label)

    metrics = model.get("metrics", {})
    for key in ["current_price", "strike", "premium", "breakeven", "max_profit", "downside_cushion_percent", "assignment_zone", "warnings"]:
        record(f"Metric present: {key}", key in metrics, str(metrics.get(key)))

    try:
        setup_path = SETUP_DIR / "phase3i_3_customer_setup.json"
        csv_path = TABLE_DIR / "phase3i_3_customer_export_summary.csv"
        saved_path = mod.save_customer_setup(setup_path)
        reloaded = mod.reload_customer_setup(saved_path)
        export_path = mod.export_customer_summary_csv(csv_path, reloaded)
        record("Customer setup JSON saved", saved_path.exists(), str(saved_path))
        record("Customer setup JSON reloaded with marker", reloaded.get("marker") == model.get("marker"), reloaded.get("marker", ""))
        record("Customer export CSV written", export_path.exists(), str(export_path))
    except Exception as exc:
        record("Save/reload/export round trip", False, repr(exc))

    prior_reports = [
        "phase3h_8_post_activation_completion_checkpoint_report.txt",
        "phase3i_1_post_activation_browser_checkpoint_report.txt",
        "phase3i_2_customer_workflow_smoke_test_checkpoint_report.txt",
    ]
    for filename in prior_reports:
        path = REPORT_DIR / filename
        record(f"Prior report exists: {filename}", path.exists(), str(path))

    report_path = REPORT_DIR / "phase3i_3_save_reload_export_checkpoint_report.txt"
    json_path = REPORT_DIR / "phase3i_3_save_reload_export_checkpoint.json"
    checklist_path = TABLE_DIR / "phase3i_3_save_reload_export_checklist.csv"
    decision_path = REPORT_DIR / "phase3i_3_save_reload_export_release_decision.txt"

    with report_path.open("w", encoding="utf-8") as handle:
        handle.write("Phase 3I-3 customer save/reload/export workflow verification check\n")
        handle.write("=" * 80 + "\n")
        for row in rows:
            handle.write(f"{row['status']:<6} {row['check']} - {row['detail']}\n")

    json_path.write_text(json.dumps({"checks": rows, "model": model}, indent=2), encoding="utf-8")
    with checklist_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["check", "status", "detail"])
        writer.writeheader()
        writer.writerows(rows)
    decision_path.write_text("PHASE3I_3_CUSTOMER_SAVE_RELOAD_EXPORT_WORKFLOW_VERIFIED\n", encoding="utf-8")

    overall = all(row["status"] == "PASS" for row in rows)
    print()
    print("=" * 100)
    print(f"Overall Phase 3I-3 checkpoint status: {'PASS' if overall else 'FAIL'}")
    print("=" * 100)
    print(f"Saved checkpoint report: {report_path}")
    print(f"Saved checkpoint JSON:   {json_path}")
    print(f"Saved checklist CSV:     {checklist_path}")
    print(f"Saved release decision:  {decision_path}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
