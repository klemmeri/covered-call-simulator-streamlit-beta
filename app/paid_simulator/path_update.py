"""
path_update.py

One-step market update logic for the paid Covered Call Simulator.

This module supports multi-contract covered-call paths.

For N short calls:
    short-call liability = option mark * 100 * N
    option P/L = (entry option price - current option mark) * 100 * N
    premium collected = entry premium * N

The buy-and-hold benchmark uses the original entry stock price and the same
share count as the covered-call stock position.
"""

from __future__ import annotations

from datetime import datetime

from models import (
    EquitySnapshot,
    PositionState,
    SelectedOption,
    SimulationInput,
)


def round_money(value: float | None) -> float | None:
    """
    Round money-like values to two decimal places.
    """
    if value is None:
        return None

    return round(float(value), 2)


def classify_moneyness(
    stock_price: float,
    strike: float,
) -> str:
    """
    Classify the short call relative to the stock price.
    """
    if stock_price > strike:
        return "ITM"

    if abs(stock_price - strike) <= stock_price * 0.005:
        return "ATM"

    return "OTM"


def classify_assignment_status(
    stock_price: float,
    strike: float,
    dte: int,
) -> str:
    """
    Provide a simple assignment-status label after a market step.
    """
    if stock_price >= strike:
        if dte <= 5:
            return "near_expiration_itm"
        return "itm_monitor"

    distance_percent = (strike - stock_price) / stock_price

    if distance_percent <= 0.01:
        return "near_strike_monitor"

    return "not_under_pressure"


def get_contract_count_from_position(
    position_state: PositionState,
) -> int:
    """
    Infer short-call contract count from the position state.
    """
    quantity = position_state.short_call_quantity

    if quantity is None:
        return 1

    contract_count = abs(int(quantity))

    if contract_count < 1:
        return 1

    return contract_count


def estimate_short_call_mark_after_move(
    previous_stock_price: float,
    new_stock_price: float,
    previous_option_mark: float,
    strike: float,
    delta: float | None,
    days_elapsed: int = 1,
) -> float:
    """
    Estimate the new short-call mark after a stock-price move.

    This is a deliberately simple approximation:

        new mark ~= old mark + delta * stock move - small daily time decay

    The estimate is bounded below by intrinsic value and a small positive
    value so that the option mark remains realistic for demonstration.
    """
    if previous_stock_price <= 0:
        raise ValueError("Previous stock price must be greater than zero.")

    if new_stock_price <= 0:
        raise ValueError("New stock price must be greater than zero.")

    if previous_option_mark < 0:
        raise ValueError("Previous option mark cannot be negative.")

    effective_delta = 0.30 if delta is None else delta

    stock_move = new_stock_price - previous_stock_price
    delta_effect = effective_delta * stock_move

    daily_time_decay = max(previous_option_mark * 0.015, 0.01) * max(days_elapsed, 1)

    intrinsic_value = max(new_stock_price - strike, 0.0)

    estimated_mark = previous_option_mark + delta_effect - daily_time_decay
    bounded_mark = max(estimated_mark, intrinsic_value, 0.01)

    return round(float(bounded_mark), 2)


def calculate_buy_hold_equity(
    starting_account_size: float,
    initial_stock_price: float,
    new_stock_price: float,
    shares: int,
) -> float:
    """
    Calculate a simple buy-and-hold benchmark using the original entry price.
    """
    initial_stock_value = initial_stock_price * shares
    remaining_cash = starting_account_size - initial_stock_value
    current_stock_value = new_stock_price * shares

    return round_money(remaining_cash + current_stock_value)


def calculate_missed_upside(
    stock_price: float,
    strike: float,
    shares: int,
) -> float:
    """
    Calculate simple capped upside when stock trades above the short-call strike.
    """
    return round_money(max(stock_price - strike, 0.0) * shares)


def update_position_after_market_step(
    simulation_input: SimulationInput,
    previous_position_state: PositionState,
    selected_option: SelectedOption,
    new_timestamp: datetime,
    new_stock_price: float,
    step_number: int,
    days_elapsed: int = 1,
    benchmark_initial_stock_price: float | None = None,
) -> tuple[PositionState, EquitySnapshot]:
    """
    Update the covered-call position after one simulated market step.
    """
    ticker = simulation_input.ticker.upper().strip()
    shares = previous_position_state.shares
    strike = float(selected_option.strike)
    contract_count = get_contract_count_from_position(previous_position_state)

    new_stock_price = round_money(new_stock_price)

    if new_stock_price is None:
        raise ValueError("New stock price cannot be None.")

    if benchmark_initial_stock_price is None:
        benchmark_initial_stock_price = previous_position_state.stock_price

    new_short_call_mark = estimate_short_call_mark_after_move(
        previous_stock_price=previous_position_state.stock_price,
        new_stock_price=new_stock_price,
        previous_option_mark=previous_position_state.short_call_mark,
        strike=strike,
        delta=selected_option.delta,
        days_elapsed=days_elapsed,
    )

    stock_value = round_money(shares * new_stock_price)
    short_call_market_value = round_money(
        -new_short_call_mark * 100 * contract_count
    )

    cash = round_money(previous_position_state.cash)

    realized_option_pl = round_money(previous_position_state.realized_option_pl)
    unrealized_option_pl = round_money(
        (selected_option.selected_price - new_short_call_mark)
        * 100
        * contract_count
    )

    total_realized_pl = round_money(previous_position_state.total_realized_pl)
    total_equity = round_money(cash + stock_value + short_call_market_value)

    new_dte = None
    if previous_position_state.days_to_expiration is not None:
        new_dte = max(previous_position_state.days_to_expiration - days_elapsed, 0)

    if new_dte is None:
        new_dte = max(selected_option.dte - days_elapsed, 0)

    moneyness = classify_moneyness(
        stock_price=new_stock_price,
        strike=strike,
    )

    assignment_status = classify_assignment_status(
        stock_price=new_stock_price,
        strike=strike,
        dte=new_dte,
    )

    capped_upside = round_money(max(strike - new_stock_price, 0.0) * shares)

    updated_position_state = PositionState(
        session_id=simulation_input.session_id,
        timestamp=new_timestamp,
        ticker=ticker,
        shares=shares,
        stock_price=new_stock_price,
        stock_value=stock_value,
        cash=cash,
        short_call_symbol=previous_position_state.short_call_symbol,
        short_call_quantity=previous_position_state.short_call_quantity,
        short_call_strike=strike,
        short_call_expiration=selected_option.expiration_date,
        short_call_mark=new_short_call_mark,
        short_call_market_value=short_call_market_value,
        realized_option_pl=realized_option_pl,
        unrealized_option_pl=unrealized_option_pl,
        realized_stock_pl=round_money(previous_position_state.realized_stock_pl),
        total_realized_pl=total_realized_pl,
        total_equity=total_equity,
        capped_upside=capped_upside,
        assignment_status=assignment_status,
        days_to_expiration=new_dte,
        moneyness=moneyness,
        note=(
            "Market-step update using simplified stock and short-call mark "
            f"movement for {contract_count} contract(s)."
        ),
    )

    benchmark_buy_hold_equity = calculate_buy_hold_equity(
        starting_account_size=simulation_input.account_size,
        initial_stock_price=benchmark_initial_stock_price,
        new_stock_price=new_stock_price,
        shares=shares,
    )

    missed_upside = calculate_missed_upside(
        stock_price=new_stock_price,
        strike=strike,
        shares=shares,
    )

    equity_snapshot = EquitySnapshot(
        session_id=simulation_input.session_id,
        timestamp=new_timestamp,
        step_number=step_number,
        stock_price=new_stock_price,
        cash=cash,
        stock_value=stock_value,
        short_call_value=short_call_market_value,
        total_equity=total_equity,
        premium_collected_to_date=round_money(
            selected_option.estimated_premium * contract_count
        ),
        realized_option_pl=realized_option_pl,
        unrealized_option_pl=unrealized_option_pl,
        missed_upside=missed_upside,
        benchmark_buy_hold_equity=benchmark_buy_hold_equity,
        benchmark_rule_equity=None,
    )

    return updated_position_state, equity_snapshot


def summarize_equity_snapshot(
    equity_snapshot: EquitySnapshot,
) -> dict[str, object]:
    """
    Convert an equity snapshot to compact printable values.
    """
    return {
        "step_number": equity_snapshot.step_number,
        "stock_price": round_money(equity_snapshot.stock_price),
        "cash": round_money(equity_snapshot.cash),
        "stock_value": round_money(equity_snapshot.stock_value),
        "short_call_value": round_money(equity_snapshot.short_call_value),
        "total_equity": round_money(equity_snapshot.total_equity),
        "premium_collected_to_date": round_money(
            equity_snapshot.premium_collected_to_date
        ),
        "realized_option_pl": round_money(equity_snapshot.realized_option_pl),
        "unrealized_option_pl": round_money(equity_snapshot.unrealized_option_pl),
        "missed_upside": round_money(equity_snapshot.missed_upside),
        "benchmark_buy_hold_equity": round_money(
            equity_snapshot.benchmark_buy_hold_equity
        ),
    }


def summarize_path_position_state(
    position_state: PositionState,
) -> dict[str, object]:
    """
    Convert the updated path position state to compact printable values.
    """
    return {
        "timestamp": position_state.timestamp,
        "ticker": position_state.ticker,
        "shares": position_state.shares,
        "stock_price": round_money(position_state.stock_price),
        "stock_value": round_money(position_state.stock_value),
        "cash": round_money(position_state.cash),
        "short_call_symbol": position_state.short_call_symbol,
        "short_call_quantity": position_state.short_call_quantity,
        "short_call_strike": round_money(position_state.short_call_strike),
        "short_call_mark": round_money(position_state.short_call_mark),
        "short_call_market_value": round_money(position_state.short_call_market_value),
        "realized_option_pl": round_money(position_state.realized_option_pl),
        "unrealized_option_pl": round_money(position_state.unrealized_option_pl),
        "total_equity": round_money(position_state.total_equity),
        "capped_upside": round_money(position_state.capped_upside),
        "assignment_status": position_state.assignment_status,
        "days_to_expiration": position_state.days_to_expiration,
        "moneyness": position_state.moneyness,
        "note": position_state.note,
    }
