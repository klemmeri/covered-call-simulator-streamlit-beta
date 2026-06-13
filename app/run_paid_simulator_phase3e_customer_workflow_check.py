"""
run_paid_simulator_phase3e_customer_workflow_check.py

Phase 3E-1 checkpoint script for the Covered Call Simulator paid dashboard.

This script verifies the customer-ready payoff workflow scaffold without
changing the existing dashboard.
"""

from __future__ import annotations

from pathlib import Path
import sys
import traceback


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
REPORT_PATH = REPORT_DIR / "phase3e_customer_workflow_checkpoint_report.txt"
SNAPSHOT_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
SNAPSHOT_PATH = SNAPSHOT_DIR / "phase3e_customer_payoff_setup_check.json"


def status_line(passed: bool, label: str, detail: str = "") -> str:
    status = "PASS" if passed else "FAIL"
    if detail:
        return f"{status:<10} {label:<65} {detail}"
    return f"{status:<10} {label}"


def main() -> int:
    lines: list[str] = []
    failures: list[str] = []

    lines.append("=" * 96)
    lines.append("Phase 3E-1 customer payoff workflow checkpoint")
    lines.append("=" * 96)
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append("")

    try:
        from paid_simulator.phase3e_customer_payoff_workflow import (
            CUSTOMER_LABELS,
            CUSTOMER_WORKFLOW_SECTIONS,
            CoveredCallSetup,
            build_customer_summary,
            build_customer_warnings,
            calculate_customer_payoff_metrics,
            export_customer_setup,
            reload_customer_setup,
            run_self_check,
        )

        lines.append(status_line(True, "Import customer workflow module"))
    except Exception as exc:  # pragma: no cover - diagnostic script
        lines.append(status_line(False, "Import customer workflow module", str(exc)))
        lines.append(traceback.format_exc())
        failures.append("Could not import Phase 3E customer workflow module.")
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
        print("\n".join(lines))
        print(f"\nSaved checkpoint report: {REPORT_PATH}")
        return 1

    checks = run_self_check()

    expected_boolean_checks = {
        "valid_setup": True,
        "required_sections_present": True,
        "customer_labels_present": True,
        "metrics_created": True,
        "warnings_created": True,
        "export_hook_available": True,
        "reload_hook_available": True,
        "developer_features_visible": False,
    }

    lines.append("Self-check results")
    lines.append("-" * 96)
    for key, expected in expected_boolean_checks.items():
        observed = checks.get(key)
        passed = observed == expected
        lines.append(status_line(passed, key, f"observed={observed!r}; expected={expected!r}"))
        if not passed:
            failures.append(f"Self-check failed: {key}")
    lines.append("")

    lines.append("Customer workflow structure")
    lines.append("-" * 96)
    required_sections = {
        "Setup inputs",
        "Payoff summary",
        "Scenario overlay",
        "Risk warnings",
        "Save or export setup",
        "Reload saved setup",
    }
    observed_sections = set(CUSTOMER_WORKFLOW_SECTIONS)
    for section in sorted(required_sections):
        passed = section in observed_sections
        lines.append(status_line(passed, f"Section present: {section}"))
        if not passed:
            failures.append(f"Missing customer workflow section: {section}")

    required_labels = {
        "current_price",
        "strike_price",
        "premium",
        "breakeven_price",
        "max_profit_total",
        "downside_cushion",
        "assignment_zone",
        "scenario_overlay",
    }
    observed_labels = set(CUSTOMER_LABELS)
    for label in sorted(required_labels):
        passed = label in observed_labels
        detail = CUSTOMER_LABELS.get(label, "")
        lines.append(status_line(passed, f"Customer label present: {label}", detail))
        if not passed:
            failures.append(f"Missing customer label: {label}")
    lines.append("")

    lines.append("Metric and warning behavior")
    lines.append("-" * 96)
    base_setup = CoveredCallSetup(
        ticker="SPY",
        current_price=545.25,
        strike_price=560.00,
        premium=4.50,
        contracts=2,
    )
    metrics = calculate_customer_payoff_metrics(base_setup)
    summary = build_customer_summary(base_setup)
    warnings = build_customer_warnings(base_setup)

    expected_breakeven = 540.75
    expected_shares = 200
    expected_premium_income = 900.00
    expected_max_profit = (560.00 - 545.25 + 4.50) * 200

    metric_checks = [
        (metrics.breakeven_price == expected_breakeven, "Breakeven calculation", f"{metrics.breakeven_price}"),
        (metrics.shares_controlled == expected_shares, "Shares controlled calculation", f"{metrics.shares_controlled}"),
        (metrics.gross_premium_income == expected_premium_income, "Gross premium income calculation", f"{metrics.gross_premium_income}"),
        (metrics.max_profit_total == round(expected_max_profit, 2), "Maximum profit calculation", f"{metrics.max_profit_total}"),
        (summary["developer_features_visible"] is False, "Developer features hidden in customer workflow", "False"),
        (len(warnings) >= 1, "Warning list created", f"count={len(warnings)}"),
    ]

    for passed, label, detail in metric_checks:
        lines.append(status_line(passed, label, detail))
        if not passed:
            failures.append(label)
    lines.append("")

    lines.append("Export and reload hook behavior")
    lines.append("-" * 96)
    try:
        exported_path = export_customer_setup(base_setup, SNAPSHOT_PATH)
        reloaded_setup = reload_customer_setup(exported_path)
        export_passed = exported_path.exists()
        reload_passed = reloaded_setup == base_setup
        lines.append(status_line(export_passed, "Export customer setup JSON", str(exported_path)))
        lines.append(status_line(reload_passed, "Reload customer setup JSON", repr(reloaded_setup)))
        if not export_passed:
            failures.append("Customer setup export did not create JSON file.")
        if not reload_passed:
            failures.append("Customer setup reload did not reproduce original setup.")
    except Exception as exc:  # pragma: no cover - diagnostic script
        lines.append(status_line(False, "Export/reload customer setup JSON", str(exc)))
        lines.append(traceback.format_exc())
        failures.append("Export/reload hook failed.")
    lines.append("")

    lines.append("=" * 96)
    if failures:
        lines.append("Overall Phase 3E-1 checkpoint status: FAIL")
        lines.append("Failures:")
        for item in failures:
            lines.append(f"- {item}")
        exit_code = 1
    else:
        lines.append("Overall Phase 3E-1 checkpoint status: PASS")
        exit_code = 0
    lines.append("=" * 96)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print("\n".join(lines))
    print(f"\nSaved checkpoint report: {REPORT_PATH}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
