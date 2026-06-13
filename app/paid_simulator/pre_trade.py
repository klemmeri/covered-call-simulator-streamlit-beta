"""
pre_trade.py

Pre-trade covered-call impact calculations for the paid Covered Call Simulator.

This module answers the question:

    What does the selected covered call do before the user places it?

It calculates:
    - premium received
    - stock value
    - upside to strike
    - gross if assigned
    - premium yield
    - if-assigned return
    - downside buffer
    - assignment pressure

Important:
    These are simplified estimates. A real version should also include
    bid/ask spread, slippage, commissions, liquidity, taxes, and changing
    option value over time.
"""

from __future__ import annotations

from models import PreTradeImpact, SelectedOption


def classify_assignment_pressure(
    stock_price: float,
    strike_price: float,
    delta: float | None = None,
) -> str:
    """
    Classify simple assignment pressure before the trade is placed.

    Parameters
    ----------
    stock_price:
        Current underlying price.

    strike_price:
        Selected call strike.

    delta:
        Selected call delta, if available.

    Returns
    -------
    str
        Assignment-pressure label.
    """
    if stock_price <= 0:
        return "unknown"

    distance_percent = (strike_price - stock_price) / stock_price

    if strike_price <= stock_price:
        return "high_itm_or_atm"

    if delta is not None:
        if delta >= 0.40:
            return "elevated"
        if delta >= 0.25:
            return "moderate"
        return "lower"

    if distance_percent <= 0.01:
        return "elevated"

    if distance_percent <= 0.05:
        return "moderate"

    return "lower"


def calculate_pre_trade_impact(
    stock_price: float,
    strike_price: float,
    option_price: float,
    delta: float | None = None,
    contract_multiplier: int = 100,
) -> PreTradeImpact:
    """
    Calculate simplified pre-trade impact metrics for one covered call.

    Parameters
    ----------
    stock_price:
        Current underlying price.

    strike_price:
        Selected call strike.

    option_price:
        Selected call price per share.

    delta:
        Selected call delta, if available.

    contract_multiplier:
        Standard equity option multiplier, usually 100.

    Returns
    -------
    PreTradeImpact
        Pre-trade covered-call impact result.
    """
    if stock_price <= 0:
        raise ValueError("Stock price must be greater than zero.")

    if strike_price <= 0:
        raise ValueError("Strike price must be greater than zero.")

    if option_price < 0:
        raise ValueError("Option price cannot be negative.")

    if contract_multiplier <= 0:
        raise ValueError("Contract multiplier must be greater than zero.")

    stock_value = stock_price * contract_multiplier
    premium_cash = option_price * contract_multiplier

    upside_to_strike = max(strike_price - stock_price, 0.0) * contract_multiplier
    gross_if_assigned = upside_to_strike + premium_cash

    premium_yield = premium_cash / stock_value
    if_assigned_return = gross_if_assigned / stock_value
    downside_buffer = option_price / stock_price

    assignment_pressure = classify_assignment_pressure(
        stock_price=stock_price,
        strike_price=strike_price,
        delta=delta,
    )

    notes = (
        "Simplified pre-trade estimate. Premium is not the same as profit; "
        "the short call becomes a liability after placement."
    )

    return PreTradeImpact(
        stock_price=stock_price,
        strike=strike_price,
        premium_per_share=option_price,
        contract_multiplier=contract_multiplier,
        stock_value=stock_value,
        premium_cash=premium_cash,
        upside_to_strike=upside_to_strike,
        gross_if_assigned=gross_if_assigned,
        premium_yield=premium_yield,
        if_assigned_return=if_assigned_return,
        downside_buffer=downside_buffer,
        assignment_pressure=assignment_pressure,
        notes=notes,
    )


def build_selected_option_from_candidate(
    candidate,
    selection_timestamp,
    transaction_cost_per_contract: float = 0.0,
) -> SelectedOption:
    """
    Convert an OptionCandidate into a SelectedOption.

    Parameters
    ----------
    candidate:
        OptionCandidate selected by the simulator.

    selection_timestamp:
        Timestamp of selection.

    transaction_cost_per_contract:
        Estimated transaction cost.

    Returns
    -------
    SelectedOption
        Selected option model.
    """
    if candidate.mid is None:
        raise ValueError("Candidate mid price is required for this demo step.")

    estimated_premium = candidate.mid * 100
    estimated_transaction_cost = transaction_cost_per_contract
    estimated_net_credit = estimated_premium - estimated_transaction_cost

    return SelectedOption(
        option_candidate_id=candidate.candidate_id,
        ticker=candidate.ticker,
        expiration_date=candidate.expiration_date,
        dte=candidate.dte,
        strike=candidate.strike,
        delta=candidate.delta,
        bid=candidate.bid,
        ask=candidate.ask,
        mid=candidate.mid,
        selected_price=candidate.mid,
        selected_price_source="mid",
        estimated_premium=estimated_premium,
        estimated_transaction_cost=estimated_transaction_cost,
        estimated_net_credit=estimated_net_credit,
        selection_timestamp=selection_timestamp,
        selection_reason=(
            "Selected by strike-selection method using illustrative demo "
            "option candidates."
        ),
    )


def summarize_pre_trade_impact(
    impact: PreTradeImpact,
) -> dict[str, object]:
    """
    Convert pre-trade impact into compact printable values.
    """
    return {
        "stock_price": impact.stock_price,
        "strike": impact.strike,
        "premium_per_share": impact.premium_per_share,
        "stock_value": impact.stock_value,
        "premium_cash": impact.premium_cash,
        "upside_to_strike": impact.upside_to_strike,
        "gross_if_assigned": impact.gross_if_assigned,
        "premium_yield_percent": impact.premium_yield * 100,
        "if_assigned_return_percent": impact.if_assigned_return * 100,
        "downside_buffer_percent": impact.downside_buffer * 100,
        "assignment_pressure": impact.assignment_pressure,
    }
