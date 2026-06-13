"""
trade_execution.py

Simulated trade-execution logic for the paid Covered Call Simulator.

This module creates the first simulated covered-call position.

It now supports a configurable contract count:

    desired_contracts = 1, 2, 3, ...

For N contracts, the simulated opening position uses:

    shares = 100 * N
    short_call_quantity = -N
    premium = option premium * N
    transaction cost = per-contract cost * N

Important accounting rule:
    Premium collected is not treated as immediate profit.

When the call is sold:
    - cash increases by the option credit,
    - but the short call also becomes a liability,
    - so total equity does not jump by the full premium.
"""

from __future__ import annotations

from datetime import datetime

from models import (
    PositionState,
    SelectedOption,
    SimulationInput,
    TickerSnapshot,
    TradeEvent,
)


def build_option_symbol(
    ticker: str,
    expiration_date: datetime,
    option_type: str,
    strike: float,
) -> str:
    """
    Build a readable illustrative option symbol.
    """
    option_type_code = option_type.upper()[0]
    expiration_text = expiration_date.strftime("%Y%m%d")

    if float(strike).is_integer():
        strike_text = str(int(strike))
    else:
        strike_text = f"{strike:.2f}"

    return f"{ticker.upper()}_{expiration_text}_{option_type_code}_{strike_text}"


def classify_position_moneyness(
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
    Provide a simple assignment-status label for the opening position.
    """
    if stock_price >= strike:
        if dte <= 5:
            return "near_expiration_itm"
        return "itm_monitor"

    distance_percent = (strike - stock_price) / stock_price

    if distance_percent <= 0.01:
        return "near_strike_monitor"

    return "not_under_pressure"


def normalize_contract_count(contract_count: int) -> int:
    """
    Validate and normalize contract count.
    """
    contract_count = int(contract_count)

    if contract_count < 1:
        raise ValueError("Contract count must be at least 1.")

    return contract_count


def create_initial_covered_call_trade_events(
    simulation_input: SimulationInput,
    ticker_snapshot: TickerSnapshot,
    selected_option: SelectedOption,
    contract_multiplier: int = 100,
    contract_count: int = 1,
) -> list[TradeEvent]:
    """
    Create the initial stock and covered-call trade events.
    """
    if ticker_snapshot.price is None:
        raise ValueError("Ticker price is required to create trade events.")

    contract_count = normalize_contract_count(contract_count)

    ticker = simulation_input.ticker.upper().strip()
    stock_price = float(ticker_snapshot.price)
    timestamp = selected_option.selection_timestamp
    shares = contract_multiplier * contract_count
    stock_value = stock_price * shares

    total_option_premium = selected_option.estimated_premium * contract_count
    total_transaction_cost = (
        selected_option.estimated_transaction_cost * contract_count
    )
    total_net_credit = selected_option.estimated_net_credit * contract_count

    option_symbol = build_option_symbol(
        ticker=ticker,
        expiration_date=selected_option.expiration_date,
        option_type="call",
        strike=selected_option.strike,
    )

    stock_event = TradeEvent(
        event_id=f"{simulation_input.session_id}_EVENT_001",
        session_id=simulation_input.session_id,
        timestamp=timestamp,
        event_type="buy_stock_for_covered_call",
        ticker=ticker,
        stock_price=stock_price,
        shares_delta=shares,
        cash_delta=-stock_value,
        transaction_cost=0.0,
        event_note=(
            f"Simulated allocation of {shares} shares so "
            f"{contract_count} covered call contract(s) are fully covered."
        ),
        user_decision=f"Buy or allocate {shares} shares",
        rule_trigger=None,
    )

    option_event = TradeEvent(
        event_id=f"{simulation_input.session_id}_EVENT_002",
        session_id=simulation_input.session_id,
        timestamp=timestamp,
        event_type="sell_covered_call",
        ticker=ticker,
        stock_price=stock_price,
        shares_delta=0,
        cash_delta=total_net_credit,
        option_symbol=option_symbol,
        option_quantity_delta=-contract_count,
        option_price=selected_option.selected_price,
        option_cash_delta=total_option_premium,
        transaction_cost=total_transaction_cost,
        realized_option_pl=-total_transaction_cost,
        realized_stock_pl=0.0,
        event_note=(
            f"Sold {contract_count} simulated covered call contract(s). "
            "Cash increases by the net credit, but the short call is also "
            "recorded as a liability."
        ),
        user_decision=f"Sell {contract_count} covered call contract(s)",
        rule_trigger=simulation_input.strike_selection_method,
    )

    return [stock_event, option_event]


def build_opening_position_state(
    simulation_input: SimulationInput,
    ticker_snapshot: TickerSnapshot,
    selected_option: SelectedOption,
    contract_multiplier: int = 100,
    contract_count: int = 1,
) -> PositionState:
    """
    Build the position state immediately after opening the covered call.
    """
    if ticker_snapshot.price is None:
        raise ValueError("Ticker price is required to build position state.")

    contract_count = normalize_contract_count(contract_count)

    ticker = simulation_input.ticker.upper().strip()
    timestamp = selected_option.selection_timestamp
    stock_price = float(ticker_snapshot.price)

    shares = contract_multiplier * contract_count
    stock_value = shares * stock_price

    total_net_credit = selected_option.estimated_net_credit * contract_count
    total_transaction_cost = (
        selected_option.estimated_transaction_cost * contract_count
    )

    option_symbol = build_option_symbol(
        ticker=ticker,
        expiration_date=selected_option.expiration_date,
        option_type="call",
        strike=selected_option.strike,
    )

    short_call_market_value = (
        -selected_option.selected_price * contract_multiplier * contract_count
    )

    cash = (
        simulation_input.account_size
        - stock_value
        + total_net_credit
    )

    total_equity = cash + stock_value + short_call_market_value

    moneyness = classify_position_moneyness(
        stock_price=stock_price,
        strike=selected_option.strike,
    )

    assignment_status = classify_assignment_status(
        stock_price=stock_price,
        strike=selected_option.strike,
        dte=selected_option.dte,
    )

    capped_upside = max(selected_option.strike - stock_price, 0.0) * shares

    return PositionState(
        session_id=simulation_input.session_id,
        timestamp=timestamp,
        ticker=ticker,
        shares=shares,
        stock_price=stock_price,
        stock_value=stock_value,
        cash=cash,
        short_call_symbol=option_symbol,
        short_call_quantity=-contract_count,
        short_call_strike=selected_option.strike,
        short_call_expiration=selected_option.expiration_date,
        short_call_mark=selected_option.selected_price,
        short_call_market_value=short_call_market_value,
        realized_option_pl=-total_transaction_cost,
        unrealized_option_pl=0.0,
        realized_stock_pl=0.0,
        total_realized_pl=-total_transaction_cost,
        total_equity=total_equity,
        capped_upside=capped_upside,
        assignment_status=assignment_status,
        days_to_expiration=selected_option.dte,
        moneyness=moneyness,
        note=(
            f"Opening covered-call position with {contract_count} contract(s). "
            "Premium credit is offset by the short-call liability at entry."
        ),
    )


def simulate_initial_covered_call_placement(
    simulation_input: SimulationInput,
    ticker_snapshot: TickerSnapshot,
    selected_option: SelectedOption,
    contract_multiplier: int = 100,
    contract_count: int = 1,
) -> tuple[list[TradeEvent], PositionState]:
    """
    Simulate initial placement of one or more covered calls.
    """
    trade_events = create_initial_covered_call_trade_events(
        simulation_input=simulation_input,
        ticker_snapshot=ticker_snapshot,
        selected_option=selected_option,
        contract_multiplier=contract_multiplier,
        contract_count=contract_count,
    )

    position_state = build_opening_position_state(
        simulation_input=simulation_input,
        ticker_snapshot=ticker_snapshot,
        selected_option=selected_option,
        contract_multiplier=contract_multiplier,
        contract_count=contract_count,
    )

    return trade_events, position_state


def summarize_trade_events(
    trade_events: list[TradeEvent],
) -> list[dict[str, object]]:
    """
    Convert trade events to compact printable dictionaries.
    """
    rows: list[dict[str, object]] = []

    for event in trade_events:
        rows.append(
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "ticker": event.ticker,
                "stock_price": event.stock_price,
                "shares_delta": event.shares_delta,
                "cash_delta": event.cash_delta,
                "option_symbol": event.option_symbol,
                "option_quantity_delta": event.option_quantity_delta,
                "option_price": event.option_price,
                "option_cash_delta": event.option_cash_delta,
                "transaction_cost": event.transaction_cost,
                "realized_option_pl": event.realized_option_pl,
                "event_note": event.event_note,
            }
        )

    return rows


def summarize_position_state(
    position_state: PositionState,
) -> dict[str, object]:
    """
    Convert the opening position state to compact printable values.
    """
    return {
        "ticker": position_state.ticker,
        "shares": position_state.shares,
        "stock_price": position_state.stock_price,
        "stock_value": position_state.stock_value,
        "cash": position_state.cash,
        "short_call_symbol": position_state.short_call_symbol,
        "short_call_quantity": position_state.short_call_quantity,
        "short_call_strike": position_state.short_call_strike,
        "short_call_mark": position_state.short_call_mark,
        "short_call_market_value": position_state.short_call_market_value,
        "realized_option_pl": position_state.realized_option_pl,
        "total_equity": position_state.total_equity,
        "capped_upside": position_state.capped_upside,
        "assignment_status": position_state.assignment_status,
        "moneyness": position_state.moneyness,
        "note": position_state.note,
    }
