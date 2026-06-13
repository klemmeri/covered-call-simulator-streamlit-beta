"""
option_candidates.py

Option-candidate generation and selection logic for the paid Covered Call
Simulator.

This first version uses deterministic illustrative option candidates. It does
not connect to a live option chain.

Purpose:
    Move the paid engine from "Can the user afford one covered-call contract?"
    to "Which simulated covered call could the user select?"
"""

from __future__ import annotations

from datetime import datetime, timedelta

from models import OptionCandidate, SimulationInput, TickerSnapshot


def calculate_mid_price(
    bid: float | None,
    ask: float | None,
) -> float | None:
    """
    Calculate the midpoint between bid and ask.

    Parameters
    ----------
    bid:
        Option bid price.

    ask:
        Option ask price.

    Returns
    -------
    float | None
        Midpoint price, or None if bid/ask are unavailable.
    """
    if bid is None or ask is None:
        return None

    return round((bid + ask) / 2.0, 2)


def calculate_spread_width(
    bid: float | None,
    ask: float | None,
) -> float | None:
    """
    Calculate bid/ask spread width.
    """
    if bid is None or ask is None:
        return None

    return round(max(ask - bid, 0.0), 2)


def calculate_spread_percent(
    bid: float | None,
    ask: float | None,
    mid: float | None,
) -> float | None:
    """
    Calculate spread as a percentage of midpoint.
    """
    if bid is None or ask is None or mid is None or mid <= 0:
        return None

    spread_width = max(ask - bid, 0.0)
    return spread_width / mid


def classify_moneyness(
    stock_price: float,
    strike: float,
) -> str:
    """
    Classify call-option moneyness relative to the stock price.
    """
    if strike < stock_price:
        return "ITM"

    if abs(strike - stock_price) <= stock_price * 0.005:
        return "ATM"

    return "OTM"


def classify_liquidity(
    volume: int | None,
    open_interest: int | None,
    spread_percent: float | None,
) -> str:
    """
    Assign a simple illustrative liquidity score.
    """
    if volume is None or open_interest is None or spread_percent is None:
        return "Unknown"

    if volume >= 1000 and open_interest >= 5000 and spread_percent <= 0.10:
        return "Good"

    if volume >= 250 and open_interest >= 1000 and spread_percent <= 0.20:
        return "Acceptable"

    return "Thin"


def build_demo_option_candidates(
    simulation_input: SimulationInput,
    ticker_snapshot: TickerSnapshot,
) -> list[OptionCandidate]:
    """
    Build deterministic illustrative covered-call candidates.

    Parameters
    ----------
    simulation_input:
        User simulation assumptions.

    ticker_snapshot:
        Underlying price snapshot.

    Returns
    -------
    list[OptionCandidate]
        Demo call candidates.
    """
    if ticker_snapshot.price is None:
        return []

    now = ticker_snapshot.timestamp
    ticker = simulation_input.ticker.upper().strip()
    stock_price = float(ticker_snapshot.price)

    # These offsets are illustrative. Later versions should use real option-chain
    # strikes and Greeks.
    raw_candidates = [
        {
            "dte": 30,
            "strike_offset": 0.025,
            "bid": 7.10,
            "ask": 7.35,
            "delta": 0.43,
            "volume": 2600,
            "open_interest": 18500,
            "iv": 0.185,
        },
        {
            "dte": 30,
            "strike_offset": 0.050,
            "bid": 4.45,
            "ask": 4.62,
            "delta": 0.31,
            "volume": 5200,
            "open_interest": 31200,
            "iv": 0.180,
        },
        {
            "dte": 30,
            "strike_offset": 0.075,
            "bid": 2.55,
            "ask": 2.72,
            "delta": 0.22,
            "volume": 3400,
            "open_interest": 22800,
            "iv": 0.176,
        },
        {
            "dte": 45,
            "strike_offset": 0.050,
            "bid": 6.10,
            "ask": 6.36,
            "delta": 0.34,
            "volume": 1800,
            "open_interest": 14400,
            "iv": 0.188,
        },
        {
            "dte": 45,
            "strike_offset": 0.075,
            "bid": 3.95,
            "ask": 4.16,
            "delta": 0.25,
            "volume": 1100,
            "open_interest": 9800,
            "iv": 0.184,
        },
    ]

    candidates: list[OptionCandidate] = []

    for index, item in enumerate(raw_candidates, start=1):
        strike = round(stock_price * (1.0 + item["strike_offset"]))

        bid = float(item["bid"])
        ask = float(item["ask"])
        mid = calculate_mid_price(bid=bid, ask=ask)
        spread_width = calculate_spread_width(bid=bid, ask=ask)
        spread_percent = calculate_spread_percent(bid=bid, ask=ask, mid=mid)

        liquidity_score = classify_liquidity(
            volume=int(item["volume"]),
            open_interest=int(item["open_interest"]),
            spread_percent=spread_percent,
        )

        moneyness = classify_moneyness(
            stock_price=stock_price,
            strike=float(strike),
        )

        dte = int(item["dte"])
        expiration_date = now + timedelta(days=dte)

        candidate = OptionCandidate(
            candidate_id=f"{ticker}_CALL_CANDIDATE_{index:03d}",
            ticker=ticker,
            expiration_date=expiration_date,
            dte=dte,
            strike=float(strike),
            option_type="call",
            bid=bid,
            ask=ask,
            mid=mid,
            last=mid,
            volume=int(item["volume"]),
            open_interest=int(item["open_interest"]),
            implied_volatility=float(item["iv"]),
            delta=float(item["delta"]),
            gamma=None,
            theta=None,
            vega=None,
            spread_width=spread_width,
            spread_percent=spread_percent,
            moneyness=moneyness,
            liquidity_score=liquidity_score,
            is_candidate=True,
            candidate_reason="Illustrative demo candidate.",
        )

        candidates.append(candidate)

    return candidates


def select_candidate_by_method(
    candidates: list[OptionCandidate],
    simulation_input: SimulationInput,
) -> OptionCandidate | None:
    """
    Select one option candidate using the requested selection method.

    Parameters
    ----------
    candidates:
        Available call candidates.

    simulation_input:
        User assumptions, including target delta and strike-selection method.

    Returns
    -------
    OptionCandidate | None
        Selected candidate or None if no candidate exists.
    """
    if not candidates:
        return None

    method = simulation_input.strike_selection_method.strip().lower()
    target_delta = simulation_input.target_delta

    liquid_candidates = [
        candidate
        for candidate in candidates
        if candidate.is_candidate and candidate.liquidity_score in {"Good", "Acceptable"}
    ]

    usable_candidates = liquid_candidates if liquid_candidates else candidates

    if method == "closest to target delta":
        return min(
            usable_candidates,
            key=lambda candidate: abs((candidate.delta or 0.0) - target_delta),
        )

    if method == "highest annualized premium subject to delta limit":
        eligible = [
            candidate
            for candidate in usable_candidates
            if candidate.delta is not None and candidate.delta <= target_delta
        ]

        if not eligible:
            eligible = usable_candidates

        return max(
            eligible,
            key=lambda candidate: (candidate.mid or 0.0) / max(candidate.dte, 1),
        )

    if method == "liquidity-filtered best match":
        return min(
            usable_candidates,
            key=lambda candidate: (
                0 if candidate.liquidity_score == "Good" else 1,
                abs((candidate.delta or 0.0) - target_delta),
            ),
        )

    # Default fallback.
    return min(
        usable_candidates,
        key=lambda candidate: abs((candidate.delta or 0.0) - target_delta),
    )


def summarize_option_candidates(
    candidates: list[OptionCandidate],
) -> list[dict[str, object]]:
    """
    Convert option candidates to compact dictionaries for printing or display.
    """
    rows: list[dict[str, object]] = []

    for candidate in candidates:
        rows.append(
            {
                "candidate_id": candidate.candidate_id,
                "dte": candidate.dte,
                "strike": candidate.strike,
                "bid": candidate.bid,
                "ask": candidate.ask,
                "mid": candidate.mid,
                "delta": candidate.delta,
                "spread_percent": candidate.spread_percent,
                "moneyness": candidate.moneyness,
                "liquidity_score": candidate.liquidity_score,
            }
        )

    return rows
