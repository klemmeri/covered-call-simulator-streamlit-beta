"""
strategy.py

Covered-call strategy logic for the Covered Call Simulator.

This module selects and prices the short covered call.

Current baseline rule:

    Sell one covered call with a strike chosen to approximate config.target_delta.

Important performance note
--------------------------
Earlier versions searched across many possible strikes. That is slow because the
simulator must do this thousands of times.

This version solves directly for the Black-Scholes strike corresponding to the
target delta.

For a call option:

    delta = N(d1)

So:

    d1 = N^{-1}(target_delta)

and the strike can be solved directly from the Black-Scholes d1 equation.

This is much faster than a grid search.
"""

from pathlib import Path
import sys
import math

from scipy.stats import norm


# ---------------------------------------------------------------------
# Import handling
#
# This allows strategy.py to work whether modules are imported from:
#
#     app/main.py
#
# or from scripts run at the project root.
# ---------------------------------------------------------------------

CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


from black_scholes import call_delta, call_price


def choose_strike_by_delta(
    stock_price: float,
    current_day: int,
    config,
) -> float:
    """
    Choose a call strike corresponding approximately to config.target_delta.

    This uses the Black-Scholes d1 equation directly instead of searching
    over candidate strikes.

    Parameters
    ----------
    stock_price:
        Current stock price.

    current_day:
        Current day in the simulated path.

    config:
        SimulationConfig object.

    Returns
    -------
    float
        Selected call strike.
    """

    expiration_day = min(
        current_day + config.dte,
        config.total_days,
    )

    days_to_expiration = max(
        expiration_day - current_day,
        1,
    )

    time_to_expiration = (
        days_to_expiration / config.trading_days_per_year
    )

    volatility = config.annual_volatility
    risk_free_rate = config.risk_free_rate
    target_delta = config.target_delta

    # Keep target delta inside a numerically safe range.
    target_delta = max(
        0.01,
        min(0.99, target_delta),
    )

    if volatility <= 0 or time_to_expiration <= 0:
        return stock_price

    d1_target = norm.ppf(target_delta)

    strike = stock_price * math.exp(
        (risk_free_rate + 0.5 * volatility ** 2) * time_to_expiration
        - d1_target * volatility * math.sqrt(time_to_expiration)
    )

    return float(strike)


def sell_covered_call(
    stock_price: float,
    current_day: int,
    config,
) -> dict:
    """
    Sell one covered call.

    Parameters
    ----------
    stock_price:
        Current stock price.

    current_day:
        Current day in the simulated path.

    config:
        SimulationConfig object.

    Returns
    -------
    dict
        Dictionary containing:
            strike
            expiration_day
            premium_per_share
            delta
            dte
    """

    expiration_day = min(
        current_day + config.dte,
        config.total_days,
    )

    days_to_expiration = max(
        expiration_day - current_day,
        1,
    )

    time_to_expiration = (
        days_to_expiration / config.trading_days_per_year
    )

    strike = choose_strike_by_delta(
        stock_price=stock_price,
        current_day=current_day,
        config=config,
    )

    premium_per_share = call_price(
        stock_price=stock_price,
        strike=strike,
        time_to_expiration=time_to_expiration,
        risk_free_rate=config.risk_free_rate,
        volatility=config.annual_volatility,
    )

    delta = call_delta(
        stock_price=stock_price,
        strike=strike,
        time_to_expiration=time_to_expiration,
        risk_free_rate=config.risk_free_rate,
        volatility=config.annual_volatility,
    )

    return {
        "strike": strike,
        "expiration_day": expiration_day,
        "premium_per_share": premium_per_share,
        "delta": delta,
        "dte": days_to_expiration,
    }