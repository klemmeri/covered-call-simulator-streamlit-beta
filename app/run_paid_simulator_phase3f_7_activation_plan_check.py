"""
run_paid_simulator_phase3f_7_activation_plan_check.py

Checkpoint script for Phase 3F-7: Controlled Customer-Preview Activation Plan.
"""

from __future__ import annotations

import ast
import csv
import importlib
import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

APP_DIR = PROJECT_ROOT / "app"
PAID_DIR = APP_DIR / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)

CHECKS: list[tuple[str, bool, str]] = []


def add_check(name: str, passed: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(passed), detail))


def syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:  # pragma: no cover
        return False, repr(exc)


def file_contains(path: Path, text: str) -> bool:
    if not path.exists():
        return False
    return text in path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    print("=" * 100)
    print("Phase 3F-7 controlled customer-preview activation plan check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    expected_files = [
        APP_DIR / "run_paid_simulator_phase3f_7_activation_plan_check.py",
        PAID_DIR / "phase3f_customer_preview_activation_plan.py",
        PROJECT_ROOT / "docs" / "phase3f_7_customer_preview_activation_plan.md",
    ]

    for path in expected_files:
        add_check(path.name, path.exists(), str(path))

    dashboard_path = PAID_DIR / "config_form_app.py"
    add_check("Dashboard file exists", dashboard_path.exists(), str(dashboard_path))
    if dashboard_path.exists():
        ok, detail = syntax_valid(dashboard_path)
        add_check("Dashboard syntax valid", ok, detail)

    module_path = PAID_DIR / "phase3f_customer_preview_activation_plan.py"
    if module_path.exists():
        ok, detail = syntax_valid(module_path)
        add_check("Activation plan module syntax valid", ok, detail)

    try:
        module = importlib.import_module("app.paid_simulator.phase3f_customer_preview_activation_plan")
        model = module.build_phase3f_7_activation_plan(PROJECT_ROOT)
        data = model.to_dict()
        fallback = module.render_phase3f_7_activation_plan(streamlit_module=None, project_root=PROJECT_ROOT)

        add_check("Activation plan module imports", True, "imported")
        add_check("Activation plan has ready marker", data.get("marker") == "PHASE3F_7_CUSTOMER_PREVIEW_ACTIVATION_READY", str(data.get("marker")))
        add_check("Public Customer release remains disabled", data.get("public_customer_release_enabled") is False, str(data.get("public_customer_release_enabled")))
        add_check("Protected preview remains allowed", data.get("protected_preview_allowed") is True, str(data.get("protected_preview_allowed")))
        add_check("Activation plan has guardrails", len(data.get("activation_guardrails", [])) >= 4, str(len(data.get("activation_guardrails", []))))
        add_check("Activation plan has customer-preview requirements", len(data.get("customer_preview_requirements", [])) >= 4, str(len(data.get("customer_preview_requirements", []))))
        add_check("Fallback render returns dict", isinstance(fallback, dict), type(fallback).__name__)
        add_check("Fallback render preserves marker", fallback.get("marker") == "PHASE3F_7_CUSTOMER_PREVIEW_ACTIVATION_READY", str(fallback.get("marker")))
    except Exception as exc:
        add_check("Activation plan module imports/renders", False, repr(exc))
        data = {}

    prior_reports = [
        REPORT_DIR / "phase3e_9_completion_checkpoint_report.txt",
        REPORT_DIR / "phase3f_3_customer_preview_route_checkpoint_report.txt",
        REPORT_DIR / "phase3f_4_preview_visual_checkpoint_report.txt",
        REPORT_DIR / "phase3f_6_release_readiness_checkpoint_report.txt",
    ]
    for path in prior_reports:
        add_check(f"Prior report exists: {path.name}", path.exists(), str(path))

    if dashboard_path.exists():
        add_check("Phase 3E marker still present", file_contains(dashboard_path, "PHASE3E_7C_DEVELOPER_TAB_READY"), "Phase 3E marker search")
        add_check("Phase 3F-3 route marker still present", file_contains(dashboard_path, "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY"), "Phase 3F-3 marker search")
        add_check("Ordinary Customer view not public-release enabled", not file_contains(dashboard_path, "PHASE3F_PUBLIC_CUSTOMER_RELEASE_ENABLED = True"), "customer protected")

    report_path = REPORT_DIR / "phase3f_7_activation_plan_checkpoint_report.txt"
    json_path = REPORT_DIR / "phase3f_7_activation_plan_checkpoint.json"
    csv_path = TABLE_DIR / "phase3f_7_activation_plan_checklist.csv"

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["check", "status", "detail"])
        for name, passed, detail in CHECKS:
            writer.writerow([name, "PASS" if passed else "FAIL", detail])

    payload = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "project_root": str(PROJECT_ROOT),
        "checks": [
            {"name": name, "passed": passed, "detail": detail}
            for name, passed, detail in CHECKS
        ],
        "activation_plan": data,
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = []
    for name, passed, detail in CHECKS:
        status = "PASS" if passed else "FAIL"
        print(f"{status:<10} {name:<70} {detail}")
        lines.append(f"{status:<10} {name:<70} {detail}")

    all_passed = all(passed for _, passed, _ in CHECKS)
    print()
    print("=" * 100)
    final = "PASS" if all_passed else "FAIL"
    print(f"Overall Phase 3F-7 checkpoint status: {final}")
    print("=" * 100)
    print(f"Saved checkpoint report: {report_path}")
    print(f"Saved checkpoint JSON:   {json_path}")
    print(f"Saved checklist CSV:     {csv_path}")

    report_path.write_text(
        "Phase 3F-7 controlled customer-preview activation plan check\n"
        + "=" * 100
        + "\n"
        + "\n".join(lines)
        + "\n\n"
        + f"Overall Phase 3F-7 checkpoint status: {final}\n",
        encoding="utf-8",
    )
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
