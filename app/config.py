"""
config.py

Configuration settings for the Covered Call Simulator.

The SimulationConfig dataclass stores the assumptions used by each simulation
experiment.

Supported management rules:

    1. hold_to_expiration

    2. close_at_50_percent_profit

    3. close_at_50_percent_profit_then_wait

    4. close_at_50_percent_profit_then_pullback_or_wait

    5. adaptive_close50_wait10_by_regime

       If regime_name is bearish_market or sideways_market:
           behaves like close_at_50_percent_profit

       Otherwise:
           behaves like close_at_50_percent_profit_then_wait with 10 wait days

Transaction-cost model:

    option_commission_per_contract:
        Commission charged per option contract per transaction.

    option_slippage_per_share:
        Slippage charged per option share.

        When selling a call:
            effective sale price = model price - slippage

        When buying back a call:
            effective buyback price = model price + slippage
"""

from dataclasses import dataclass


@dataclass
class SimulationConfig:
    """
    Container for simulation assumptions.
    """

    start_price: float = 100.0
    shares: int = 100

    annual_return: float = 0.08
    annual_volatility: float = 0.25
    risk_free_rate: float = 0.04

    total_days: int = 252
    dte: int = 30
    target_delta: float = 0.30

    n_paths: int = 250
    trading_days_per_year: int = 252

    regime_name: str = "baseline"

    management_rule: str = "hold_to_expiration"

    close_profit_fraction: float = 0.50

    # Used by close_at_50_percent_profit_then_wait.
    wait_days_after_profit_close: int = 3

    # Used by close_at_50_percent_profit_then_pullback_or_wait.
    pullback_fraction_after_profit_close: float = 0.02
    max_wait_days_after_profit_close: int = 10

    # Used by adaptive_close50_wait10_by_regime.
    adaptive_wait_days_after_profit_close: int = 10

    # Transaction-cost assumptions.
    option_commission_per_contract: float = 0.65
    option_slippage_per_share: float = 0.01