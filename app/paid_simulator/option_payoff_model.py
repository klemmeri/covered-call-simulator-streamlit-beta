"""
option_payoff_model.py

Phase 2 scaffold for the paid covered-call simulator.

This module provides a standalone, dependency-light approximation of a
single-cycle covered-call outcome. It is intentionally separate from the
existing paid simulator engine so the Phase 2 modeling layer can be tested
without disturbing the working v0.1 dashboard.

The model is not a full options-pricing engine. It approximates the covered-call
tradeoff using:

1. Stock price at entry.
2. Stock price at exit/expiration.
3. Short-call strike.
4. Initial call premium.
5. Contract count.
6. Transaction cost and slippage assumptions.

It produces buy-and-hold P/L, covered-call P/L, and relative result.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class CoveredCallInput:
    """Inputs for one simplified covered-call payoff calculation."""

    ticker: str
    start_price: float
    end_price: float
    strike_price: float
    call_premium: float
    contracts: int = 1
    transaction_cost: float = 0.0
    slippage: float = 0.0


@dataclass(frozen=True)
class CoveredCallPayoff:
    """Output from one simplified covered-call payoff calculation."""

    ticker: str
    contracts: int
    shares: int
    start_price: float
    end_price: float
    strike_price: float
    call_premium: float
    stock_pnl: float
    call_intrinsic_loss: float
    premium_income: float
    transaction_cost_total: float
    slippage_total: float
    buy_hold_pnl: float
    covered_call_pnl: float
    covered_call_minus_buy_hold: float
    assigned: bool

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable dictionary for CSV/report use."""
        return asdict(self)


def calculate_covered_call_payoff(inputs: CoveredCallInput) -> CoveredCallPayoff:
    """
    Calculate a simplified covered-call payoff.

    The short call is treated as a liability at expiration/exit equal to:

        max(end_price - strike_price, 0) * shares

    The covered-call P/L is:

        stock_pnl + premium_income - call_intrinsic_loss - costs - slippage

    Buy-and-hold P/L is simply:

        (end_price - start_price) * shares

    Parameters
    ----------
    inputs:
        Covered-call setup and terminal price.

    Returns
    -------
    CoveredCallPayoff
        Simplified payoff summary.
    """
    if inputs.contracts <= 0:
        raise ValueError("contracts must be positive")
    if inputs.start_price <= 0:
        raise ValueError("start_price must be positive")
    if inputs.end_price <= 0:
        raise ValueError("end_price must be positive")
    if inputs.strike_price <= 0:
        raise ValueError("strike_price must be positive")
    if inputs.call_premium < 0:
        raise ValueError("call_premium cannot be negative")
    if inputs.transaction_cost < 0:
        raise ValueError("transaction_cost cannot be negative")
    if inputs.slippage < 0:
        raise ValueError("slippage cannot be negative")

    shares = int(inputs.contracts) * 100
    stock_pnl = (float(inputs.end_price) - float(inputs.start_price)) * shares
    buy_hold_pnl = stock_pnl
    premium_income = float(inputs.call_premium) * shares
    call_intrinsic_loss = max(float(inputs.end_price) - float(inputs.strike_price), 0.0) * shares
    transaction_cost_total = float(inputs.transaction_cost) * int(inputs.contracts)
    slippage_total = float(inputs.slippage) * shares

    covered_call_pnl = stock_pnl + premium_income - call_intrinsic_loss - transaction_cost_total - slippage_total
    relative = covered_call_pnl - buy_hold_pnl

    return CoveredCallPayoff(
        ticker=str(inputs.ticker).upper(),
        contracts=int(inputs.contracts),
        shares=shares,
        start_price=float(inputs.start_price),
        end_price=float(inputs.end_price),
        strike_price=float(inputs.strike_price),
        call_premium=float(inputs.call_premium),
        stock_pnl=stock_pnl,
        call_intrinsic_loss=call_intrinsic_loss,
        premium_income=premium_income,
        transaction_cost_total=transaction_cost_total,
        slippage_total=slippage_total,
        buy_hold_pnl=buy_hold_pnl,
        covered_call_pnl=covered_call_pnl,
        covered_call_minus_buy_hold=relative,
        assigned=bool(inputs.end_price > inputs.strike_price),
    )


def estimate_demo_call_premium(start_price: float, target_delta: float, target_dte: int) -> float:
    """
    Estimate a simple demonstration premium per share.

    This is intentionally not a Black-Scholes model. It is a stable scaffold
    formula that lets Phase 2 tests connect configuration assumptions to a
    plausible premium scale before a more rigorous pricing model is added.

    The premium increases with price, delta, and square-root time.
    """
    if start_price <= 0:
        raise ValueError("start_price must be positive")
    if target_delta <= 0:
        raise ValueError("target_delta must be positive")
    if target_dte <= 0:
        raise ValueError("target_dte must be positive")

    time_scale = (float(target_dte) / 30.0) ** 0.5
    premium = float(start_price) * float(target_delta) * 0.018 * time_scale
    return round(premium, 2)


def estimate_demo_strike(start_price: float, target_delta: float, target_dte: int) -> float:
    """
    Estimate a simple demonstration strike.

    Lower-delta calls are placed farther out of the money. Higher-delta calls
    are placed closer to the current price. This is a scaffold heuristic only.
    """
    if start_price <= 0:
        raise ValueError("start_price must be positive")
    if target_delta <= 0:
        raise ValueError("target_delta must be positive")
    if target_dte <= 0:
        raise ValueError("target_dte must be positive")

    otm_fraction = max(0.01, 0.12 - float(target_delta) * 0.20)
    time_adjustment = (float(target_dte) / 30.0) ** 0.5
    strike = float(start_price) * (1.0 + otm_fraction * time_adjustment)
    return round(strike, 2)
