"""
account.py

Account-size and position-size logic for the paid Covered Call Simulator.

This module answers a basic practical question:

    Can the selected account reasonably support one covered-call contract
    under the chosen position-size cap?

Important:
    Passing the account screen does not mean a trade is recommended.
    It only means the ticker fits the selected account-size rule.
"""

from __future__ import annotations

from models import (
    AccountFeasibility,
    SimulationInput,
    TickerSnapshot,
)


def get_position_size_cap(
    risk_tier: str,
    ticker: str | None = None,
) -> float:
    """
    Return the default per-position cap for a selected risk tier.

    Parameters
    ----------
    risk_tier:
        User-selected risk tier. Expected values include:
        Conservative, Balanced, Aggressive.

    ticker:
        Optional ticker symbol. Reserved for later ticker-specific adjustments.

    Returns
    -------
    float
        Position-size cap as a decimal.

    Notes
    -----
    These are starting assumptions only. Leveraged ETFs or volatile products
    may require lower caps in future versions.
    """
    normalized_tier = risk_tier.strip().lower()

    if normalized_tier == "conservative":
        return 0.05

    if normalized_tier == "balanced":
        return 0.10

    if normalized_tier == "aggressive":
        return 0.20

    raise ValueError(
        "Unknown risk tier. Expected Conservative, Balanced, or Aggressive."
    )


def calculate_minimum_equity_required(
    price: float,
    position_size_cap: float,
    contract_multiplier: int = 100,
) -> float:
    """
    Calculate the minimum account equity required for one covered-call contract.

    Formula
    -------
    stock_value_required = price * contract_multiplier

    minimum_equity_required = stock_value_required / position_size_cap

    Parameters
    ----------
    price:
        Current or simulated underlying price.

    position_size_cap:
        Maximum fraction of the account allowed in one covered-call position.

    contract_multiplier:
        Shares controlled by one option contract. Standard equity options
        usually use 100.

    Returns
    -------
    float
        Estimated minimum account equity.
    """
    if price <= 0:
        raise ValueError("Price must be greater than zero.")

    if position_size_cap <= 0:
        raise ValueError("Position-size cap must be greater than zero.")

    stock_value_required = price * contract_multiplier
    return stock_value_required / position_size_cap


def check_account_feasibility(
    simulation_input: SimulationInput,
    ticker_snapshot: TickerSnapshot,
    contract_multiplier: int = 100,
) -> AccountFeasibility:
    """
    Check whether one covered-call contract fits the selected account rules.

    Parameters
    ----------
    simulation_input:
        User-selected simulator assumptions.

    ticker_snapshot:
        Current or historical ticker snapshot.

    contract_multiplier:
        Shares controlled by one option contract.

    Returns
    -------
    AccountFeasibility
        Account-screen result.
    """
    ticker = simulation_input.ticker.upper().strip()
    price = ticker_snapshot.price
    account_size = simulation_input.account_size
    position_size_cap = simulation_input.position_size_cap

    if price is None:
        return AccountFeasibility(
            ticker=ticker,
            price=None,
            shares_required=contract_multiplier,
            contract_multiplier=contract_multiplier,
            stock_value_required=None,
            account_size=account_size,
            position_size_cap=position_size_cap,
            minimum_equity_required=None,
            passes_account_screen=False,
            reason="Price is unavailable, so account feasibility cannot be calculated.",
        )

    stock_value_required = price * contract_multiplier
    minimum_equity_required = calculate_minimum_equity_required(
        price=price,
        position_size_cap=position_size_cap,
        contract_multiplier=contract_multiplier,
    )

    passes_account_screen = account_size >= minimum_equity_required

    if passes_account_screen:
        reason = (
            "One covered-call contract fits within the selected account-size "
            "and position-size cap."
        )
    else:
        reason = (
            "One covered-call contract exceeds the selected account-size "
            "and position-size cap."
        )

    return AccountFeasibility(
        ticker=ticker,
        price=price,
        shares_required=contract_multiplier,
        contract_multiplier=contract_multiplier,
        stock_value_required=stock_value_required,
        account_size=account_size,
        position_size_cap=position_size_cap,
        minimum_equity_required=minimum_equity_required,
        passes_account_screen=passes_account_screen,
        reason=reason,
    )
