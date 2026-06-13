"""
Customer-view readiness checker for the Covered Call Strategy Stress Test dashboard.

Run this file from PyCharm after installing dashboard updates. It performs a lightweight
file/documentation check for the customer-facing dashboard materials.
"""

from __future__ import annotations

from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

CHECKS = [
    ("Dashboard launcher", PROJECT_ROOT / "app" / "run_paid_simulator_form.py"),
    ("Dashboard app", PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"),
    ("Product metadata", PROJECT_ROOT / "app" / "paid_simulator" / "product_info.py"),
    ("Dashboard status helper", PROJECT_ROOT / "app" / "paid_simulator" / "dashboard_status.py"),
    ("Release check script", PROJECT_ROOT / "app" / "run_paid_simulator_release_check.py"),
    ("Config file", PROJECT_ROOT / "config" / "paid_simulator_config.json"),
    ("Scenario comparison CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_comparison.csv"),
    ("HTML report", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "scenario_comparison_report.html"),
    ("Customer demo walkthrough", PROJECT_ROOT / "docs" / "paid_simulator_customer_demo_walkthrough.md"),
    ("Customer view acceptance test", PROJECT_ROOT / "docs" / "paid_simulator_customer_view_acceptance_test.md"),
    ("Release readiness checklist", PROJECT_ROOT / "docs" / "paid_simulator_release_readiness_checklist.md"),
]


def main() -> None:
    print("=" * 88)
    print("Paid simulator customer-view readiness check")
    print("=" * 88)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    missing = []
    for label, path in CHECKS:
        status = "FOUND" if path.exists() else "MISSING"
        print(f"{status:<10} {label:<36} {path}")
        if not path.exists():
            missing.append((label, path))

    print()
    print("=" * 88)
    if missing:
        print("Overall customer-view status: REVIEW")
        print("Missing items:")
        for label, path in missing:
            print(f"- {label}: {path}")
    else:
        print("Overall customer-view status: PASS")
        print("Customer-facing dashboard files and support documents are present.")
    print("=" * 88)


if __name__ == "__main__":
    main()
