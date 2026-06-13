"""
phase3e_customer_payoff_workflow.py

Phase 3E customer-ready interactive payoff workflow scaffold for the
Covered Call Simulator paid dashboard.

This module is intentionally standalone for the first Phase 3E checkpoint.
It does not modify the existing paid dashboard and does not expose developer
or test-only controls to the customer-facing workflow.

Design goals
------------
1. Present covered-call payoff information in customer-facing language.
2. Keep key setup inputs explicit: current price, strike, premium, contracts.
3. Calculate core payoff metrics consistently.
4. Provide warning-box logic for risky setups.
5. Provide save/export and reload hooks for later Streamlit integration.
6. Remain importable and testable without Streamlit.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXPORT_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
DEFAULT_EXPORT_FILE = DEFAULT_EXPORT_DIR / "phase3e_customer_payoff_setup.json"


@dataclass(frozen=True)
class CoveredCallSetup:
    """
    Customer-facing covered-call setup.

    Parameters
    ----------
    ticker:
        Underlying ticker symbol.
    current_price:
        Current underlying share price.
    strike_price:
        Covered-call strike price.
    premium:
        Option premium received per share.
    contracts:
        Number of covered-call contracts.
    shares_per_contract:
        Standard option contract multiplier. Defaults to 100.
    """

    ticker: str = "SPY"
    current_price: float = 545.25
    strike_price: float = 560.00
    premium: float = 4.50
    contracts: int = 1
    shares_per_contract: int = 100

    def validate(self) -> list[str]:
        """Return validation messages for invalid setup values."""
        errors: list[str] = []

        if not self.ticker.strip():
            errors.append("Ticker is required.")
        if self.current_price <= 0:
            errors.append("Current price must be greater than zero.")
        if self.strike_price <= 0:
            errors.append("Strike price must be greater than zero.")
        if self.premium < 0:
            errors.append("Premium cannot be negative.")
        if self.contracts <= 0:
            errors.append("Contracts must be at least 1.")
        if self.shares_per_contract <= 0:
            errors.append("Shares per contract must be greater than zero.")

        return errors


@dataclass(frozen=True)
class CustomerPayoffMetrics:
    """
    Customer-facing payoff metrics for a covered-call setup.
    """

    ticker: str
    current_price: float
    strike_price: float
    premium: float
    contracts: int
    shares_controlled: int
    gross_premium_income: float
    breakeven_price: float
    downside_cushion_dollars: float
    downside_cushion_percent: float
    max_profit_per_share: float
    max_profit_total: float
    assignment_zone_starts_at: float
    moneyness_label: str
    distance_to_strike_dollars: float
    distance_to_strike_percent: float


@dataclass(frozen=True)
class CustomerWarning:
    """
    A warning or guidance message suitable for customer display.
    """

    severity: str
    title: str
    message: str


CUSTOMER_WORKFLOW_SECTIONS: tuple[str, ...] = (
    "Setup inputs",
    "Payoff summary",
    "Scenario overlay",
    "Risk warnings",
    "Save or export setup",
    "Reload saved setup",
)


CUSTOMER_LABELS: dict[str, str] = {
    "current_price": "Current stock price",
    "strike_price": "Call strike price",
    "premium": "Premium received",
    "breakeven_price": "Breakeven price",
    "max_profit_total": "Maximum profit if assigned",
    "downside_cushion": "Downside cushion from premium",
    "assignment_zone": "Assignment zone",
    "scenario_overlay": "Scenario overlay",
}


def calculate_customer_payoff_metrics(setup: CoveredCallSetup) -> CustomerPayoffMetrics:
    """
    Calculate customer-facing covered-call payoff metrics.

    The covered-call breakeven is approximated as:

        current stock price - premium received

    The maximum profit if assigned is approximated as:

        strike price - current stock price + premium received

    This assumes the customer already owns the shares at the displayed
    current price. Later phases can add tax lots, commissions, and cost basis.
    """
    errors = setup.validate()
    if errors:
        raise ValueError("Invalid covered-call setup: " + "; ".join(errors))

    shares_controlled = setup.contracts * setup.shares_per_contract
    gross_premium_income = setup.premium * shares_controlled
    breakeven_price = setup.current_price - setup.premium
    downside_cushion_dollars = setup.premium
    downside_cushion_percent = setup.premium / setup.current_price * 100.0
    max_profit_per_share = setup.strike_price - setup.current_price + setup.premium
    max_profit_total = max_profit_per_share * shares_controlled
    assignment_zone_starts_at = setup.strike_price
    distance_to_strike_dollars = setup.strike_price - setup.current_price
    distance_to_strike_percent = distance_to_strike_dollars / setup.current_price * 100.0

    if setup.strike_price > setup.current_price:
        moneyness_label = "Out of the money"
    elif setup.strike_price < setup.current_price:
        moneyness_label = "In the money"
    else:
        moneyness_label = "At the money"

    return CustomerPayoffMetrics(
        ticker=setup.ticker.upper().strip(),
        current_price=round(setup.current_price, 2),
        strike_price=round(setup.strike_price, 2),
        premium=round(setup.premium, 2),
        contracts=setup.contracts,
        shares_controlled=shares_controlled,
        gross_premium_income=round(gross_premium_income, 2),
        breakeven_price=round(breakeven_price, 2),
        downside_cushion_dollars=round(downside_cushion_dollars, 2),
        downside_cushion_percent=round(downside_cushion_percent, 2),
        max_profit_per_share=round(max_profit_per_share, 2),
        max_profit_total=round(max_profit_total, 2),
        assignment_zone_starts_at=round(assignment_zone_starts_at, 2),
        moneyness_label=moneyness_label,
        distance_to_strike_dollars=round(distance_to_strike_dollars, 2),
        distance_to_strike_percent=round(distance_to_strike_percent, 2),
    )


def build_customer_warnings(setup: CoveredCallSetup) -> list[CustomerWarning]:
    """
    Build customer-facing warning boxes for the setup.

    The warnings are intentionally conservative. They are not trade advice;
    they flag conditions that a customer should understand before using a
    covered-call setup.
    """
    errors = setup.validate()
    if errors:
        return [
            CustomerWarning(
                severity="error",
                title="Setup needs correction",
                message=" ".join(errors),
            )
        ]

    warnings: list[CustomerWarning] = []
    metrics = calculate_customer_payoff_metrics(setup)

    if setup.strike_price < setup.current_price:
        warnings.append(
            CustomerWarning(
                severity="warning",
                title="Call is already in the assignment zone",
                message=(
                    "The strike is below the current stock price. The position "
                    "has less upside room and a higher chance of assignment."
                ),
            )
        )

    if metrics.max_profit_per_share <= 0:
        warnings.append(
            CustomerWarning(
                severity="warning",
                title="Maximum profit is not positive",
                message=(
                    "Using the displayed current price, strike, and premium, "
                    "the capped upside does not produce a positive maximum profit."
                ),
            )
        )

    if metrics.downside_cushion_percent < 0.5:
        warnings.append(
            CustomerWarning(
                severity="info",
                title="Small downside cushion",
                message=(
                    "The premium provides less than 0.5% downside cushion. "
                    "A modest stock decline could exceed the premium received."
                ),
            )
        )

    if metrics.distance_to_strike_percent < 1.0:
        warnings.append(
            CustomerWarning(
                severity="info",
                title="Strike is close to current price",
                message=(
                    "The strike is within about 1% of the current stock price. "
                    "This may provide more premium but less upside room."
                ),
            )
        )

    if not warnings:
        warnings.append(
            CustomerWarning(
                severity="success",
                title="No major setup warnings",
                message=(
                    "The displayed setup has positive capped upside and a "
                    "clearly defined breakeven based on the premium entered."
                ),
            )
        )

    return warnings


def build_customer_summary(setup: CoveredCallSetup) -> dict[str, Any]:
    """
    Return a complete customer workflow summary.
    """
    metrics = calculate_customer_payoff_metrics(setup)
    warnings = build_customer_warnings(setup)

    return {
        "workflow_name": "Phase 3E Customer Payoff Workflow",
        "sections": list(CUSTOMER_WORKFLOW_SECTIONS),
        "labels": CUSTOMER_LABELS,
        "setup": asdict(setup),
        "metrics": asdict(metrics),
        "warnings": [asdict(item) for item in warnings],
        "export_hook_available": True,
        "reload_hook_available": True,
        "developer_features_visible": False,
    }


def export_customer_setup(
    setup: CoveredCallSetup,
    export_path: Path | str = DEFAULT_EXPORT_FILE,
) -> Path:
    """
    Save a customer payoff setup and calculated summary to JSON.

    This function is the Phase 3E save/export hook. It is already functional
    for JSON export and can later be wired to a Streamlit button.
    """
    path = Path(export_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    summary = build_customer_summary(setup)
    path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return path


def reload_customer_setup(
    import_path: Path | str = DEFAULT_EXPORT_FILE,
) -> CoveredCallSetup:
    """
    Reload a customer payoff setup from a JSON export.

    This function is the Phase 3E reload hook. It expects the JSON structure
    produced by export_customer_setup().
    """
    path = Path(import_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    setup_data = data.get("setup", {})

    return CoveredCallSetup(
        ticker=str(setup_data.get("ticker", "SPY")),
        current_price=float(setup_data.get("current_price", 545.25)),
        strike_price=float(setup_data.get("strike_price", 560.00)),
        premium=float(setup_data.get("premium", 4.50)),
        contracts=int(setup_data.get("contracts", 1)),
        shares_per_contract=int(setup_data.get("shares_per_contract", 100)),
    )


def format_customer_metric_lines(metrics: CustomerPayoffMetrics) -> list[str]:
    """
    Format key metrics as plain customer-facing text lines.

    This is useful for simple reports and can also guide Streamlit copy.
    """
    return [
        f"Ticker: {metrics.ticker}",
        f"Current stock price: ${metrics.current_price:,.2f}",
        f"Call strike price: ${metrics.strike_price:,.2f}",
        f"Premium received: ${metrics.premium:,.2f} per share",
        f"Gross premium income: ${metrics.gross_premium_income:,.2f}",
        f"Breakeven price: ${metrics.breakeven_price:,.2f}",
        f"Maximum profit if assigned: ${metrics.max_profit_total:,.2f}",
        f"Downside cushion from premium: {metrics.downside_cushion_percent:,.2f}%",
        f"Assignment zone starts at: ${metrics.assignment_zone_starts_at:,.2f}",
        f"Moneyness: {metrics.moneyness_label}",
    ]


def run_self_check() -> dict[str, Any]:
    """
    Lightweight module self-check used by the Phase 3E check script.
    """
    setup = CoveredCallSetup()
    summary = build_customer_summary(setup)
    metrics = calculate_customer_payoff_metrics(setup)
    warnings = build_customer_warnings(setup)

    required_sections = set(CUSTOMER_WORKFLOW_SECTIONS)
    observed_sections = set(summary["sections"])

    return {
        "module": "phase3e_customer_payoff_workflow",
        "valid_setup": setup.validate() == [],
        "required_sections_present": required_sections.issubset(observed_sections),
        "customer_labels_present": len(CUSTOMER_LABELS) >= 8,
        "metrics_created": isinstance(metrics, CustomerPayoffMetrics),
        "warnings_created": len(warnings) >= 1,
        "export_hook_available": callable(export_customer_setup),
        "reload_hook_available": callable(reload_customer_setup),
        "developer_features_visible": summary["developer_features_visible"],
    }


if __name__ == "__main__":
    check = run_self_check()
    for key, value in check.items():
        print(f"{key}: {value}")
