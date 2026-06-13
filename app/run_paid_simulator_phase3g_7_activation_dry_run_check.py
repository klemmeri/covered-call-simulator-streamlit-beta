"""
Phase 3G-7 public customer activation dry-run check.

This script validates the dry-run activation model and confirms that public
Customer-view enablement remains disabled.
"""

from __future__ import annotations

import ast
import csv
import importlib.util
import json
from pathlib import Path
import sys
import traceback

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase3g_public_customer_activation_dry_run.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase3g_7_public_activation_dry_run.md"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_PATH = REPORT_DIR / "phase3g_7_activation_dry_run_checkpoint_report.txt"
JSON_PATH = REPORT_DIR / "phase3g_7_activation_dry_run_checkpoint.json"
CSV_PATH = TABLE_DIR / "phase3g_7_activation_dry_run_checklist.csv"
DECISION_PATH = REPORT_DIR / "phase3g_7_activation_dry_run_release_decision.txt"

PRIOR_REPORTS = [
    REPORT_DIR / "phase3e_9_completion_checkpoint_report.txt",
    REPORT_DIR / "phase3f_8_completion_gate_checkpoint_report.txt",
    REPORT_DIR / "phase3g_1_public_release_gate_checkpoint_report.txt",
    REPORT_DIR / "phase3g_5_public_route_promotion_decision.txt",
    REPORT_DIR / "phase3g_6_final_pre_activation_release_decision.txt",
]


def add(results, status, label, detail):
    results.append({"status": status, "label": label, "detail": str(detail)})


def syntax_valid(path):
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:
        return False, repr(exc)


def import_module_from_path(path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main():
    results = []
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 100)
    print("Phase 3G-7 public customer activation dry-run check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    for label, path in [
        ("phase3g_public_customer_activation_dry_run.py", MODULE_FILE),
        ("run_paid_simulator_phase3g_7_activation_dry_run_check.py", Path(__file__).resolve()),
        ("phase3g_7_public_activation_dry_run.md", DOC_FILE),
        ("config_form_app.py", DASHBOARD_FILE),
    ]:
        add(results, "PASS" if path.exists() else "FAIL", label, path)

    for label, path in [("Dashboard syntax valid", DASHBOARD_FILE), ("Activation dry-run module syntax valid", MODULE_FILE)]:
        if path.exists():
            ok, detail = syntax_valid(path)
            add(results, "PASS" if ok else "FAIL", label, detail)
        else:
            add(results, "FAIL", label, "missing file")

    try:
        module = import_module_from_path(MODULE_FILE, "phase3g_public_customer_activation_dry_run_check_import")
        model = module.build_phase3g_public_activation_dry_run_model()
        model_dict = model.to_dict()
        rendered = module.render_phase3g_public_activation_dry_run(streamlit_module=None)
        add(results, "PASS", "Activation dry-run module imports and renders", "imported")
        add(results, "PASS" if model_dict.get("marker") == "PHASE3G_7_PUBLIC_ACTIVATION_DRY_RUN_READY" else "FAIL", "Dry-run model has ready marker", model_dict.get("marker"))
        add(results, "PASS" if model_dict.get("public_customer_enabled") is False else "FAIL", "Public Customer view remains disabled", model_dict.get("public_customer_enabled"))
        add(results, "PASS" if model_dict.get("protected_preview_required") is True else "FAIL", "Protected preview remains required", model_dict.get("protected_preview_required"))
        add(results, "PASS" if model_dict.get("release_decision") == "DRY_RUN_ONLY_DO_NOT_ENABLE_PUBLIC_CUSTOMER_VIEW" else "FAIL", "Dry-run release decision is conservative", model_dict.get("release_decision"))
        add(results, "PASS" if len(model_dict.get("customer_labels", [])) >= 6 else "FAIL", "Customer-facing labels present", len(model_dict.get("customer_labels", [])))
        add(results, "PASS" if len(model_dict.get("guardrails", [])) >= 4 else "FAIL", "Activation guardrails present", len(model_dict.get("guardrails", [])))
        add(results, "PASS" if isinstance(rendered, dict) and rendered.get("marker") == model_dict.get("marker") else "FAIL", "Fallback render returns dry-run dict", type(rendered).__name__)
    except Exception as exc:
        add(results, "FAIL", "Activation dry-run module imports and renders", repr(exc))
        add(results, "FAIL", "Activation dry-run traceback", traceback.format_exc())
        model_dict = {}

    dashboard_text = DASHBOARD_FILE.read_text(encoding="utf-8") if DASHBOARD_FILE.exists() else ""
    dashboard_checks = [
        ("Phase 3D markers remain present", "Phase 3D" in dashboard_text),
        ("Phase 3E Developer marker remains present", "PHASE3E_7C_DEVELOPER_TAB_READY" in dashboard_text),
        ("Phase 3F preview marker remains present", "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY" in dashboard_text),
        ("Phase 3G route readiness marker remains present", "PHASE3G_4_PUBLIC_ROUTE_READINESS_READY" in dashboard_text or "PHASE3G_4_PUBLIC_CUSTOMER_ENABLED" in dashboard_text),
        ("Public Customer flag is not enabled", "PHASE3G_4_PUBLIC_CUSTOMER_ENABLED = True" not in dashboard_text),
        ("Ordinary Customer view not marked as Phase 3E enabled", "CUSTOMER_VIEW_PHASE3E_ENABLED = True" not in dashboard_text),
        ("Ordinary Customer view not marked as Phase 3F enabled", "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_CUSTOMER_ENABLED = True" not in dashboard_text),
    ]
    for label, ok in dashboard_checks:
        add(results, "PASS" if ok else "FAIL", label, ok)

    for prior in PRIOR_REPORTS:
        add(results, "PASS" if prior.exists() else "WARN", f"Prior report available: {prior.name}", prior)

    decision = "DRY_RUN_ONLY_DO_NOT_ENABLE_PUBLIC_CUSTOMER_VIEW"
    if model_dict and model_dict.get("public_customer_enabled") is True:
        decision = "FAIL_PUBLIC_CUSTOMER_VIEW_WAS_ENABLED"
    DECISION_PATH.write_text(decision + "\n", encoding="utf-8")
    add(results, "PASS" if decision.startswith("DRY_RUN_ONLY") else "FAIL", "Release decision written", DECISION_PATH)

    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["status", "label", "detail"])
        writer.writeheader()
        writer.writerows(results)

    JSON_PATH.write_text(json.dumps({"results": results, "decision": decision}, indent=2), encoding="utf-8")

    lines = []
    lines.append("Phase 3G-7 public customer activation dry-run check")
    lines.append("=" * 100)
    for row in results:
        lines.append(f"{row['status']:<10} {row['label']:<70} {row['detail']}")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    for row in results:
        print(f"{row['status']:<10} {row['label']:<70} {row['detail']}")

    failing = [r for r in results if r["status"] == "FAIL"]
    print()
    print("=" * 100)
    if failing:
        print("Overall Phase 3G-7 checkpoint status: FAIL")
        print("=" * 100)
        print(f"Saved checkpoint report: {REPORT_PATH}")
        print(f"Saved checkpoint JSON:   {JSON_PATH}")
        print(f"Saved checklist CSV:     {CSV_PATH}")
        print(f"Saved release decision:  {DECISION_PATH}")
        sys.exit(1)
    print("Overall Phase 3G-7 checkpoint status: PASS")
    print("=" * 100)
    print(f"Saved checkpoint report: {REPORT_PATH}")
    print(f"Saved checkpoint JSON:   {JSON_PATH}")
    print(f"Saved checklist CSV:     {CSV_PATH}")
    print(f"Saved release decision:  {DECISION_PATH}")


if __name__ == "__main__":
    main()
