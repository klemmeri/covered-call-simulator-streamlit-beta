"""
Phase 3G-2 public Customer-view activation-plan checkpoint.

Run from PyCharm or command line:
    python app/run_paid_simulator_phase3g_2_activation_plan_check.py
"""
from __future__ import annotations

import ast
import importlib.util
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)

CHECKS: list[tuple[str, bool, str]] = []


def add_check(name: str, passed: bool, detail: str = "") -> None:
    CHECKS.append((name, passed, detail))


def syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:
        return False, repr(exc)


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    dashboard_path = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
    module_path = PROJECT_ROOT / "app" / "paid_simulator" / "phase3g_public_customer_activation_plan.py"
    doc_path = PROJECT_ROOT / "docs" / "phase3g_2_public_customer_activation_plan.md"

    print("=" * 100)
    print("Phase 3G-2 public Customer-view activation-plan check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    expected_files = [
        ("phase3g_public_customer_activation_plan.py", module_path),
        ("run_paid_simulator_phase3g_2_activation_plan_check.py", Path(__file__).resolve()),
        ("phase3g_2_public_customer_activation_plan.md", doc_path),
    ]
    for label, path in expected_files:
        add_check(label, path.exists(), str(path))

    if dashboard_path.exists():
        ok, detail = syntax_valid(dashboard_path)
        add_check("Dashboard syntax remains valid", ok, detail)
        dashboard_text = dashboard_path.read_text(encoding="utf-8", errors="ignore")
        add_check("Phase 3D markers remain present", "Phase 3D" in dashboard_text, "Phase 3D marker search")
        add_check("Phase 3E marker remains present", "PHASE3E_7C_DEVELOPER_TAB_READY" in dashboard_text, "Phase 3E marker search")
        add_check("Phase 3F marker remains present", "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY" in dashboard_text, "Phase 3F marker search")
        add_check("Public Customer view not already enabled", "PHASE3G_PUBLIC_CUSTOMER_ENABLED = True" not in dashboard_text, "public disabled")
    else:
        add_check("Dashboard file exists", False, str(dashboard_path))

    if module_path.exists():
        ok, detail = syntax_valid(module_path)
        add_check("Activation-plan module syntax valid", ok, detail)
        try:
            module = load_module(module_path, "phase3g_public_customer_activation_plan_check_import")
            model = module.build_phase3g_public_customer_activation_plan(PROJECT_ROOT)
            fallback = module.render_phase3g_public_customer_activation_plan(streamlit_module=None, project_root=PROJECT_ROOT)
            add_check("Activation-plan marker present", model.get("marker") == "PHASE3G_2_PUBLIC_CUSTOMER_ACTIVATION_PLAN_READY", str(model.get("marker")))
            add_check("Public Customer view remains disabled", model.get("public_customer_enabled") is False, str(model.get("public_customer_enabled")))
            add_check("Protected preview remains required", model.get("protected_preview_required") is True, str(model.get("protected_preview_required")))
            add_check("Activation requirements present", len(model.get("activation_requirements", [])) >= 5, str(len(model.get("activation_requirements", []))))
            add_check("Release guardrails present", len(model.get("release_guardrails", [])) >= 5, str(len(model.get("release_guardrails", []))))
            add_check("Customer labels present", len(model.get("customer_facing_labels", [])) >= 6, str(len(model.get("customer_facing_labels", []))))
            add_check("Fallback render returns model dictionary", isinstance(fallback, dict) and fallback.get("marker") == model.get("marker"), type(fallback).__name__)
        except Exception as exc:
            add_check("Activation-plan module imports and renders", False, repr(exc))

    prior_reports = [
        REPORT_DIR / "phase3e_9_completion_checkpoint_report.txt",
        REPORT_DIR / "phase3f_8_completion_gate_checkpoint_report.txt",
        REPORT_DIR / "phase3g_1_public_release_gate_checkpoint_report.txt",
    ]
    for report in prior_reports:
        add_check(f"Prior report exists: {report.name}", report.exists(), str(report))

    report_lines = []
    csv_lines = ["check,passed,detail"]
    for name, passed, detail in CHECKS:
        status = "PASS" if passed else "FAIL"
        print(f"{status:<10} {name:<70} {detail}")
        report_lines.append(f"{status:<10} {name:<70} {detail}")
        escaped_detail = detail.replace('"', '""')
        csv_lines.append(f'"{name}",{str(passed).upper()},"{escaped_detail}"')

    overall = all(passed for _, passed, _ in CHECKS)
    print()
    print("=" * 100)
    print(f"Overall Phase 3G-2 checkpoint status: {'PASS' if overall else 'FAIL'}")
    print("=" * 100)

    report_path = REPORT_DIR / "phase3g_2_activation_plan_checkpoint_report.txt"
    json_path = REPORT_DIR / "phase3g_2_activation_plan_checkpoint.json"
    csv_path = TABLE_DIR / "phase3g_2_activation_plan_checklist.csv"
    report_path.write_text("\n".join(report_lines) + f"\n\nOverall Phase 3G-2 checkpoint status: {'PASS' if overall else 'FAIL'}\n", encoding="utf-8")
    json_path.write_text(json.dumps({"overall_pass": overall, "checks": [{"name": n, "passed": p, "detail": d} for n, p, d in CHECKS]}, indent=2), encoding="utf-8")
    csv_path.write_text("\n".join(csv_lines) + "\n", encoding="utf-8")
    print(f"Saved checkpoint report: {report_path}")
    print(f"Saved checkpoint JSON:   {json_path}")
    print(f"Saved checklist CSV:     {csv_path}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
