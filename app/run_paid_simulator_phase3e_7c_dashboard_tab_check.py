"""
run_paid_simulator_phase3e_7c_dashboard_tab_check.py

Validation check for Phase 3E-7C guarded dashboard-tab integration.

Run this after app/install_phase3e_7c_dashboard_tab.py.
"""

from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
DASHBOARD_FILE = APP_DIR / "paid_simulator" / "config_form_app.py"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
REPORT_FILE = REPORT_DIR / "phase3e_7c_dashboard_tab_checkpoint_report.txt"
JSON_FILE = REPORT_DIR / "phase3e_7c_dashboard_tab_checkpoint.json"

EXPECTED_FILES = [
    APP_DIR / "install_phase3e_7c_dashboard_tab.py",
    APP_DIR / "run_paid_simulator_phase3e_7c_dashboard_tab_check.py",
    APP_DIR / "paid_simulator" / "phase3e_customer_workbench_streamlit_panel.py",
    PROJECT_ROOT / "docs" / "phase3e_7c_dashboard_tab_integration.md",
]

CHECKS: list[dict[str, str]] = []


def add_check(status: str, name: str, detail: str = "") -> None:
    CHECKS.append({"status": status, "name": name, "detail": detail})


def contains_any(text: str, markers: list[str]) -> bool:
    lowered = text.lower()
    return any(marker.lower() in lowered for marker in markers)


def print_section(title: str) -> None:
    print("\n" + title)
    print("-" * 100)


def main() -> int:
    print("=" * 100)
    print("Phase 3E-7C guarded dashboard-tab integration check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")

    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    print_section("Expected files")
    for file_path in EXPECTED_FILES:
        if file_path.exists():
            add_check("PASS", file_path.name, str(file_path))
        else:
            add_check("FAIL", file_path.name, str(file_path))
        print(f"{CHECKS[-1]['status']:<10} {CHECKS[-1]['name']:<65} {CHECKS[-1]['detail']}")

    print_section("Import checks")
    try:
        from app.paid_simulator.phase3e_customer_workbench_streamlit_panel import (
            build_panel_render_model,
            render_phase3e_customer_workbench_panel,
        )
        model = build_panel_render_model()
        rendered_model = render_phase3e_customer_workbench_panel(streamlit_module=None)
        if model and rendered_model:
            add_check("PASS", "Panel model and render functions import", "imported")
        else:
            add_check("FAIL", "Panel model and render functions import", "empty model")
    except Exception as exc:
        add_check("FAIL", "Panel model and render functions import", repr(exc))
    print(f"{CHECKS[-1]['status']:<10} {CHECKS[-1]['name']:<65} {CHECKS[-1]['detail']}")

    try:
        spec = importlib.util.spec_from_file_location("config_form_app_phase3e_check", DASHBOARD_FILE)
        if spec is None or spec.loader is None:
            raise RuntimeError("could not create import spec")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        add_check("PASS", "Dashboard file imports after guarded patch", "config_form_app.py")
    except Exception as exc:
        add_check("FAIL", "Dashboard file imports after guarded patch", repr(exc))
    print(f"{CHECKS[-1]['status']:<10} {CHECKS[-1]['name']:<65} {CHECKS[-1]['detail']}")

    print_section("Dashboard integration markers")
    if DASHBOARD_FILE.exists():
        text = DASHBOARD_FILE.read_text(encoding="utf-8")
        marker_checks = [
            ("Customer-view markers still present", contains_any(text, ["Customer", "customer"]), "Customer marker search"),
            ("Phase 3D markers still present", contains_any(text, ["Phase 3D", "integrated overlay", "phase3d"]), "Phase 3D marker search"),
            ("Phase 3E renderer reference present", "render_phase3e_customer_workbench_panel" in text, "panel renderer"),
            ("Phase 3E Developer-view readiness marker present", "PHASE3E_7C_DEVELOPER_TAB_READY" in text, "readiness marker"),
            ("Phase 3E helper function present", "_render_phase3e_customer_payoff_workbench_tab" in text, "helper function"),
            ("Customer view not marked as Phase 3E enabled", "PHASE3E_CUSTOMER_VIEW_ENABLED" not in text, "customer protected"),
        ]
        for name, passed, detail in marker_checks:
            add_check("PASS" if passed else "FAIL", name, detail)
            print(f"{CHECKS[-1]['status']:<10} {CHECKS[-1]['name']:<65} {CHECKS[-1]['detail']}")
    else:
        add_check("FAIL", "Dashboard file found", str(DASHBOARD_FILE))
        print(f"{CHECKS[-1]['status']:<10} {CHECKS[-1]['name']:<65} {CHECKS[-1]['detail']}")

    print_section("Backup check")
    backup_dir = PROJECT_ROOT / "outputs" / "backups" / "paid_simulator"
    backups = sorted(backup_dir.glob("config_form_app_before_phase3e_7c_*.py")) if backup_dir.exists() else []
    if backups:
        add_check("PASS", "Timestamped dashboard backup exists", str(backups[-1]))
    else:
        add_check("FAIL", "Timestamped dashboard backup exists", str(backup_dir))
    print(f"{CHECKS[-1]['status']:<10} {CHECKS[-1]['name']:<65} {CHECKS[-1]['detail']}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    pass_count = sum(1 for item in CHECKS if item["status"] == "PASS")
    fail_count = sum(1 for item in CHECKS if item["status"] == "FAIL")
    overall = "PASS" if fail_count == 0 else "FAIL"

    report_lines = [
        "Phase 3E-7C guarded dashboard-tab integration checkpoint report",
        f"Project root: {PROJECT_ROOT}",
        f"Overall status: {overall}",
        f"PASS count: {pass_count}",
        f"FAIL count: {fail_count}",
        "",
    ]
    for item in CHECKS:
        report_lines.append(f"{item['status']:<10} {item['name']:<65} {item['detail']}")
    REPORT_FILE.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    JSON_FILE.write_text(json.dumps({"overall_status": overall, "checks": CHECKS}, indent=2), encoding="utf-8")

    print("\n" + "=" * 100)
    print(f"Overall Phase 3E-7C checkpoint status: {overall}")
    print("=" * 100)
    print(f"Saved checkpoint report: {REPORT_FILE}")
    print(f"Saved checkpoint JSON:   {JSON_FILE}")

    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
