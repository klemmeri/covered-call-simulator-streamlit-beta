"""
path_runner.py

Multi-step path runner for the paid Covered Call Simulator.

This module extends the one-day path update into a short simulated path.

It answers:

    What happens to total equity over several market steps after opening
    the covered call?

The path runner produces:
    - updated position states
    - equity snapshots
    - covered-call equity curve
    - buy-and-hold benchmark equity curve
    - final summary metrics

This is still an illustrative engine component. It does not yet use real
historical data or a full option-pricing model.

Accounting note:
    The buy-and-hold benchmark must use the original entry stock price for
    every path step. The original entry stock price is captured from the
    opening_position_state and passed into path_update.py.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from models import (
    EquitySnapshot,
    PositionState,
    SelectedOption,
    SimulationInput,
)
from path_update import update_position_after_market_step


def round_money(value: float | None) -> float | None:
    """
    Round money-like values to two decimal places.
    """
    if value is None:
        return None

    return round(float(value), 2)


def generate_demo_price_path(
    starting_price: float,
    daily_returns: list[float] | None = None,
) -> list[float]:
    """
    Generate a deterministic illustrative price path.
    """
    if starting_price <= 0:
        raise ValueError("Starting price must be greater than zero.")

    if daily_returns is None:
        daily_returns = [
            0.012,
            -0.006,
            0.004,
            0.018,
            -0.010,
            0.006,
            0.009,
        ]

    prices: list[float] = []
    current_price = starting_price

    for daily_return in daily_returns:
        current_price = round_money(current_price * (1.0 + daily_return))
        prices.append(current_price)

    return prices


def run_multi_step_path(
    simulation_input: SimulationInput,
    opening_position_state: PositionState,
    selected_option: SelectedOption,
    path_prices: list[float],
    start_timestamp: datetime,
    days_per_step: int = 1,
) -> tuple[list[PositionState], list[EquitySnapshot]]:
    """
    Run a multi-step covered-call path.
    """
    if not path_prices:
        return [], []

    position_states: list[PositionState] = []
    equity_snapshots: list[EquitySnapshot] = []

    previous_position_state = opening_position_state
    benchmark_initial_stock_price = opening_position_state.stock_price

    for step_number, new_stock_price in enumerate(path_prices, start=1):
        new_timestamp = start_timestamp + timedelta(
            days=step_number * days_per_step
        )

        updated_position_state, equity_snapshot = update_position_after_market_step(
            simulation_input=simulation_input,
            previous_position_state=previous_position_state,
            selected_option=selected_option,
            new_timestamp=new_timestamp,
            new_stock_price=new_stock_price,
            step_number=step_number,
            days_elapsed=days_per_step,
            benchmark_initial_stock_price=benchmark_initial_stock_price,
        )

        position_states.append(updated_position_state)
        equity_snapshots.append(equity_snapshot)

        previous_position_state = updated_position_state

    return position_states, equity_snapshots


def summarize_equity_curve(
    equity_snapshots: list[EquitySnapshot],
) -> list[dict[str, object]]:
    """
    Convert equity snapshots to compact rows for printing or display.
    """
    rows: list[dict[str, object]] = []

    for snapshot in equity_snapshots:
        rows.append(
            {
                "step": snapshot.step_number,
                "stock_price": round_money(snapshot.stock_price),
                "covered_call_equity": round_money(snapshot.total_equity),
                "buy_hold_equity": round_money(snapshot.benchmark_buy_hold_equity),
                "short_call_value": round_money(snapshot.short_call_value),
                "unrealized_option_pl": round_money(snapshot.unrealized_option_pl),
                "missed_upside": round_money(snapshot.missed_upside),
            }
        )

    return rows


def summarize_path_result(
    simulation_input: SimulationInput,
    opening_position_state: PositionState,
    equity_snapshots: list[EquitySnapshot],
) -> dict[str, object]:
    """
    Summarize the multi-step path result.
    """
    if not equity_snapshots:
        return {
            "session_id": simulation_input.session_id,
            "steps": 0,
            "message": "No path steps were run.",
        }

    final_snapshot = equity_snapshots[-1]

    starting_equity = round_money(opening_position_state.total_equity)
    final_covered_call_equity = round_money(final_snapshot.total_equity)
    final_buy_hold_equity = round_money(final_snapshot.benchmark_buy_hold_equity)

    covered_call_pl = round_money(final_covered_call_equity - starting_equity)

    buy_hold_pl = None
    if final_buy_hold_equity is not None:
        buy_hold_pl = round_money(final_buy_hold_equity - simulation_input.account_size)

    benchmark_difference = None
    if final_buy_hold_equity is not None:
        benchmark_difference = round_money(
            final_covered_call_equity - final_buy_hold_equity
        )

    return {
        "session_id": simulation_input.session_id,
        "steps": len(equity_snapshots),
        "starting_equity_after_entry": starting_equity,
        "final_covered_call_equity": final_covered_call_equity,
        "covered_call_pl_after_entry": covered_call_pl,
        "final_buy_hold_equity": final_buy_hold_equity,
        "buy_hold_pl_from_initial_account": buy_hold_pl,
        "covered_call_minus_buy_hold": benchmark_difference,
        "final_stock_price": round_money(final_snapshot.stock_price),
        "final_short_call_value": round_money(final_snapshot.short_call_value),
        "final_unrealized_option_pl": round_money(final_snapshot.unrealized_option_pl),
        "total_missed_upside": round_money(final_snapshot.missed_upside),
    }
