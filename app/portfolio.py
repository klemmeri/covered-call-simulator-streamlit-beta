"""
portfolio.py

Portfolio accounting logic for the Covered Call Simulator.

Supported management rules:

    1. hold_to_expiration

    2. close_at_50_percent_profit

       Close the short call after reaching the profit target and immediately
       sell the next call.

    3. close_at_50_percent_profit_then_wait

       Close the short call after reaching the profit target, wait a fixed
       number of trading days, then sell the next call.

    4. close_at_50_percent_profit_then_pullback_or_wait

       Close the short call after reaching the profit target, then wait until
       either the stock pulls back by a specified percentage or the maximum
       wait period is reached.

    5. adaptive_close50_wait10_by_regime

       If config.regime_name is bearish_market or sideways_market:
           behaves like close_at_50_percent_profit

       Otherwise:
           behaves like close_at_50_percent_profit_then_wait with
           config.adaptive_wait_days_after_profit_close, normally 10 days.

    6. adaptive_close50_wait10_by_regime_and_cost

       If config.regime_name is bearish_market:
           behaves like close_at_50_percent_profit

       If config.regime_name is sideways_market:
           If option commission >= $1.25 per contract
           or option slippage >= $0.025 per share:
               behaves like hold_to_expiration
           Otherwise:
               behaves like close_at_50_percent_profit

       Otherwise:
           behaves like close_at_50_percent_profit_then_wait with
           config.adaptive_wait_days_after_profit_close, normally 10 days.

    7. adaptive_by_regime_dte_cost

       Simplified DTE-aware adaptive rule.

       If config.regime_name is bearish_market:
           behaves like close_at_50_percent_profit

       If config.regime_name is sideways_market:
           If DTE <= 14:
               behaves like hold_to_expiration

           If DTE >= 21:
               If option commission >= $1.25 per contract
               or option slippage >= $0.025 per share:
                   behaves like hold_to_expiration
               Otherwise:
                   behaves like close_at_50_percent_profit

       If config.regime_name is baseline, bullish_market, high_volatility,
       or low_volatility:
           If DTE < 45:
               behaves like close_at_50_percent_profit_then_wait
           If DTE >= 45:
               behaves like hold_to_expiration

Transaction-cost model:

    Selling a call:
        gross premium = model option price x shares
        sell slippage = option_slippage_per_share x shares
        sell commission = option_commission_per_contract x contracts
        net premium = gross premium - sell slippage - sell commission

    Buying back a call:
        gross buyback = model option price x shares
        buyback slippage = option_slippage_per_share x shares
        buyback commission = option_commission_per_contract x contracts
        total buyback cost = gross buyback + buyback slippage + buyback commission

Notes:
    This version assumes the covered-call position covers all shares.
    contracts = shares / 100.
"""

from dataclasses import dataclass, field
from pathlib import Path
import sys


# ---------------------------------------------------------------------
# Import handling
# ---------------------------------------------------------------------

CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


from black_scholes import call_price


# ---------------------------------------------------------------------
# Cost-aware adaptive thresholds
# ---------------------------------------------------------------------

COST_AWARE_SIDEWAYS_COMMISSION_THRESHOLD = 1.25
COST_AWARE_SIDEWAYS_SLIPPAGE_THRESHOLD = 0.025


# ---------------------------------------------------------------------
# DTE-aware adaptive settings
# ---------------------------------------------------------------------

DTE_AWARE_SIDEWAYS_HOLD_MAX_DTE = 14
DTE_AWARE_LONG_DTE_HOLD_THRESHOLD = 45
DTE_AWARE_DEFAULT_WAIT_DAYS = 10


@dataclass
class PortfolioResult:
    """
    Path-level result from one covered-call simulation path.
    """

    final_covered_call_value: float
    final_buy_and_hold_value: float

    total_premium_collected: float
    total_gross_premium_collected: float

    total_buyback_cost: float
    total_gross_buyback_cost: float

    total_missed_upside: float
    total_transaction_cost: float
    total_commission_cost: float
    total_slippage_cost: float

    net_option_effect: float
    assignments: int
    option_cycles: int
    covered_call_return: float
    buy_and_hold_return: float
    outperformance: float
    cycle_records: list[dict] = field(default_factory=list)


def _normalize_text(value) -> str:
    """
    Normalize strings for rule and regime comparisons.
    """

    return (
        str(value)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .strip("_")
    )


def _get_contract_count(config) -> float:
    """
    Return number of option contracts implied by the share count.

    The simulator prices premium using all shares, so the matching contract
    count is shares / 100.
    """

    shares = float(getattr(config, "shares", 100))
    return max(shares / 100.0, 0.0)


def _get_option_commission_per_contract(config) -> float:
    """
    Return option commission per contract.
    """

    value = getattr(config, "option_commission_per_contract", 0.0)

    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0.0

    return max(value, 0.0)


def _get_option_slippage_per_share(config) -> float:
    """
    Return option slippage per share.
    """

    value = getattr(config, "option_slippage_per_share", 0.0)

    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0.0

    return max(value, 0.0)


def _get_configured_dte(config) -> int:
    """
    Return the configured option DTE.

    The project has used a few possible DTE field names during development.
    This helper checks the likely names and returns the first valid value.

    If no DTE field is found, it falls back to 30.
    """

    dte_field_candidates = [
        "option_dte",
        "option_days_to_expiration",
        "days_to_expiration",
        "dte",
        "call_dte",
        "covered_call_dte",
        "expiration_days",
        "option_expiration_days",
        "option_duration_days",
        "days_per_option_cycle",
        "option_cycle_days",
    ]

    for field_name in dte_field_candidates:
        if hasattr(config, field_name):
            value = getattr(config, field_name)

            try:
                value = int(value)
            except (TypeError, ValueError):
                continue

            if value > 0:
                return value

    return 30


def _sideways_costs_are_high(config) -> bool:
    """
    Return True if transaction costs are high enough that Close50 is no longer
    preferred in sideways_market.

    Threshold was based on the cost_threshold_search.py robustness result:

        commission = $1.25 per contract
        slippage   = $0.025 per share
    """

    commission_per_contract = _get_option_commission_per_contract(config)
    slippage_per_share = _get_option_slippage_per_share(config)

    return (
        commission_per_contract >= COST_AWARE_SIDEWAYS_COMMISSION_THRESHOLD
        or slippage_per_share >= COST_AWARE_SIDEWAYS_SLIPPAGE_THRESHOLD
    )


def _get_effective_management_rule(config) -> str:
    """
    Convert adaptive management rules into the actual behavior to use.

    External adaptive rule names remain:

        adaptive_close50_wait10_by_regime
        adaptive_close50_wait10_by_regime_and_cost
        adaptive_by_regime_dte_cost

    Inside the path simulation, they are converted into one of the real
    behavioral rules:

        hold_to_expiration
        close_at_50_percent_profit
        close_at_50_percent_profit_then_wait
    """

    management_rule = _normalize_text(
        getattr(config, "management_rule", "hold_to_expiration")
    )

    adaptive_rules = {
        "adaptive_close50_wait10_by_regime",
        "adaptive_close50_wait10_by_regime_and_cost",
        "adaptive_by_regime_dte_cost",
    }

    if management_rule not in adaptive_rules:
        return management_rule

    regime_name = _normalize_text(
        getattr(config, "regime_name", "baseline")
    )

    # ------------------------------------------------------------
    # Original adaptive rule
    # ------------------------------------------------------------

    if management_rule == "adaptive_close50_wait10_by_regime":
        immediate_resell_regimes = {
            "bearish_market",
            "sideways_market",
        }

        if regime_name in immediate_resell_regimes:
            return "close_at_50_percent_profit"

        return "close_at_50_percent_profit_then_wait"

    # ------------------------------------------------------------
    # Cost-aware adaptive rule
    # ------------------------------------------------------------

    if management_rule == "adaptive_close50_wait10_by_regime_and_cost":
        if regime_name == "bearish_market":
            return "close_at_50_percent_profit"

        if regime_name == "sideways_market":
            if _sideways_costs_are_high(config):
                return "hold_to_expiration"

            return "close_at_50_percent_profit"

        return "close_at_50_percent_profit_then_wait"

    # ------------------------------------------------------------
    # Simplified DTE-aware, cost-aware adaptive rule
    # ------------------------------------------------------------

    if management_rule == "adaptive_by_regime_dte_cost":
        dte = _get_configured_dte(config)

        if regime_name == "bearish_market":
            return "close_at_50_percent_profit"

        if regime_name == "sideways_market":
            if dte <= DTE_AWARE_SIDEWAYS_HOLD_MAX_DTE:
                return "hold_to_expiration"

            if _sideways_costs_are_high(config):
                return "hold_to_expiration"

            return "close_at_50_percent_profit"

        if regime_name in {
            "baseline",
            "bullish_market",
            "high_volatility",
            "low_volatility",
        }:
            if dte >= DTE_AWARE_LONG_DTE_HOLD_THRESHOLD:
                return "hold_to_expiration"

            return "close_at_50_percent_profit_then_wait"

        # Fallback for unknown regimes.
        if dte >= DTE_AWARE_LONG_DTE_HOLD_THRESHOLD:
            return "hold_to_expiration"

        return "close_at_50_percent_profit_then_wait"

    return management_rule


def _get_option_commission(config) -> float:
    """
    Return option commission for one option transaction.
    """

    contracts = _get_contract_count(config)
    commission_per_contract = _get_option_commission_per_contract(config)

    return contracts * commission_per_contract


def _get_option_slippage(config) -> float:
    """
    Return option slippage cost for one option transaction.
    """

    shares = float(getattr(config, "shares", 100))
    slippage_per_share = _get_option_slippage_per_share(config)

    return shares * slippage_per_share


def _price_short_call_on_day(
    stock_price: float,
    strike: float,
    current_day: int,
    expiration_day: int,
    config,
) -> float:
    """
    Reprice the short call on a given day using Black-Scholes.
    """

    remaining_days = max(
        expiration_day - current_day,
        0,
    )

    time_to_expiration = (
        remaining_days / config.trading_days_per_year
    )

    return call_price(
        stock_price=stock_price,
        strike=strike,
        time_to_expiration=time_to_expiration,
        risk_free_rate=config.risk_free_rate,
        volatility=config.annual_volatility,
    )


def _find_early_close_day(
    price_path,
    start_day: int,
    expiration_day: int,
    strike: float,
    original_premium_per_share: float,
    config,
) -> tuple[int | None, float]:
    """
    Find the first day where the short call can be closed at the profit target.

    For a 50% profit target:

        close when current option value <= 50% of original premium

    The trigger uses the model option value, not transaction costs. Costs are
    applied when the buyback is executed.
    """

    close_threshold = (
        original_premium_per_share * (1.0 - config.close_profit_fraction)
    )

    first_check_day = start_day + 1

    for day in range(first_check_day, expiration_day):
        stock_price = price_path[day]

        current_option_value = _price_short_call_on_day(
            stock_price=stock_price,
            strike=strike,
            current_day=day,
            expiration_day=expiration_day,
            config=config,
        )

        if current_option_value <= close_threshold:
            return day, current_option_value

    return None, 0.0


def _get_wait_days_after_profit_close(config, effective_management_rule: str) -> int:
    """
    Return fixed wait days after profit close.

    For adaptive wait rules, the effective wait rule uses:

        config.adaptive_wait_days_after_profit_close

    normally 10 trading days.
    """

    original_management_rule = _normalize_text(
        getattr(config, "management_rule", "")
    )

    adaptive_wait_rules = {
        "adaptive_close50_wait10_by_regime",
        "adaptive_close50_wait10_by_regime_and_cost",
        "adaptive_by_regime_dte_cost",
    }

    if (
        original_management_rule in adaptive_wait_rules
        and effective_management_rule == "close_at_50_percent_profit_then_wait"
    ):
        wait_days = getattr(
            config,
            "adaptive_wait_days_after_profit_close",
            DTE_AWARE_DEFAULT_WAIT_DAYS,
        )
    else:
        wait_days = getattr(config, "wait_days_after_profit_close", 0)

    try:
        wait_days = int(wait_days)
    except (TypeError, ValueError):
        wait_days = 0

    return max(wait_days, 0)


def _get_max_wait_days_after_profit_close(config) -> int:
    """
    Return maximum wait days for the pullback-or-wait rule.
    """

    wait_days = getattr(config, "max_wait_days_after_profit_close", 10)

    try:
        wait_days = int(wait_days)
    except (TypeError, ValueError):
        wait_days = 10

    return max(wait_days, 0)


def _get_pullback_fraction_after_profit_close(config) -> float:
    """
    Return pullback fraction for the pullback-or-wait rule.
    """

    pullback_fraction = getattr(
        config,
        "pullback_fraction_after_profit_close",
        0.02,
    )

    try:
        pullback_fraction = float(pullback_fraction)
    except (TypeError, ValueError):
        pullback_fraction = 0.02

    return max(pullback_fraction, 0.0)


def _is_early_close_rule(effective_management_rule: str) -> bool:
    """
    Return True if the effective management rule uses the 50% profit close trigger.
    """

    return effective_management_rule in {
        "close_at_50_percent_profit",
        "close_at_50_percent_profit_then_wait",
        "close_at_50_percent_profit_then_pullback_or_wait",
    }


def _find_next_start_day_after_pullback_or_wait(
    price_path,
    close_day: int,
    config,
) -> tuple[int, int, bool]:
    """
    Find the next day to sell a call after closing at the profit target.

    The next call is sold when either:

        1. price pulls back by the configured pullback fraction from the
           close-day stock price, or
        2. the configured maximum wait period is reached.

    Returns
    -------
    tuple[int, int, bool]
        next_start_day:
            Day to sell the next call.

        actual_wait_days:
            Number of trading days waited.

        pullback_triggered:
            True if the pullback condition triggered before the max wait.
    """

    close_price = price_path[close_day]

    pullback_fraction = _get_pullback_fraction_after_profit_close(config)
    max_wait_days = _get_max_wait_days_after_profit_close(config)

    pullback_trigger_price = close_price * (1.0 - pullback_fraction)

    latest_day = min(
        close_day + max_wait_days,
        config.total_days,
        len(price_path) - 1,
    )

    first_check_day = min(close_day + 1, len(price_path) - 1)

    for day in range(first_check_day, latest_day + 1):
        if price_path[day] <= pullback_trigger_price:
            return day, day - close_day, True

    return latest_day, latest_day - close_day, False


def run_covered_call_path(
    price_path,
    config,
    sell_call_function,
    path_number: int | None = None,
) -> PortfolioResult:
    """
    Run one covered-call simulation path.
    """

    shares = config.shares
    initial_stock_price = price_path[0]
    initial_value = shares * initial_stock_price

    cash = 0.0

    total_premium_collected = 0.0
    total_gross_premium_collected = 0.0

    total_buyback_cost = 0.0
    total_gross_buyback_cost = 0.0

    total_missed_upside = 0.0

    total_transaction_cost = 0.0
    total_commission_cost = 0.0
    total_slippage_cost = 0.0

    assignments = 0
    option_cycles = 0

    cycle_records = []

    current_day = 0

    original_management_rule = _normalize_text(
        getattr(config, "management_rule", "hold_to_expiration")
    )

    effective_management_rule = _get_effective_management_rule(config)

    while current_day < config.total_days:
        start_day = current_day

        if start_day >= len(price_path):
            break

        stock_price = price_path[start_day]

        call = sell_call_function(
            stock_price=stock_price,
            current_day=start_day,
            config=config,
        )

        option_cycles += 1
        cycle_number = option_cycles

        strike = call["strike"]
        expiration_day = min(call["expiration_day"], config.total_days)

        if expiration_day >= len(price_path):
            expiration_day = len(price_path) - 1

        original_premium_per_share = call["premium_per_share"]

        gross_premium_collected = original_premium_per_share * shares

        sell_commission = _get_option_commission(config)
        sell_slippage = _get_option_slippage(config)
        sell_transaction_cost = sell_commission + sell_slippage

        net_premium_collected = max(
            gross_premium_collected - sell_transaction_cost,
            0.0,
        )

        cash += net_premium_collected

        total_premium_collected += net_premium_collected
        total_gross_premium_collected += gross_premium_collected

        total_transaction_cost += sell_transaction_cost
        total_commission_cost += sell_commission
        total_slippage_cost += sell_slippage

        assigned = False
        missed_upside = 0.0

        gross_buyback_cost = 0.0
        buyback_cost = 0.0
        buyback_commission = 0.0
        buyback_slippage = 0.0
        buyback_transaction_cost = 0.0

        realized_option_profit = net_premium_collected

        exit_reason = "expiration"
        exit_day = expiration_day
        exit_price = price_path[expiration_day]

        next_start_day = expiration_day
        next_start_price = price_path[next_start_day]

        wait_days_after_close = 0
        pullback_triggered = False

        # ------------------------------------------------------------
        # Early-close rules
        # ------------------------------------------------------------

        if _is_early_close_rule(effective_management_rule):
            close_day, close_price_per_share = _find_early_close_day(
                price_path=price_path,
                start_day=start_day,
                expiration_day=expiration_day,
                strike=strike,
                original_premium_per_share=original_premium_per_share,
                config=config,
            )

            if close_day is not None:
                gross_buyback_cost = close_price_per_share * shares

                buyback_commission = _get_option_commission(config)
                buyback_slippage = _get_option_slippage(config)
                buyback_transaction_cost = buyback_commission + buyback_slippage

                buyback_cost = gross_buyback_cost + buyback_transaction_cost

                cash -= buyback_cost

                total_buyback_cost += buyback_cost
                total_gross_buyback_cost += gross_buyback_cost

                total_transaction_cost += buyback_transaction_cost
                total_commission_cost += buyback_commission
                total_slippage_cost += buyback_slippage

                realized_option_profit = net_premium_collected - buyback_cost

                exit_reason = "closed_at_profit_target"
                exit_day = close_day
                exit_price = price_path[close_day]

                assigned = False
                missed_upside = 0.0

                if effective_management_rule == "close_at_50_percent_profit":
                    next_start_day = exit_day
                    wait_days_after_close = 0
                    pullback_triggered = False

                elif effective_management_rule == "close_at_50_percent_profit_then_wait":
                    wait_days_after_close = _get_wait_days_after_profit_close(
                        config=config,
                        effective_management_rule=effective_management_rule,
                    )
                    next_start_day = min(
                        exit_day + wait_days_after_close,
                        config.total_days,
                        len(price_path) - 1,
                    )
                    pullback_triggered = False

                elif effective_management_rule == "close_at_50_percent_profit_then_pullback_or_wait":
                    (
                        next_start_day,
                        wait_days_after_close,
                        pullback_triggered,
                    ) = _find_next_start_day_after_pullback_or_wait(
                        price_path=price_path,
                        close_day=exit_day,
                        config=config,
                    )

                next_start_price = price_path[next_start_day]

                cycle_net_option_effect = (
                    net_premium_collected - buyback_cost - missed_upside
                )

                cycle_records.append(
                    {
                        "path_number": path_number,
                        "cycle_number": cycle_number,
                        "management_rule": original_management_rule,
                        "effective_management_rule": effective_management_rule,
                        "regime_name": getattr(config, "regime_name", "unknown"),
                        "start_day": start_day,
                        "exit_day": exit_day,
                        "next_start_day": next_start_day,
                        "expiration_day": expiration_day,
                        "start_price": stock_price,
                        "exit_price": exit_price,
                        "next_start_price": next_start_price,
                        "expiration_price": price_path[expiration_day],
                        "strike": strike,
                        "premium_collected": net_premium_collected,
                        "gross_premium_collected": gross_premium_collected,
                        "buyback_cost": buyback_cost,
                        "gross_buyback_cost": gross_buyback_cost,
                        "sell_commission": sell_commission,
                        "sell_slippage": sell_slippage,
                        "sell_transaction_cost": sell_transaction_cost,
                        "buyback_commission": buyback_commission,
                        "buyback_slippage": buyback_slippage,
                        "buyback_transaction_cost": buyback_transaction_cost,
                        "total_cycle_transaction_cost": (
                            sell_transaction_cost + buyback_transaction_cost
                        ),
                        "realized_option_profit": realized_option_profit,
                        "missed_upside": missed_upside,
                        "net_option_effect": cycle_net_option_effect,
                        "assigned": int(assigned),
                        "wait_days_after_close": wait_days_after_close,
                        "pullback_triggered": int(pullback_triggered),
                        "exit_reason": exit_reason,
                    }
                )

                current_day = next_start_day

                if current_day >= config.total_days:
                    break

                continue

        # ------------------------------------------------------------
        # Hold-to-expiration behavior
        # ------------------------------------------------------------

        expiration_price = price_path[expiration_day]
        exit_day = expiration_day
        exit_price = expiration_price
        exit_reason = "expiration"

        next_start_day = expiration_day
        next_start_price = price_path[next_start_day]

        if expiration_price > strike:
            assigned = True
            assignments += 1

            missed_upside = (expiration_price - strike) * shares
            total_missed_upside += missed_upside

            cash += strike * shares
            cash -= expiration_price * shares

        realized_option_profit = net_premium_collected - buyback_cost

        cycle_net_option_effect = (
            net_premium_collected - buyback_cost - missed_upside
        )

        cycle_records.append(
            {
                "path_number": path_number,
                "cycle_number": cycle_number,
                "management_rule": original_management_rule,
                "effective_management_rule": effective_management_rule,
                "regime_name": getattr(config, "regime_name", "unknown"),
                "start_day": start_day,
                "exit_day": exit_day,
                "next_start_day": next_start_day,
                "expiration_day": expiration_day,
                "start_price": stock_price,
                "exit_price": exit_price,
                "next_start_price": next_start_price,
                "expiration_price": expiration_price,
                "strike": strike,
                "premium_collected": net_premium_collected,
                "gross_premium_collected": gross_premium_collected,
                "buyback_cost": buyback_cost,
                "gross_buyback_cost": gross_buyback_cost,
                "sell_commission": sell_commission,
                "sell_slippage": sell_slippage,
                "sell_transaction_cost": sell_transaction_cost,
                "buyback_commission": buyback_commission,
                "buyback_slippage": buyback_slippage,
                "buyback_transaction_cost": buyback_transaction_cost,
                "total_cycle_transaction_cost": (
                    sell_transaction_cost + buyback_transaction_cost
                ),
                "realized_option_profit": realized_option_profit,
                "missed_upside": missed_upside,
                "net_option_effect": cycle_net_option_effect,
                "assigned": int(assigned),
                "wait_days_after_close": wait_days_after_close,
                "pullback_triggered": int(pullback_triggered),
                "exit_reason": exit_reason,
            }
        )

        current_day = expiration_day

        if current_day >= config.total_days:
            break

    final_stock_price = price_path[-1]

    final_covered_call_value = cash + shares * final_stock_price
    final_buy_and_hold_value = shares * final_stock_price

    covered_call_return = (
        final_covered_call_value - initial_value
    ) / initial_value

    buy_and_hold_return = (
        final_buy_and_hold_value - initial_value
    ) / initial_value

    outperformance = covered_call_return - buy_and_hold_return

    net_option_effect = (
        total_premium_collected - total_buyback_cost - total_missed_upside
    )

    return PortfolioResult(
        final_covered_call_value=final_covered_call_value,
        final_buy_and_hold_value=final_buy_and_hold_value,
        total_premium_collected=total_premium_collected,
        total_gross_premium_collected=total_gross_premium_collected,
        total_buyback_cost=total_buyback_cost,
        total_gross_buyback_cost=total_gross_buyback_cost,
        total_missed_upside=total_missed_upside,
        total_transaction_cost=total_transaction_cost,
        total_commission_cost=total_commission_cost,
        total_slippage_cost=total_slippage_cost,
        net_option_effect=net_option_effect,
        assignments=assignments,
        option_cycles=option_cycles,
        covered_call_return=covered_call_return,
        buy_and_hold_return=buy_and_hold_return,
        outperformance=outperformance,
        cycle_records=cycle_records,
    )