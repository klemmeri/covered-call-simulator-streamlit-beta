"""
Phase 2 readiness check for the Covered Call Strategy Stress Test project.

Run this file from PyCharm. It confirms that the v0.1 local prototype release
artifacts and Phase 2 planning documents are present before deeper modeling or
website-integration work begins.
"""

from __future__ import annotations

import json
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]

REQUIRED_FILES = [
    ("Dashboard launcher", PROJECT_ROOT / "app" / "run_paid_simulator_form.py"),
    ("Dashboard app", PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"),
    ("Product metadata", PROJECT_ROOT / "app" / "paid_simulator" / "product_info.py"),
    ("Dashboard status helper", PROJECT_ROOT / "app" / "paid_simulator" / "dashboard_status.py"),
    ("Release checker", PROJECT_ROOT / "app" / "run_paid_simulator_release_check.py"),
    ("Customer-view checker", PROJECT_ROOT / "app" / "run_paid_simulator_customer_view_check.py"),
    ("Beta-demo checker", PROJECT_ROOT / "app" / "run_paid_simulator_beta_demo_check.py"),
    ("Config file", PROJECT_ROOT / "config" / "paid_simulator_config.json"),
    ("Scenario comparison CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_comparison.csv"),
    ("HTML report", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "scenario_comparison_report.html"),
    ("Phase 2 decision plan", PROJECT_ROOT / "docs" / "paid_simulator_phase2_decision_plan.md"),
    ("Phase 2 modeling scaffold doc", PROJECT_ROOT / "docs" / "paid_simulator_phase2_modeling_scaffold.md"),
]

CLEAN_DEMO_EXPECTED = {
    "ticker": "SPY",
    "account_size": 600000.0,
    "risk_tier": "Balanced",
    "position_size_cap": 0.10,
    "desired_contracts": 1,
    "target_delta": 0.30,
    "target_dte": 30,
    "management_rule": "close_at_50_percent_profit",
    "rolling_rule": "none",
    "re_entry_rule": "immediate",
    "transaction_cost": 1.00,
    "slippage_assumption": 0.01,
    "demo_price": 545.25,
}


def format_status(found: bool) -> str:
    return "FOUND" if found else "MISSING"


def values_match(actual, expected) -> bool:
    if isinstance(expected, float):
        try:
            return abs(float(actual) - expected) < 1e-9
        except Exception:
            return False
    return actual == expected


def main() -> None:
    print("=" * 88)
    print("Paid simulator Phase 2 readiness check")
    print("=" * 88)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    missing = []
    for label, path in REQUIRED_FILES:
        found = path.exists()
        print(f"{format_status(found):<10} {label:<35} {path}")
        if not found:
            missing.append(label)

    print()
    print("-" * 88)
    print("Clean demo config check")
    print("-" * 88)

    config_path = PROJECT_ROOT / "config" / "paid_simulator_config.json"
    config_ok = False
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            mismatches = []
            for key, expected in CLEAN_DEMO_EXPECTED.items():
                actual = config.get(key)
                if not values_match(actual, expected):
                    mismatches.append((key, actual, expected))
            if mismatches:
                print("REVIEW - active config does not fully match the clean demo setup.")
                for key, actual, expected in mismatches:
                    print(f"  {key}: actual={actual!r}, expected={expected!r}")
            else:
                print("PASS - active config matches the clean demo setup.")
                config_ok = True
        except Exception as exc:
            print(f"REVIEW - could not parse config JSON: {exc}")
    else:
        print("REVIEW - config file is missing.")

    print()
    print("=" * 88)
    if not missing and config_ok:
        print("Overall Phase 2 readiness status: PASS")
        print("The v0.1 local prototype is preserved and Phase 2 planning docs are present.")
    else:
        print("Overall Phase 2 readiness status: REVIEW")
        if missing:
            print("Missing files:")
            for item in missing:
                print(f"  - {item}")
        if not config_ok:
            print("Clean demo config is not confirmed. Use Demo controls -> Reset and run clean demo if needed.")
    print("=" * 88)


if __name__ == "__main__":
    main()
