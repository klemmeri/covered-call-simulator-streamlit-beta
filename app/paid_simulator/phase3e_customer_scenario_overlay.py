"""
phase3e_customer_scenario_overlay.py

Phase 3E-4 customer scenario-overlay workflow for the Covered Call Simulator.

This module provides a customer-safe way to update a covered-call payoff setup
under simple scenario assumptions. It intentionally avoids developer/test
terminology and does not depend on Streamlit, so it can be checked from PyCharm
before being wired into the paid dashboard.

Customer-facing purpose
-----------------------
A customer can adjust the current stock price, strike, premium, and optional
scenario prices, then receive a refreshed payoff summary with plain-language
labels and setup warnings.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable
import csv
import json


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
SAVED_SETUP_DIR = PROJECT_ROOT / "outputs" / "saved_setups" / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"


@dataclass(frozen=True)
class CustomerScenarioInput:
    """Customer-facing covered-call scenario inputs."""

    ticker: str = "SPY"
    current_price: float = 545.25
    shares: int = 100
    strike: float = 555.00
    premium: float = 4.50
    stock_cost_basis: float = 545.25
    scenario_prices: tuple[float, ...] = (500.0, 525.0, 545.25, 555.0, 575.0, 600.0)
    note: str = "Customer scenario overlay checkpoint setup"


@dataclass(frozen=True)
class CustomerScenarioRow:
    """One customer-readable row in the scenario overlay."""

    ticker: str
    scenario_price: float
    stock_only_profit: float
    covered_call_profit: float
    option_effect: float
    assignment_likely: str
    customer_zone: str
    explanation: str


@dataclass(frozen=True)
class CustomerScenarioSummary:
    """Customer-facing scenario-overlay summary."""

    ticker: str
    current_price: float
    strike: float
    premium: float
    breakeven: float
    max_profit_if_assigned: float
    downside_cushion_dollars: float
    downside_cushion_percent: float
    assignment_zone_starts_at: float
    number_of_scenarios: int
    warnings: tuple[str, ...]
    rows: tuple[CustomerScenarioRow, ...]


class ScenarioValidationError(ValueError):
    """Raised when a customer scenario setup is not valid."""


def _require_positive(name: str, value: float) -> None:
    if value <= 0:
        raise ScenarioValidationError(f"{name} must be greater than zero.")


def validate_customer_scenario_input(setup: CustomerScenarioInput) -> None:
    """Validate customer scenario inputs before calculation."""

    if not setup.ticker.strip():
        raise ScenarioValidationError("Ticker is required.")
    _require_positive("Current price", setup.current_price)
    _require_positive("Strike", setup.strike)
    _require_positive("Stock cost basis", setup.stock_cost_basis)
    if setup.shares <= 0:
        raise ScenarioValidationError("Shares must be greater than zero.")
    if setup.premium < 0:
        raise ScenarioValidationError("Premium cannot be negative.")
    if not setup.scenario_prices:
        raise ScenarioValidationError("At least one scenario price is required.")
    for price in setup.scenario_prices:
        _require_positive("Scenario price", price)


def build_default_scenario_prices(current_price: float, strike: float) -> tuple[float, ...]:
    """Create a simple customer-safe scenario range around current price and strike."""

    low = min(current_price, strike) * 0.90
    mid_low = current_price * 0.97
    mid = current_price
    near_strike = strike
    mid_high = max(current_price, strike) * 1.03
    high = max(current_price, strike) * 1.10
    values = sorted({round(x, 2) for x in (low, mid_low, mid, near_strike, mid_high, high)})
    return tuple(values)


def build_customer_warnings(setup: CustomerScenarioInput) -> tuple[str, ...]:
    """Return customer-facing warnings for risky or unusual setups."""

    warnings: list[str] = []
    breakeven = setup.stock_cost_basis - setup.premium
    cushion_percent = setup.premium / setup.stock_cost_basis if setup.stock_cost_basis else 0.0
    upside_room = setup.strike - setup.current_price
    upside_room_percent = upside_room / setup.current_price if setup.current_price else 0.0

    if setup.strike < setup.current_price:
        warnings.append(
            "The strike is below the current stock price. Assignment risk is already elevated."
        )
    elif upside_room_percent < 0.01:
        warnings.append(
            "The strike is close to the current price. The covered call has limited upside room."
        )

    if cushion_percent < 0.005:
        warnings.append(
            "The premium provides less than a 0.5% downside cushion relative to cost basis."
        )
    elif cushion_percent < 0.01:
        warnings.append(
            "The premium provides only a modest downside cushion relative to cost basis."
        )

    if breakeven > setup.current_price:
        warnings.append(
            "The breakeven is above the current price, so the setup starts below breakeven."
        )

    if setup.premium > setup.current_price * 0.08:
        warnings.append(
            "The premium is unusually large relative to the stock price. Confirm the option quote."
        )

    return tuple(warnings)


def _assignment_likely(price: float, strike: float) -> str:
    return "Yes" if price >= strike else "No"


def _customer_zone(price: float, setup: CustomerScenarioInput) -> str:
    breakeven = setup.stock_cost_basis - setup.premium
    if price < breakeven:
        return "Below breakeven"
    if price < setup.strike:
        return "Profitable stock zone"
    return "Assignment zone"


def _explanation(price: float, setup: CustomerScenarioInput) -> str:
    if price < setup.stock_cost_basis - setup.premium:
        return "The premium helps, but the stock decline is larger than the cushion."
    if price < setup.strike:
        return "The stock is above breakeven and below the strike, so assignment is not expected."
    return "The stock is at or above the strike; gains are capped by likely assignment."


def build_customer_scenario_overlay(setup: CustomerScenarioInput) -> CustomerScenarioSummary:
    """Calculate the customer-facing scenario overlay for a covered call."""

    validate_customer_scenario_input(setup)

    rows: list[CustomerScenarioRow] = []
    premium_total = setup.premium * setup.shares
    breakeven = setup.stock_cost_basis - setup.premium
    max_profit_if_assigned = ((setup.strike - setup.stock_cost_basis) + setup.premium) * setup.shares
    downside_cushion_dollars = setup.premium
    downside_cushion_percent = setup.premium / setup.stock_cost_basis * 100.0

    for price in setup.scenario_prices:
        stock_only_profit = (price - setup.stock_cost_basis) * setup.shares
        if price >= setup.strike:
            covered_call_profit = max_profit_if_assigned
        else:
            covered_call_profit = stock_only_profit + premium_total
        option_effect = covered_call_profit - stock_only_profit
        rows.append(
            CustomerScenarioRow(
                ticker=setup.ticker.upper().strip(),
                scenario_price=round(price, 2),
                stock_only_profit=round(stock_only_profit, 2),
                covered_call_profit=round(covered_call_profit, 2),
                option_effect=round(option_effect, 2),
                assignment_likely=_assignment_likely(price, setup.strike),
                customer_zone=_customer_zone(price, setup),
                explanation=_explanation(price, setup),
            )
        )

    return CustomerScenarioSummary(
        ticker=setup.ticker.upper().strip(),
        current_price=round(setup.current_price, 2),
        strike=round(setup.strike, 2),
        premium=round(setup.premium, 2),
        breakeven=round(breakeven, 2),
        max_profit_if_assigned=round(max_profit_if_assigned, 2),
        downside_cushion_dollars=round(downside_cushion_dollars, 2),
        downside_cushion_percent=round(downside_cushion_percent, 2),
        assignment_zone_starts_at=round(setup.strike, 2),
        number_of_scenarios=len(rows),
        warnings=build_customer_warnings(setup),
        rows=tuple(rows),
    )


def update_customer_scenario_overlay(
    base_setup: CustomerScenarioInput,
    *,
    current_price: float | None = None,
    strike: float | None = None,
    premium: float | None = None,
    stock_cost_basis: float | None = None,
    scenario_prices: Iterable[float] | None = None,
) -> CustomerScenarioSummary:
    """One-call update hook for future dashboard buttons and widgets."""

    updated_current = base_setup.current_price if current_price is None else float(current_price)
    updated_strike = base_setup.strike if strike is None else float(strike)
    updated_premium = base_setup.premium if premium is None else float(premium)
    updated_cost_basis = base_setup.stock_cost_basis if stock_cost_basis is None else float(stock_cost_basis)
    if scenario_prices is None:
        updated_scenarios = build_default_scenario_prices(updated_current, updated_strike)
    else:
        updated_scenarios = tuple(float(x) for x in scenario_prices)

    updated_setup = CustomerScenarioInput(
        ticker=base_setup.ticker,
        current_price=updated_current,
        shares=base_setup.shares,
        strike=updated_strike,
        premium=updated_premium,
        stock_cost_basis=updated_cost_basis,
        scenario_prices=updated_scenarios,
        note=base_setup.note,
    )
    return build_customer_scenario_overlay(updated_setup)


def save_customer_scenario_overlay_csv(
    summary: CustomerScenarioSummary,
    output_path: Path | None = None,
) -> Path:
    """Save the customer scenario overlay rows to CSV."""

    if output_path is None:
        output_path = OUTPUT_DIR / "phase3e_customer_scenario_overlay.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "ticker",
                "scenario_price",
                "stock_only_profit",
                "covered_call_profit",
                "option_effect",
                "assignment_likely",
                "customer_zone",
                "explanation",
            ],
        )
        writer.writeheader()
        for row in summary.rows:
            writer.writerow(asdict(row))

    return output_path


def save_customer_scenario_setup_json(
    setup: CustomerScenarioInput,
    output_path: Path | None = None,
) -> Path:
    """Save the current customer scenario setup for later reload."""

    if output_path is None:
        output_path = SAVED_SETUP_DIR / "phase3e_customer_scenario_setup.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = asdict(setup)
    payload["scenario_prices"] = list(setup.scenario_prices)
    payload["saved_at"] = datetime.now().isoformat(timespec="seconds")

    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path


def load_customer_scenario_setup_json(input_path: Path) -> CustomerScenarioInput:
    """Reload a previously saved customer scenario setup."""

    payload = json.loads(input_path.read_text(encoding="utf-8"))
    return CustomerScenarioInput(
        ticker=str(payload.get("ticker", "SPY")),
        current_price=float(payload.get("current_price", 545.25)),
        shares=int(payload.get("shares", 100)),
        strike=float(payload.get("strike", 555.0)),
        premium=float(payload.get("premium", 4.5)),
        stock_cost_basis=float(payload.get("stock_cost_basis", payload.get("current_price", 545.25))),
        scenario_prices=tuple(float(x) for x in payload.get("scenario_prices", ())),
        note=str(payload.get("note", "Reloaded customer scenario setup")),
    )


def build_customer_scenario_report(summary: CustomerScenarioSummary) -> str:
    """Build a plain-text customer checkpoint report."""

    lines = [
        "Phase 3E-4 customer scenario-overlay checkpoint report",
        "=" * 72,
        "",
        f"Ticker:                     {summary.ticker}",
        f"Current price:              ${summary.current_price:,.2f}",
        f"Strike:                     ${summary.strike:,.2f}",
        f"Premium:                    ${summary.premium:,.2f}",
        f"Breakeven:                  ${summary.breakeven:,.2f}",
        f"Max profit if assigned:     ${summary.max_profit_if_assigned:,.2f}",
        f"Downside cushion:           ${summary.downside_cushion_dollars:,.2f} ({summary.downside_cushion_percent:.2f}%)",
        f"Assignment zone starts at:  ${summary.assignment_zone_starts_at:,.2f}",
        f"Number of scenarios:        {summary.number_of_scenarios}",
        "",
        "Warnings",
        "-" * 72,
    ]

    if summary.warnings:
        lines.extend(f"WARNING: {warning}" for warning in summary.warnings)
    else:
        lines.append("No customer warning boxes triggered for this checkpoint setup.")

    lines.extend(["", "Scenario rows", "-" * 72])
    for row in summary.rows:
        lines.append(
            f"${row.scenario_price:,.2f}: {row.customer_zone}; "
            f"covered-call P/L ${row.covered_call_profit:,.2f}; "
            f"assignment likely: {row.assignment_likely}"
        )

    return "\n".join(lines) + "\n"


def save_customer_scenario_report(
    summary: CustomerScenarioSummary,
    output_path: Path | None = None,
) -> Path:
    """Save the customer scenario report."""

    if output_path is None:
        output_path = REPORT_DIR / "phase3e_customer_scenario_overlay_checkpoint_report.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_customer_scenario_report(summary), encoding="utf-8")
    return output_path


def run_phase3e_customer_scenario_checkpoint() -> dict[str, Path | CustomerScenarioSummary]:
    """Run the standalone Phase 3E-4 checkpoint workflow."""

    setup = CustomerScenarioInput()
    summary = build_customer_scenario_overlay(setup)
    csv_path = save_customer_scenario_overlay_csv(summary)
    setup_path = save_customer_scenario_setup_json(setup)
    reloaded_setup = load_customer_scenario_setup_json(setup_path)
    reloaded_summary = update_customer_scenario_overlay(reloaded_setup, current_price=550.0)
    updated_csv_path = save_customer_scenario_overlay_csv(
        reloaded_summary,
        OUTPUT_DIR / "phase3e_customer_scenario_overlay_updated.csv",
    )
    report_path = save_customer_scenario_report(reloaded_summary)

    return {
        "initial_summary": summary,
        "updated_summary": reloaded_summary,
        "csv_path": csv_path,
        "updated_csv_path": updated_csv_path,
        "setup_path": setup_path,
        "report_path": report_path,
    }
