"""
phase3e_customer_payoff_labels.py

Phase 3E-3 customer-facing payoff labels and risk warnings for the
Covered Call Simulator paid dashboard workflow.

This module is intentionally standalone. It does not alter the existing
Phase 3D viewer or the main Streamlit dashboard. It provides plain-English
labels, payoff metric summaries, and warning messages that can later be
wired into the customer-facing Pro dashboard.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class CoveredCallSetup:
    """Basic covered-call setup used for customer-facing payoff labels."""

    ticker: str
    current_price: float
    strike_price: float
    premium: float
    shares: int = 100
    contracts: int = 1

    def validate(self) -> None:
        if not self.ticker.strip():
            raise ValueError("Ticker is required.")
        if self.current_price <= 0:
            raise ValueError("Current price must be greater than zero.")
        if self.strike_price <= 0:
            raise ValueError("Strike price must be greater than zero.")
        if self.premium < 0:
            raise ValueError("Premium cannot be negative.")
        if self.shares <= 0:
            raise ValueError("Shares must be greater than zero.")
        if self.contracts <= 0:
            raise ValueError("Contracts must be greater than zero.")


@dataclass(frozen=True)
class CustomerPayoffLabels:
    """Customer-ready payoff label set."""

    ticker_label: str
    current_price_label: str
    strike_label: str
    premium_label: str
    breakeven_label: str
    max_profit_label: str
    downside_cushion_label: str
    assignment_zone_label: str
    expiration_outcome_label: str
    plain_english_summary: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class RiskWarning:
    """Customer-facing warning message."""

    level: str
    title: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def dollars(value: float) -> str:
    """Format a value as dollars."""
    return f"${value:,.2f}"


def pct(value: float) -> str:
    """Format a decimal ratio as a percentage."""
    return f"{value * 100:.1f}%"


def compute_customer_metrics(setup: CoveredCallSetup) -> dict[str, float]:
    """Compute covered-call payoff metrics for customer display."""
    setup.validate()

    shares_controlled = setup.shares * setup.contracts
    stock_cost = setup.current_price * shares_controlled
    total_premium = setup.premium * shares_controlled
    breakeven = setup.current_price - setup.premium
    max_profit_per_share = max(setup.strike_price - setup.current_price, 0) + setup.premium
    max_profit = max_profit_per_share * shares_controlled
    downside_cushion_pct = setup.premium / setup.current_price
    upside_to_strike_pct = (setup.strike_price - setup.current_price) / setup.current_price

    return {
        "shares_controlled": float(shares_controlled),
        "stock_cost": stock_cost,
        "total_premium": total_premium,
        "breakeven": breakeven,
        "max_profit": max_profit,
        "max_profit_per_share": max_profit_per_share,
        "downside_cushion_pct": downside_cushion_pct,
        "upside_to_strike_pct": upside_to_strike_pct,
    }


def build_customer_payoff_labels(setup: CoveredCallSetup) -> CustomerPayoffLabels:
    """Build customer-facing labels for the payoff workflow."""
    metrics = compute_customer_metrics(setup)
    ticker = setup.ticker.upper().strip()

    if setup.strike_price > setup.current_price:
        assignment_zone = (
            f"Assignment becomes likely if {ticker} finishes above "
            f"the {dollars(setup.strike_price)} strike at expiration."
        )
        expiration_outcome = (
            "If the stock is above the strike at expiration, the shares may be called away. "
            "If it is below the strike, you usually keep the shares and the option premium."
        )
    elif setup.strike_price == setup.current_price:
        assignment_zone = (
            f"The strike is at the current price, so assignment risk can become active quickly."
        )
        expiration_outcome = (
            "This at-the-money setup collects more premium but gives the stock little room "
            "to rise before assignment risk becomes important."
        )
    else:
        assignment_zone = (
            f"The strike is already below the current price, so this setup is already in the assignment zone."
        )
        expiration_outcome = (
            "This in-the-money setup behaves more like a defensive income trade. "
            "It has less upside participation and a higher chance of assignment."
        )

    summary = (
        f"This covered call on {ticker} collects {dollars(metrics['total_premium'])} in option premium. "
        f"The breakeven price is {dollars(metrics['breakeven'])}. "
        f"The maximum profit at expiration is about {dollars(metrics['max_profit'])} "
        f"if the stock finishes at or above {dollars(setup.strike_price)}."
    )

    return CustomerPayoffLabels(
        ticker_label=f"Ticker: {ticker}",
        current_price_label=f"Current stock price: {dollars(setup.current_price)}",
        strike_label=f"Covered-call strike: {dollars(setup.strike_price)}",
        premium_label=(
            f"Option premium collected: {dollars(setup.premium)} per share "
            f"({dollars(metrics['total_premium'])} total)"
        ),
        breakeven_label=f"Breakeven at expiration: {dollars(metrics['breakeven'])}",
        max_profit_label=f"Maximum profit at expiration: {dollars(metrics['max_profit'])}",
        downside_cushion_label=(
            f"Downside cushion from premium: {pct(metrics['downside_cushion_pct'])}"
        ),
        assignment_zone_label=assignment_zone,
        expiration_outcome_label=expiration_outcome,
        plain_english_summary=summary,
    )


def build_risk_warnings(setup: CoveredCallSetup) -> list[RiskWarning]:
    """Return customer-facing warnings for potentially risky setups."""
    metrics = compute_customer_metrics(setup)
    warnings: list[RiskWarning] = []

    if setup.strike_price < setup.current_price:
        warnings.append(
            RiskWarning(
                level="high",
                title="Strike is below the current stock price",
                message=(
                    "This call is already in the money. The setup has a higher chance "
                    "of assignment and gives up more upside if the stock keeps rising."
                ),
            )
        )

    if setup.strike_price == setup.current_price:
        warnings.append(
            RiskWarning(
                level="medium",
                title="Strike is at the current stock price",
                message=(
                    "This setup may collect more premium, but even a small stock rise can "
                    "move the position into the assignment zone."
                ),
            )
        )

    if metrics["downside_cushion_pct"] < 0.01:
        warnings.append(
            RiskWarning(
                level="medium",
                title="Small downside cushion",
                message=(
                    "The premium provides less than 1% downside cushion. A modest stock "
                    "decline could offset the income from the option."
                ),
            )
        )

    if metrics["upside_to_strike_pct"] < 0.01 and setup.strike_price >= setup.current_price:
        warnings.append(
            RiskWarning(
                level="medium",
                title="Limited room before assignment zone",
                message=(
                    "The strike is less than 1% above the current stock price. The trade "
                    "has limited upside room before assignment risk becomes important."
                ),
            )
        )

    if setup.premium > setup.current_price * 0.08:
        warnings.append(
            RiskWarning(
                level="review",
                title="Unusually large premium",
                message=(
                    "The premium is more than 8% of the stock price. Confirm that the "
                    "option price, expiration, and contract multiplier are correct."
                ),
            )
        )

    if not warnings:
        warnings.append(
            RiskWarning(
                level="info",
                title="No major setup warning detected",
                message=(
                    "This does not mean the trade is risk-free. The stock can still fall "
                    "more than the premium collected."
                ),
            )
        )

    return warnings


def build_customer_payoff_view_model(setup: CoveredCallSetup) -> dict[str, Any]:
    """Build a complete customer-facing view model for Streamlit integration."""
    return {
        "setup": asdict(setup),
        "metrics": compute_customer_metrics(setup),
        "labels": build_customer_payoff_labels(setup).to_dict(),
        "warnings": [warning.to_dict() for warning in build_risk_warnings(setup)],
    }


def demo_setup() -> CoveredCallSetup:
    """Return a stable demo setup used by the Phase 3E-3 check script."""
    return CoveredCallSetup(
        ticker="SPY",
        current_price=545.25,
        strike_price=555.00,
        premium=4.80,
        shares=100,
        contracts=1,
    )


if __name__ == "__main__":
    import json

    print(json.dumps(build_customer_payoff_view_model(demo_setup()), indent=2))
