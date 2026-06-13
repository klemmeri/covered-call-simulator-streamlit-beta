"""
run_paid_simulator_phase3g_5_route_smoke_test_check.py

Phase 3G-5 public Customer-view route smoke-test checkpoint.
"""

from __future__ import annotations

import ast
import csv
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)

CHECK_REPORT = REPORT_DIR / "phase3g_5_route_smoke_test_checkpoint_report.txt"
CHECK_JSON = REPORT_DIR / "phase3g_5_route_smoke_test_checkpoint.json"
CHECK_CSV = TABLE_DIR / "phase3g_5_route_smoke_test_checklist.csv"
DECISION_REPORT = REPORT_DIR / "phase3g_5_public_route_promotion_decision.txt"

EXPECTED_FILES = [
    APP_DIR / "paid_simulator" / "phase3g_public_customer_route_smoke_test.py",
    APP_DIR / "run_paid_simulator_phase3g_5_route_smoke_test_check.py",
    PROJECT_ROOT / "docs" / "phase3g_5_public_route_smoke_test.md",
]

DASHBOARD_FILE = APP_DIR / "paid_simulator" / "config_form_app.py"
PRIOR_REPORTS = [
    REPORT_DIR / "phase3e_9_completion_checkpoint_report.txt",
    REPORT_DIR / "phase3f_8_completion_gate_checkpoint_report.txt",
    REPORT_DIR / "phase3g_1_public_release_gate_checkpoint_report.txt",
]

checks: list[dict[str, Any]] = []


def add_check(name: str, passed: bool, detail: Any = "") -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": str(detail)})


def syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:  # pragma: no cover - checkpoint diagnostic
        return False, repr(exc)


def import_module_from_path(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    print("=" * 100)
    print("Phase 3G-5 public Customer-view route smoke-test check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    print("Expected files")
    print("-" * 100)
    for path in EXPECTED_FILES:
        add_check(path.name, path.exists(), path)

    print("\nDashboard and module syntax")
    print("-" * 100)
    add_check("Dashboard file exists", DASHBOARD_FILE.exists(), DASHBOARD_FILE)
    if DASHBOARD_FILE.exists():
        ok, detail = syntax_valid(DASHBOARD_FILE)
        add_check("Dashboard syntax valid", ok, detail)
        dashboard_text = DASHBOARD_FILE.read_text(encoding="utf-8", errors="ignore")
    else:
        dashboard_text = ""

    module_path = APP_DIR / "paid_simulator" / "phase3g_public_customer_route_smoke_test.py"
    ok, detail = syntax_valid(module_path)
    add_check("Phase 3G-5 smoke-test module syntax valid", ok, detail)

    print("\nModel import and behavior")
    print("-" * 100)
    try:
        module = import_module_from_path("phase3g_public_customer_route_smoke_test_check_import", module_path)
        model = module.build_public_route_smoke_test_model()
        data = model.to_dict()
        fallback = module.render_public_route_smoke_test(streamlit_module=None)
        add_check("Phase 3G-5 model imports and renders", True, "imported")
        add_check("Route smoke-test ready marker present", data.get("marker") == "PHASE3G_5_PUBLIC_ROUTE_SMOKE_TEST_READY", data.get("marker"))
        add_check("Public Customer view remains disabled", data.get("public_customer_enabled") is False, data.get("public_customer_enabled"))
        add_check("Protected preview remains required", data.get("protected_preview_required") is True, data.get("protected_preview_required"))
        add_check("Release decision remains DO NOT ENABLE", data.get("public_release_decision") == "DO_NOT_ENABLE_PUBLIC_CUSTOMER_VIEW_YET", data.get("public_release_decision"))
        add_check("Route smoke tests present", len(data.get("route_smoke_tests", [])) >= 4, len(data.get("route_smoke_tests", [])))
        add_check("Guardrails present", len(data.get("guardrails", [])) >= 4, len(data.get("guardrails", [])))
        add_check("Promotion criteria present", len(data.get("promotion_criteria", [])) >= 4, len(data.get("promotion_criteria", [])))
        add_check("Fallback render returns dictionary", isinstance(fallback, dict), type(fallback).__name__)
        label_blob = "\n".join(data.get("customer_facing_labels", [])).lower()
        for label in ["current price", "breakeven", "max profit", "downside cushion", "assignment zone"]:
            add_check(f"Customer-facing label present: {label}", label in label_blob, label)
    except Exception as exc:
        add_check("Phase 3G-5 model imports and renders", False, repr(exc))

    print("\nDashboard markers and customer protection")
    print("-" * 100)
    add_check("Phase 3G-4 dashboard readiness marker present", "PHASE3G_4_PUBLIC_CUSTOMER_ROUTE_READY" in dashboard_text or "PHASE3G_4_PUBLIC_ROUTE_READY" in dashboard_text, "Phase 3G-4 marker search")
    add_check("Phase 3F-3 dashboard marker present", "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY" in dashboard_text, "Phase 3F-3 marker search")
    add_check("Phase 3E dashboard marker present", "PHASE3E_7C_DEVELOPER_TAB_READY" in dashboard_text, "Phase 3E marker search")
    add_check("Phase 3D markers still present", "Phase 3D" in dashboard_text or "phase3d" in dashboard_text.lower(), "Phase 3D marker search")
    add_check("Customer-view markers still present", "Customer" in dashboard_text or "customer" in dashboard_text.lower(), "Customer marker search")
    forbidden_enabled = "PHASE3G_4_PUBLIC_CUSTOMER_ENABLED = True" in dashboard_text or "PHASE3G_5_PUBLIC_CUSTOMER_ENABLED = True" in dashboard_text
    add_check("Public Customer view not prematurely enabled", not forbidden_enabled, "customer protected")

    print("\nPrior report availability")
    print("-" * 100)
    for path in PRIOR_REPORTS:
        add_check(f"Prior report exists: {path.name}", path.exists(), path)

    all_passed = all(item["passed"] for item in checks)

    with CHECK_REPORT.open("w", encoding="utf-8") as f:
        f.write("Phase 3G-5 public Customer-view route smoke-test checkpoint\n")
        f.write("=" * 80 + "\n\n")
        for item in checks:
            status = "PASS" if item["passed"] else "FAIL"
            f.write(f"{status:<8} {item['name']:<70} {item['detail']}\n")
        f.write("\n")
        f.write(f"Overall Phase 3G-5 checkpoint status: {'PASS' if all_passed else 'FAIL'}\n")

    with CHECK_JSON.open("w", encoding="utf-8") as f:
        json.dump({"phase": "3G-5", "passed": all_passed, "checks": checks}, f, indent=2)

    with CHECK_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["passed", "name", "detail"])
        writer.writeheader()
        for item in checks:
            writer.writerow(item)

    with DECISION_REPORT.open("w", encoding="utf-8") as f:
        f.write("Phase 3G-5 public route promotion decision\n")
        f.write("=" * 60 + "\n\n")
        f.write("Decision: DO NOT ENABLE PUBLIC CUSTOMER VIEW YET\n")
        f.write("Reason: Phase 3G-5 is a smoke-test and promotion-decision checkpoint only.\n")
        f.write("Next logical step: Phase 3G-6 controlled public activation switch package.\n")

    for item in checks:
        status = "PASS" if item["passed"] else "FAIL"
        print(f"{status:<10} {item['name']:<65} {item['detail']}")

    print("\n" + "=" * 100)
    print(f"Overall Phase 3G-5 checkpoint status: {'PASS' if all_passed else 'FAIL'}")
    print("=" * 100)
    print(f"Saved checkpoint report: {CHECK_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECK_JSON}")
    print(f"Saved checklist CSV:     {CHECK_CSV}")
    print(f"Saved decision report:   {DECISION_REPORT}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
