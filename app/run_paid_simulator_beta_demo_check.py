"""
Beta-demo readiness checker for the Covered Call Strategy Stress Test.

Run this file from PyCharm before showing the local Streamlit dashboard to a
customer, beta tester, collaborator, or potential user.
"""

from __future__ import annotations

import json
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

CHECKS = [
    ("Dashboard launcher", PROJECT_ROOT / "app" / "run_paid_simulator_form.py"),
    ("Dashboard app", PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"),
    ("Product metadata", PROJECT_ROOT / "app" / "paid_simulator" / "product_info.py"),
    ("Dashboard status helper", PROJECT_ROOT / "app" / "paid_simulator" / "dashboard_status.py"),
    ("Customer view checker", PROJECT_ROOT / "app" / "run_paid_simulator_customer_view_check.py"),
    ("Release checker", PROJECT_ROOT / "app" / "run_paid_simulator_release_check.py"),
    ("Config file", PROJECT_ROOT / "config" / "paid_simulator_config.json"),
    ("Scenario comparison CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_comparison.csv"),
    ("HTML report", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "scenario_comparison_report.html"),
    ("Decision memo folder", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "decision_memos"),
    ("Customer demo walkthrough", PROJECT_ROOT / "docs" / "paid_simulator_customer_demo_walkthrough.md"),
    ("Customer view acceptance test", PROJECT_ROOT / "docs" / "paid_simulator_customer_view_acceptance_test.md"),
    ("Beta demo readiness checklist", PROJECT_ROOT / "docs" / "paid_simulator_beta_demo_readiness.md"),
    ("Beta feedback form", PROJECT_ROOT / "docs" / "paid_simulator_beta_feedback_form.md"),
    ("Beta test log", PROJECT_ROOT / "docs" / "paid_simulator_beta_test_log.md"),
]

EXPECTED_CLEAN_DEMO = {
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


def line(char: str = "=", width: int = 88) -> None:
    print(char * width)


def check_config() -> list[str]:
    problems: list[str] = []
    config_path = PROJECT_ROOT / "config" / "paid_simulator_config.json"
    if not config_path.exists():
        return ["Config file is missing."]
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return [f"Config file is not valid JSON: {exc}"]

    for key, expected in EXPECTED_CLEAN_DEMO.items():
        actual = config.get(key)
        if isinstance(expected, float):
            try:
                if abs(float(actual) - expected) > 1e-9:
                    problems.append(f"Config differs from clean demo: {key}={actual!r}, expected {expected!r}")
            except Exception:
                problems.append(f"Config differs from clean demo: {key}={actual!r}, expected {expected!r}")
        elif actual != expected:
            problems.append(f"Config differs from clean demo: {key}={actual!r}, expected {expected!r}")
    return problems


def main() -> None:
    line()
    print("Covered Call Strategy Stress Test - beta-demo readiness check")
    line()
    print(f"Project root: {PROJECT_ROOT}")
    print()

    missing = []
    for label, path in CHECKS:
        status = "FOUND" if path.exists() else "MISSING"
        print(f"{status:<10} {label:<38} {path}")
        if not path.exists():
            missing.append(label)

    print()
    line("-")
    print("Clean demo config check")
    line("-")
    config_problems = check_config()
    if config_problems:
        print("REVIEW")
        for problem in config_problems:
            print(f"- {problem}")
        print("Recommendation: open the dashboard and use Demo controls -> Reset and run clean demo before presenting.")
    else:
        print("PASS - active config matches the clean demo setup.")

    print()
    line()
    if missing or config_problems:
        print("Overall beta-demo status: REVIEW")
        print("The dashboard can likely run, but clean demo readiness needs attention before a customer-facing presentation.")
    else:
        print("Overall beta-demo status: PASS")
        print("Customer-facing demo files are present and the active config matches the clean demo setup.")
    line()


if __name__ == "__main__":
    main()
