"""
phase3e_customer_payoff_workbench.py

Phase 3E-5 customer payoff workbench for the Covered Call Simulator.

This module combines the earlier Phase 3E customer-facing pieces into one
standalone workflow that can later be placed into the paid Streamlit dashboard.
It intentionally avoids developer/test controls and does not require Streamlit.

Customer workflow covered here
------------------------------
1. Validate a covered-call setup.
2. Calculate clear payoff labels and summary metrics.
3. Build a scenario overlay around current price and strike.
4. Generate customer-safe risk warnings.
5. Save/reload a setup in JSON.
6. Export scenario rows in CSV.
7. Write a plain-text customer summary report.

All paths are project-root relative and are safe for PyCharm checkpoint runs.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable
import csv
import json


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
SAVED_SETUP_DIR = PROJECT_ROOT / "outputs" / "saved_setups" / "paid_simulator"


@dataclass(frozen=True)
class CustomerPayoffWorkbenchInput:
    """Customer-facing covered-call setup for the Phase 3E payoff workbench."""

    ticker: str = "SPY"
    current_price: float = 545.25
    stock_cost_basis: float = 545.25
    strike_price: float = 555.00
    premium: float = 4.50
    shares: int = 100
    expiration_date: str = ""
    setup_name: str = "Customer payoff workflow setup"
    scenario_prices: tuple[float, ...] = ()
    notes: str = ""


@dataclass(frozen=True)
class CustomerPayoffMetricCard:
    """One visible customer metric card."""

    label: str
    value: str
    explanation: str


@dataclass(frozen=True)
class CustomerRiskWarning:
    """One customer-safe warning box."""

    level: str
    title: str
    message: str


@dataclass(frozen=True)
class CustomerScenarioOverlayRow:
    """One row in the customer scenario overlay table."""

    scenario_price: float
    stock_only_profit: float
    covered_call_profit: float
    option_effect: float
    assignment_zone: str
    customer_zone: str
    explanation: str


@dataclass(frozen=True)
class CustomerPayoffWorkbenchResult:
    """Complete result returned by the customer payoff workbench."""

    ticker: str
    setup_name: str
    current_price: float
    stock_cost_basis: float
    strike_price: float
    premium: float
    shares: int
    expiration_date: str
    breakeven_price: float
    premium_income: float
    max_profit_if_assigned: float
    max_profit_percent: float
    downside_cushion_dollars: float
    downside_cushion_percent: float
    upside_to_strike_dollars: float
    upside_to_strike_percent: float
    assignment_zone_starts_at: float
    metric_cards: tuple[CustomerPayoffMetricCard, ...]
    warnings: tuple[CustomerRiskWarning, ...]
    scenario_rows: tuple[CustomerScenarioOverlayRow, ...]


class CustomerPayoffWorkbenchError(ValueError):
    """Raised when a customer payoff setup cannot be processed."""


def _money(value: float) -> str:
    return f"${value:,.2f}"


def _percent(value: float) -> str:
    return f"{value:.2f}%"


def _clean_ticker(ticker: str) -> str:
    return ticker.upper().strip()


def validate_workbench_input(setup: CustomerPayoffWorkbenchInput) -> None:
    """Validate customer-facing setup values before calculating metrics."""

    if not setup.ticker.strip():
        raise CustomerPayoffWorkbenchError("Ticker is required.")
    if setup.current_price <= 0:
        raise CustomerPayoffWorkbenchError("Current stock price must be greater than zero.")
    if setup.stock_cost_basis <= 0:
        raise CustomerPayoffWorkbenchError("Stock cost basis must be greater than zero.")
    if setup.strike_price <= 0:
        raise CustomerPayoffWorkbenchError("Call strike price must be greater than zero.")
    if setup.premium < 0:
        raise CustomerPayoffWorkbenchError("Premium cannot be negative.")
    if setup.shares <= 0:
        raise CustomerPayoffWorkbenchError("Share count must be greater than zero.")
    if setup.scenario_prices:
        for price in setup.scenario_prices:
            if price <= 0:
                raise CustomerPayoffWorkbenchError("Scenario prices must be greater than zero.")


def build_default_scenario_prices(current_price: float, strike_price: float) -> tuple[float, ...]:
    """Build a compact scenario range around the current price and strike."""

    low_anchor = min(current_price, strike_price)
    high_anchor = max(current_price, strike_price)
    raw_prices = (
        low_anchor * 0.90,
        current_price * 0.97,
        current_price,
        strike_price,
        high_anchor * 1.03,
        high_anchor * 1.10,
    )
    return tuple(sorted({round(price, 2) for price in raw_prices}))


def build_customer_warnings(setup: CustomerPayoffWorkbenchInput) -> tuple[CustomerRiskWarning, ...]:
    """Build customer-safe warning boxes for the covered-call setup."""

    validate_workbench_input(setup)

    warnings: list[CustomerRiskWarning] = []
    upside_room = setup.strike_price - setup.current_price
    upside_room_pct = upside_room / setup.current_price * 100.0
    cushion_pct = setup.premium / setup.stock_cost_basis * 100.0
    max_profit = ((setup.strike_price - setup.stock_cost_basis) + setup.premium) * setup.shares

    if setup.strike_price < setup.current_price:
        warnings.append(
            CustomerRiskWarning(
                level="high",
                title="Strike is already below the current stock price",
                message=(
                    "The covered call is already in the assignment zone. Upside is capped "
                    "and assignment risk is elevated."
                ),
            )
        )
    elif upside_room_pct < 1.0:
        warnings.append(
            CustomerRiskWarning(
                level="medium",
                title="Strike is close to the current stock price",
                message=(
                    "The trade has limited room before the assignment zone begins. A small "
                    "move higher could cap additional stock gains."
                ),
            )
        )

    if cushion_pct < 0.5:
        warnings.append(
            CustomerRiskWarning(
                level="medium",
                title="Small downside cushion",
                message=(
                    "The option premium offsets less than 0.5% of the stock cost basis. "
                    "A modest stock decline can exceed the premium received."
                ),
            )
        )
    elif cushion_pct < 1.0:
        warnings.append(
            CustomerRiskWarning(
                level="low",
                title="Modest downside cushion",
                message=(
                    "The premium provides some cushion, but the stock still carries most "
                    "of the downside risk."
                ),
            )
        )

    if max_profit <= 0:
        warnings.append(
            CustomerRiskWarning(
                level="high",
                title="Maximum profit is not positive",
                message=(
                    "Using the displayed cost basis, strike, and premium, the assigned "
                    "outcome does not produce a positive maximum profit."
                ),
            )
        )

    if setup.premium > setup.current_price * 0.08:
        warnings.append(
            CustomerRiskWarning(
                level="medium",
                title="Premium looks unusually large",
                message=(
                    "The premium is more than 8% of the current stock price. Confirm the "
                    "option quote, expiration, and multiplier before relying on this setup."
                ),
            )
        )

    if not warnings:
        warnings.append(
            CustomerRiskWarning(
                level="info",
                title="No major setup warnings detected",
                message=(
                    "The setup passed the basic customer-facing checks. This does not mean "
                    "the trade is risk-free; the stock can still decline."
                ),
            )
        )

    return tuple(warnings)


def _customer_zone(price: float, setup: CustomerPayoffWorkbenchInput) -> str:
    breakeven = setup.stock_cost_basis - setup.premium
    if price < breakeven:
        return "Below breakeven"
    if price < setup.strike_price:
        return "Profitable uncapped zone"
    return "Assignment zone"


def _scenario_explanation(price: float, setup: CustomerPayoffWorkbenchInput) -> str:
    breakeven = setup.stock_cost_basis - setup.premium
    if price < breakeven:
        return "The stock decline is larger than the premium cushion."
    if price < setup.strike_price:
        return "The stock is above breakeven and below the strike; assignment is not expected."
    return "The stock is at or above the strike; gains are capped by likely assignment."


def build_scenario_overlay(setup: CustomerPayoffWorkbenchInput) -> tuple[CustomerScenarioOverlayRow, ...]:
    """Build customer-facing scenario rows for one covered-call setup."""

    validate_workbench_input(setup)
    prices = setup.scenario_prices or build_default_scenario_prices(
        setup.current_price,
        setup.strike_price,
    )
    premium_total = setup.premium * setup.shares
    max_profit_if_assigned = ((setup.strike_price - setup.stock_cost_basis) + setup.premium) * setup.shares

    rows: list[CustomerScenarioOverlayRow] = []
    for price in prices:
        stock_only_profit = (price - setup.stock_cost_basis) * setup.shares
        if price >= setup.strike_price:
            covered_call_profit = max_profit_if_assigned
            assignment_zone = "Yes"
        else:
            covered_call_profit = stock_only_profit + premium_total
            assignment_zone = "No"

        rows.append(
            CustomerScenarioOverlayRow(
                scenario_price=round(float(price), 2),
                stock_only_profit=round(stock_only_profit, 2),
                covered_call_profit=round(covered_call_profit, 2),
                option_effect=round(covered_call_profit - stock_only_profit, 2),
                assignment_zone=assignment_zone,
                customer_zone=_customer_zone(float(price), setup),
                explanation=_scenario_explanation(float(price), setup),
            )
        )

    return tuple(rows)


def build_metric_cards(setup: CustomerPayoffWorkbenchInput) -> tuple[CustomerPayoffMetricCard, ...]:
    """Build clear customer-facing metric cards."""

    validate_workbench_input(setup)
    premium_income = setup.premium * setup.shares
    breakeven = setup.stock_cost_basis - setup.premium
    max_profit = ((setup.strike_price - setup.stock_cost_basis) + setup.premium) * setup.shares
    max_profit_pct = max_profit / (setup.stock_cost_basis * setup.shares) * 100.0
    cushion_pct = setup.premium / setup.stock_cost_basis * 100.0
    upside_to_strike = setup.strike_price - setup.current_price
    upside_to_strike_pct = upside_to_strike / setup.current_price * 100.0

    return (
        CustomerPayoffMetricCard(
            label="Current stock price",
            value=_money(setup.current_price),
            explanation="The stock price used for the current setup.",
        ),
        CustomerPayoffMetricCard(
            label="Call strike price",
            value=_money(setup.strike_price),
            explanation="At or above this price, assignment becomes likely at expiration.",
        ),
        CustomerPayoffMetricCard(
            label="Premium received",
            value=_money(premium_income),
            explanation="Estimated total option income for the displayed share count.",
        ),
        CustomerPayoffMetricCard(
            label="Breakeven price",
            value=_money(breakeven),
            explanation="Approximate stock price where the premium offsets the stock loss.",
        ),
        CustomerPayoffMetricCard(
            label="Maximum profit if assigned",
            value=f"{_money(max_profit)} ({_percent(max_profit_pct)})",
            explanation="Approximate capped profit if the stock finishes at or above the strike.",
        ),
        CustomerPayoffMetricCard(
            label="Downside cushion from premium",
            value=f"{_money(setup.premium)} per share ({_percent(cushion_pct)})",
            explanation="How much the option premium offsets a stock decline before losses begin.",
        ),
        CustomerPayoffMetricCard(
            label="Distance to assignment zone",
            value=f"{_money(upside_to_strike)} ({_percent(upside_to_strike_pct)})",
            explanation="How far the current stock price is from the call strike.",
        ),
    )


def build_customer_payoff_workbench(
    setup: CustomerPayoffWorkbenchInput,
) -> CustomerPayoffWorkbenchResult:
    """Run the complete customer payoff workbench workflow."""

    validate_workbench_input(setup)

    premium_income = setup.premium * setup.shares
    breakeven = setup.stock_cost_basis - setup.premium
    max_profit = ((setup.strike_price - setup.stock_cost_basis) + setup.premium) * setup.shares
    stock_value = setup.stock_cost_basis * setup.shares
    max_profit_pct = max_profit / stock_value * 100.0
    cushion_pct = setup.premium / setup.stock_cost_basis * 100.0
    upside_to_strike = setup.strike_price - setup.current_price
    upside_to_strike_pct = upside_to_strike / setup.current_price * 100.0

    return CustomerPayoffWorkbenchResult(
        ticker=_clean_ticker(setup.ticker),
        setup_name=setup.setup_name,
        current_price=round(setup.current_price, 2),
        stock_cost_basis=round(setup.stock_cost_basis, 2),
        strike_price=round(setup.strike_price, 2),
        premium=round(setup.premium, 2),
        shares=setup.shares,
        expiration_date=setup.expiration_date,
        breakeven_price=round(breakeven, 2),
        premium_income=round(premium_income, 2),
        max_profit_if_assigned=round(max_profit, 2),
        max_profit_percent=round(max_profit_pct, 2),
        downside_cushion_dollars=round(setup.premium, 2),
        downside_cushion_percent=round(cushion_pct, 2),
        upside_to_strike_dollars=round(upside_to_strike, 2),
        upside_to_strike_percent=round(upside_to_strike_pct, 2),
        assignment_zone_starts_at=round(setup.strike_price, 2),
        metric_cards=build_metric_cards(setup),
        warnings=build_customer_warnings(setup),
        scenario_rows=build_scenario_overlay(setup),
    )


def update_customer_payoff_workbench(
    setup: CustomerPayoffWorkbenchInput,
    *,
    current_price: float | None = None,
    stock_cost_basis: float | None = None,
    strike_price: float | None = None,
    premium: float | None = None,
    shares: int | None = None,
    scenario_prices: Iterable[float] | None = None,
) -> CustomerPayoffWorkbenchResult:
    """One-call scenario update hook for future customer dashboard controls."""

    updated = CustomerPayoffWorkbenchInput(
        ticker=setup.ticker,
        current_price=setup.current_price if current_price is None else float(current_price),
        stock_cost_basis=setup.stock_cost_basis if stock_cost_basis is None else float(stock_cost_basis),
        strike_price=setup.strike_price if strike_price is None else float(strike_price),
        premium=setup.premium if premium is None else float(premium),
        shares=setup.shares if shares is None else int(shares),
        expiration_date=setup.expiration_date,
        setup_name=setup.setup_name,
        scenario_prices=setup.scenario_prices if scenario_prices is None else tuple(float(p) for p in scenario_prices),
        notes=setup.notes,
    )
    return build_customer_payoff_workbench(updated)


def _setup_to_payload(setup: CustomerPayoffWorkbenchInput) -> dict[str, Any]:
    payload = asdict(setup)
    payload["ticker"] = _clean_ticker(setup.ticker)
    payload["scenario_prices"] = list(setup.scenario_prices)
    payload["saved_at"] = datetime.now().isoformat(timespec="seconds")
    payload["workflow"] = "Phase 3E customer payoff workbench"
    return payload


def save_customer_workbench_setup(
    setup: CustomerPayoffWorkbenchInput,
    path: Path | None = None,
) -> Path:
    """Save a customer payoff workbench setup as readable JSON."""

    validate_workbench_input(setup)
    target = path or (SAVED_SETUP_DIR / "phase3e_customer_workbench_setup.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(_setup_to_payload(setup), indent=2), encoding="utf-8")
    return target


def load_customer_workbench_setup(path: Path) -> CustomerPayoffWorkbenchInput:
    """Reload a customer payoff workbench setup from JSON."""

    data = json.loads(path.read_text(encoding="utf-8"))
    setup = CustomerPayoffWorkbenchInput(
        ticker=str(data.get("ticker", "SPY")),
        current_price=float(data["current_price"]),
        stock_cost_basis=float(data.get("stock_cost_basis", data["current_price"])),
        strike_price=float(data["strike_price"]),
        premium=float(data["premium"]),
        shares=int(data.get("shares", 100)),
        expiration_date=str(data.get("expiration_date", "")),
        setup_name=str(data.get("setup_name", "Customer payoff workflow setup")),
        scenario_prices=tuple(float(p) for p in data.get("scenario_prices", ())),
        notes=str(data.get("notes", "")),
    )
    validate_workbench_input(setup)
    return setup


def export_customer_workbench_csv(
    result: CustomerPayoffWorkbenchResult,
    path: Path | None = None,
) -> Path:
    """Export scenario overlay rows to CSV."""

    target = path or (OUTPUT_TABLE_DIR / "phase3e_customer_workbench_scenarios.csv")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as file_obj:
        writer = csv.DictWriter(
            file_obj,
            fieldnames=[
                "scenario_price",
                "stock_only_profit",
                "covered_call_profit",
                "option_effect",
                "assignment_zone",
                "customer_zone",
                "explanation",
            ],
        )
        writer.writeheader()
        for row in result.scenario_rows:
            writer.writerow(asdict(row))
    return target


def build_customer_summary_text(result: CustomerPayoffWorkbenchResult) -> str:
    """Build a plain-text customer summary report."""

    lines: list[str] = []
    lines.append("Phase 3E Customer Payoff Workbench Summary")
    lines.append("=" * 64)
    lines.append(f"Setup: {result.setup_name}")
    lines.append(f"Ticker: {result.ticker}")
    lines.append(f"Current stock price: {_money(result.current_price)}")
    lines.append(f"Stock cost basis: {_money(result.stock_cost_basis)}")
    lines.append(f"Call strike price: {_money(result.strike_price)}")
    lines.append(f"Premium: {_money(result.premium)} per share")
    lines.append(f"Shares: {result.shares:,}")
    if result.expiration_date:
        lines.append(f"Expiration date: {result.expiration_date}")
    lines.append("")
    lines.append("Customer payoff labels")
    lines.append("-" * 64)
    for card in result.metric_cards:
        lines.append(f"{card.label}: {card.value}")
        lines.append(f"  {card.explanation}")
    lines.append("")
    lines.append("Risk warnings")
    lines.append("-" * 64)
    for warning in result.warnings:
        lines.append(f"[{warning.level.upper()}] {warning.title}: {warning.message}")
    lines.append("")
    lines.append("Scenario overlay")
    lines.append("-" * 64)
    for row in result.scenario_rows:
        lines.append(
            f"Price {_money(row.scenario_price)} | Covered call P/L {_money(row.covered_call_profit)} | "
            f"Zone: {row.customer_zone} | Assignment: {row.assignment_zone}"
        )
    return "\n".join(lines) + "\n"


def write_customer_summary_report(
    result: CustomerPayoffWorkbenchResult,
    path: Path | None = None,
) -> Path:
    """Write the customer summary report to disk."""

    target = path or (OUTPUT_REPORT_DIR / "phase3e_customer_workbench_summary.txt")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build_customer_summary_text(result), encoding="utf-8")
    return target


def run_phase3e_customer_workbench_checkpoint() -> dict[str, str]:
    """Run a small end-to-end checkpoint for PyCharm."""

    setup = CustomerPayoffWorkbenchInput(
        ticker="SPY",
        current_price=545.25,
        stock_cost_basis=542.00,
        strike_price=555.00,
        premium=4.50,
        shares=100,
        expiration_date="2026-07-17",
        setup_name="Phase 3E-5 checkpoint covered call",
        notes="Standalone customer workbench checkpoint.",
    )
    result = build_customer_payoff_workbench(setup)
    setup_path = save_customer_workbench_setup(setup)
    loaded_setup = load_customer_workbench_setup(setup_path)
    updated_result = update_customer_payoff_workbench(
        loaded_setup,
        current_price=552.50,
        scenario_prices=(520.0, 542.0, 552.5, 555.0, 565.0, 585.0),
    )
    csv_path = export_customer_workbench_csv(updated_result)
    report_path = write_customer_summary_report(updated_result)

    return {
        "setup_path": str(setup_path),
        "csv_path": str(csv_path),
        "report_path": str(report_path),
        "ticker": result.ticker,
        "scenario_rows": str(len(updated_result.scenario_rows)),
        "warning_count": str(len(updated_result.warnings)),
    }
