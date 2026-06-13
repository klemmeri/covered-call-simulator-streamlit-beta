"""
run_paid_simulator_phase3e_customer_workbench_check.py

Phase 3E-5 checkpoint runner for the customer payoff workbench.
Run this file from PyCharm after installing the Phase 3E-5 package.
"""

from __future__ import annotations

from pathlib import Path
import csv
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.paid_simulator.phase3e_customer_payoff_workbench import (  # noqa: E402
    CustomerPayoffWorkbenchInput,
    build_customer_payoff_workbench,
    build_default_scenario_prices,
    build_customer_summary_text,
    load_customer_workbench_setup,
    run_phase3e_customer_workbench_checkpoint,
    save_customer_workbench_setup,
    update_customer_payoff_workbench,
)


def print_result(status: str, item: str, detail: str = "") -> None:
    print(f"{status:<10} {item:<64} {detail}")


def require(condition: bool, item: str, detail: str = "") -> bool:
    if condition:
        print_result("PASS", item, detail)
        return True
    print_result("FAIL", item, detail)
    return False


def main() -> int:
    print("=" * 96)
    print("Phase 3E-5 customer payoff workbench checkpoint")
    print("=" * 96)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    checks: list[bool] = []

    setup = CustomerPayoffWorkbenchInput(
        ticker="SPY",
        current_price=545.25,
        stock_cost_basis=542.00,
        strike_price=555.00,
        premium=4.50,
        shares=100,
        expiration_date="2026-07-17",
        setup_name="Phase 3E-5 checkpoint setup",
    )

    result = build_customer_payoff_workbench(setup)
    checks.append(require(result.ticker == "SPY", "Ticker is cleaned for customer display", result.ticker))
    checks.append(require(result.breakeven_price == 537.50, "Breakeven calculation", str(result.breakeven_price)))
    checks.append(require(result.premium_income == 450.00, "Premium income calculation", str(result.premium_income)))
    checks.append(require(result.max_profit_if_assigned == 1750.00, "Maximum profit if assigned", str(result.max_profit_if_assigned)))
    checks.append(require(len(result.metric_cards) >= 7, "Customer metric cards created", str(len(result.metric_cards))))
    checks.append(require(any(card.label == "Breakeven price" for card in result.metric_cards), "Breakeven label present"))
    checks.append(require(any(card.label == "Assignment zone" or "assignment" in card.explanation.lower() for card in result.metric_cards), "Assignment-zone language present"))
    checks.append(require(len(result.scenario_rows) >= 5, "Scenario overlay rows created", str(len(result.scenario_rows))))
    checks.append(require(any(row.assignment_zone == "Yes" for row in result.scenario_rows), "Assignment scenario included"))
    checks.append(require(len(result.warnings) >= 1, "Risk-warning list created", str(len(result.warnings))))

    default_prices = build_default_scenario_prices(545.25, 555.00)
    checks.append(require(545.25 in default_prices, "Default scenario prices include current price", str(default_prices)))
    checks.append(require(555.00 in default_prices, "Default scenario prices include strike", str(default_prices)))

    updated = update_customer_payoff_workbench(
        setup,
        current_price=552.50,
        scenario_prices=(520.0, 542.0, 552.5, 555.0, 565.0, 585.0),
    )
    checks.append(require(updated.current_price == 552.50, "One-click scenario update hook changes current price", str(updated.current_price)))
    checks.append(require(len(updated.scenario_rows) == 6, "One-click scenario update uses supplied scenario range", str(len(updated.scenario_rows))))

    setup_path = save_customer_workbench_setup(setup)
    checks.append(require(setup_path.exists(), "Saved customer setup JSON", str(setup_path)))
    loaded = load_customer_workbench_setup(setup_path)
    checks.append(require(loaded.ticker == "SPY", "Reloaded setup ticker", loaded.ticker))
    checks.append(require(loaded.strike_price == 555.00, "Reloaded setup strike", str(loaded.strike_price)))

    outputs = run_phase3e_customer_workbench_checkpoint()
    csv_path = Path(outputs["csv_path"])
    report_path = Path(outputs["report_path"])
    checks.append(require(csv_path.exists(), "Scenario CSV exported", str(csv_path)))
    checks.append(require(report_path.exists(), "Customer summary report written", str(report_path)))

    with csv_path.open("r", newline="", encoding="utf-8") as file_obj:
        rows = list(csv.DictReader(file_obj))
    checks.append(require(len(rows) == 6, "Scenario CSV contains updated scenario rows", str(len(rows))))
    checks.append(require("covered_call_profit" in rows[0], "Scenario CSV includes covered-call profit column"))

    summary_text = build_customer_summary_text(updated)
    checks.append(require("Customer payoff labels" in summary_text, "Summary text includes customer payoff label section"))
    checks.append(require("Risk warnings" in summary_text, "Summary text includes risk-warning section"))
    checks.append(require("Scenario overlay" in summary_text, "Summary text includes scenario-overlay section"))

    print()
    print("=" * 96)
    if all(checks):
        print("Overall Phase 3E-5 checkpoint status: PASS")
        print("=" * 96)
        print(f"Saved setup: {outputs['setup_path']}")
        print(f"Scenario CSV: {outputs['csv_path']}")
        print(f"Summary report: {outputs['report_path']}")
        return 0

    print("Overall Phase 3E-5 checkpoint status: FAIL")
    print("=" * 96)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
