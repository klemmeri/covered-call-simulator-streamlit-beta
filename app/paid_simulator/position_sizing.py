"""
position_sizing.py

Position-sizing calculations for the paid Covered Call Simulator.

Purpose:
    Convert account size, ticker price, position-size cap, and desired
    contract count into practical covered-call capacity.

Covered calls are contract-based. One standard contract requires:

    100 shares

Therefore, even if a strategy is attractive, the account may not be large
enough to hold the desired number of contracts without violating the selected
position-size cap.
"""

from __future__ import annotations

from math import floor
from typing import Any

from models import (
    SimulationInput,
    TickerSnapshot,
)


DEFAULT_CONTRACT_MULTIPLIER = 100


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Convert a value to float safely.
    """
    if value is None:
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """
    Convert a value to int safely.
    """
    if value is None:
        return default

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def round_money(value: Any) -> float:
    """
    Round a numeric value to two decimal places.
    """
    return round(safe_float(value), 2)


def calculate_position_sizing(
    simulation_input: SimulationInput,
    ticker_snapshot: TickerSnapshot,
    contract_multiplier: int = DEFAULT_CONTRACT_MULTIPLIER,
    desired_contracts: int = 1,
) -> dict[str, object]:
    """
    Calculate practical covered-call position capacity.

    Parameters
    ----------
    simulation_input:
        Paid simulator assumptions.

    ticker_snapshot:
        Current or illustrative ticker price snapshot.

    contract_multiplier:
        Standard equity-option contract multiplier. Usually 100.

    desired_contracts:
        Number of covered-call contracts the user wants to evaluate.

    Returns
    -------
    dict[str, object]
        Position-sizing summary.
    """
    account_size = safe_float(simulation_input.account_size)
    stock_price = safe_float(ticker_snapshot.price)
    position_size_cap = safe_float(simulation_input.position_size_cap)
    desired_contracts = max(safe_int(desired_contracts, 1), 0)

    if account_size <= 0:
        raise ValueError("Account size must be greater than zero.")

    if stock_price <= 0:
        raise ValueError("Ticker price must be greater than zero.")

    if position_size_cap <= 0:
        raise ValueError("Position-size cap must be greater than zero.")

    stock_value_per_contract = stock_price * contract_multiplier
    allowed_position_value = account_size * position_size_cap
    minimum_equity_required = stock_value_per_contract / position_size_cap

    max_contracts_allowed = int(
        floor(allowed_position_value / stock_value_per_contract)
    )

    passes_account_screen = max_contracts_allowed >= 1

    desired_position_value = desired_contracts * stock_value_per_contract
    desired_position_percent = desired_position_value / account_size

    required_equity_for_desired_contracts = (
        desired_position_value / position_size_cap
        if desired_contracts > 0
        else 0.0
    )

    desired_contracts_pass_screen = desired_contracts <= max_contracts_allowed

    required_extra_equity_for_desired_contracts = max(
        required_equity_for_desired_contracts - account_size,
        0.0,
    )

    used_position_value_at_max_contracts = (
        max_contracts_allowed * stock_value_per_contract
    )

    remaining_position_capacity = (
        allowed_position_value - used_position_value_at_max_contracts
    )

    required_extra_equity_for_one_contract = max(
        minimum_equity_required - account_size,
        0.0,
    )

    return {
        "ticker": simulation_input.ticker,
        "account_size": round_money(account_size),
        "risk_tier": simulation_input.risk_tier,
        "position_size_cap": position_size_cap,
        "stock_price": round_money(stock_price),
        "contract_multiplier": contract_multiplier,
        "desired_contracts": desired_contracts,
        "stock_value_per_contract": round_money(stock_value_per_contract),
        "allowed_position_value": round_money(allowed_position_value),
        "minimum_equity_required": round_money(minimum_equity_required),
        "max_contracts_allowed": max_contracts_allowed,
        "passes_account_screen": passes_account_screen,
        "desired_position_value": round_money(desired_position_value),
        "desired_position_percent": desired_position_percent,
        "required_equity_for_desired_contracts": round_money(
            required_equity_for_desired_contracts
        ),
        "desired_contracts_pass_screen": desired_contracts_pass_screen,
        "required_extra_equity_for_desired_contracts": round_money(
            required_extra_equity_for_desired_contracts
        ),
        "used_position_value_at_max_contracts": round_money(
            used_position_value_at_max_contracts
        ),
        "remaining_position_capacity": round_money(remaining_position_capacity),
        "required_extra_equity_for_one_contract": round_money(
            required_extra_equity_for_one_contract
        ),
    }


def format_money(value: Any) -> str:
    """
    Format a value as dollars.
    """
    return f"${safe_float(value):,.2f}"


def format_percent(value: Any) -> str:
    """
    Format a decimal value as a percentage.
    """
    return f"{safe_float(value):.2%}"


def format_position_sizing_lines(
    position_sizing: dict[str, object],
) -> list[str]:
    """
    Format position-sizing output for console display.
    """
    return [
        f"Ticker:                         {position_sizing.get('ticker')}",
        f"Account size:                   {format_money(position_sizing.get('account_size'))}",
        f"Risk tier:                      {position_sizing.get('risk_tier')}",
        f"Position-size cap:              {format_percent(position_sizing.get('position_size_cap'))}",
        f"Underlying price:               {format_money(position_sizing.get('stock_price'))}",
        f"Contract multiplier:            {position_sizing.get('contract_multiplier')}",
        f"Desired contracts:              {position_sizing.get('desired_contracts')}",
        f"Stock value per contract:       {format_money(position_sizing.get('stock_value_per_contract'))}",
        f"Desired position value:         {format_money(position_sizing.get('desired_position_value'))}",
        f"Desired position percent:       {format_percent(position_sizing.get('desired_position_percent'))}",
        f"Allowed position value:         {format_money(position_sizing.get('allowed_position_value'))}",
        f"Minimum equity for 1 contract:  {format_money(position_sizing.get('minimum_equity_required'))}",
        f"Maximum contracts allowed:      {position_sizing.get('max_contracts_allowed')}",
        f"Passes 1-contract screen:       {position_sizing.get('passes_account_screen')}",
        f"Desired contracts pass screen:  {position_sizing.get('desired_contracts_pass_screen')}",
        f"Equity needed for desired:      {format_money(position_sizing.get('required_equity_for_desired_contracts'))}",
        f"Extra equity needed desired:    {format_money(position_sizing.get('required_extra_equity_for_desired_contracts'))}",
        f"Remaining position capacity:    {format_money(position_sizing.get('remaining_position_capacity'))}",
    ]
