"""
run_paid_simulator_phase3e_customer_scenario_overlay_check.py

Standalone Phase 3E-4 checkpoint check for the Covered Call Simulator.

Run from PyCharm after extracting the Phase 3E-4 package into the project root:

    app\run_paid_simulator_phase3e_customer_scenario_overlay_check.py
"""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.paid_simulator.phase3e_customer_scenario_overlay import (  # noqa: E402
    CustomerScenarioInput,
    ScenarioValidationError,
    build_customer_scenario_overlay,
    build_default_scenario_prices,
    run_phase3e_customer_scenario_checkpoint,
    update_customer_scenario_overlay,
)


def _pass(label: str, detail: str = "") -> None:
    print(f"PASS       {label:<58} {detail}")


def _fail(label: str, detail: str = "") -> None:
    print(f"FAIL       {label:<58} {detail}")


def main() -> int:
    print("=" * 96)
    print("Phase 3E-4 customer scenario-overlay workflow check")
    print("=" * 96)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    failures: list[str] = []

    try:
        setup = CustomerScenarioInput()
        summary = build_customer_scenario_overlay(setup)
        _pass("Build default customer scenario overlay", f"{summary.number_of_scenarios} scenarios")
    except Exception as exc:  # pragma: no cover - checkpoint script
        _fail("Build default customer scenario overlay", str(exc))
        failures.append("default overlay build failed")
        summary = None

    if summary is not None:
        labels = [row.customer_zone for row in summary.rows]
        required_zones = {"Below breakeven", "Profitable stock zone", "Assignment zone"}
        if required_zones.issubset(set(labels)):
            _pass("Customer zones present", ", ".join(sorted(set(labels))))
        else:
            _fail("Customer zones present", f"found {sorted(set(labels))}")
            failures.append("missing customer zones")

        if summary.breakeven == round(setup.stock_cost_basis - setup.premium, 2):
            _pass("Breakeven calculation", f"${summary.breakeven:,.2f}")
        else:
            _fail("Breakeven calculation", f"${summary.breakeven:,.2f}")
            failures.append("bad breakeven")

        if summary.max_profit_if_assigned > 0:
            _pass("Max profit if assigned is available", f"${summary.max_profit_if_assigned:,.2f}")
        else:
            _fail("Max profit if assigned is available", f"${summary.max_profit_if_assigned:,.2f}")
            failures.append("bad max profit")

    try:
        default_prices = build_default_scenario_prices(550.0, 560.0)
        if len(default_prices) >= 5 and default_prices == tuple(sorted(default_prices)):
            _pass("One-click scenario range builder", str(default_prices))
        else:
            _fail("One-click scenario range builder", str(default_prices))
            failures.append("scenario range builder failed")
    except Exception as exc:
        _fail("One-click scenario range builder", str(exc))
        failures.append("scenario range builder exception")

    try:
        updated = update_customer_scenario_overlay(
            CustomerScenarioInput(),
            current_price=550.0,
            strike=552.0,
            premium=1.25,
        )
        if updated.current_price == 550.0 and updated.strike == 552.0 and updated.premium == 1.25:
            _pass("One-click overlay update hook", "current price, strike, and premium updated")
        else:
            _fail("One-click overlay update hook", str(updated))
            failures.append("overlay update hook failed")
        if updated.warnings:
            _pass("Warning boxes triggered for tight setup", f"{len(updated.warnings)} warning(s)")
        else:
            _fail("Warning boxes triggered for tight setup", "none")
            failures.append("warning boxes not triggered")
    except Exception as exc:
        _fail("One-click overlay update hook", str(exc))
        failures.append("overlay update hook exception")

    try:
        build_customer_scenario_overlay(CustomerScenarioInput(current_price=-1.0))
        _fail("Invalid input validation", "negative current price accepted")
        failures.append("negative current price accepted")
    except ScenarioValidationError:
        _pass("Invalid input validation", "negative current price rejected")
    except Exception as exc:
        _fail("Invalid input validation", str(exc))
        failures.append("unexpected validation exception")

    try:
        outputs = run_phase3e_customer_scenario_checkpoint()
        for key in ("csv_path", "updated_csv_path", "setup_path", "report_path"):
            path = outputs[key]
            if isinstance(path, Path) and path.exists():
                _pass(f"Output exists: {key}", str(path))
            else:
                _fail(f"Output exists: {key}", str(path))
                failures.append(f"missing output {key}")
    except Exception as exc:
        _fail("Checkpoint output workflow", str(exc))
        failures.append("checkpoint output workflow failed")

    print()
    print("=" * 96)
    if failures:
        print("Overall Phase 3E-4 checkpoint status: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Overall Phase 3E-4 checkpoint status: PASS")
    print("=" * 96)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
