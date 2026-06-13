"""
option_premium_model.py

Phase 2B option-premium model scaffold for the paid covered-call simulator.

This module adds a more realistic, but still self-contained, option premium
estimator based on a Black-Scholes-style European call model. It is intended
as a bridge between the simple Phase 2 payoff scaffold and a future production
model that may use live option-chain data.

Important:
- This is still a scaffold, not final production pricing.
- It does not require scipy, numpy, or external market data.
- It intentionally uses simple implied-volatility assumptions by scenario.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import erf, exp, log, sqrt
from pathlib import Path
from typing import Any

import csv


@dataclass(frozen=True)
class PremiumScenarioAssumption:
    """Scenario-level assumption inputs for option premium estimation."""

    scenario_name: str
    display_name: str
    modeled_total_return_percent: float
    realized_volatility_label: str
    implied_volatility_bias: str
    skew_bias: str
    path_shape: str
    covered_call_profile: str
    interpretation: str


@dataclass(frozen=True)
class OptionPremiumInputs:
    """Inputs required for simplified Black-Scholes call pricing."""

    underlying_price: float
    strike_price: float
    days_to_expiration: int
    implied_volatility: float
    risk_free_rate: float = 0.045
    dividend_yield: float = 0.0


@dataclass(frozen=True)
class OptionPremiumResult:
    """Output row for the premium model scaffold."""

    scenario_name: str
    display_name: str
    underlying_price: float
    target_delta: float
    estimated_strike: float
    days_to_expiration: int
    implied_volatility: float
    risk_free_rate: float
    dividend_yield: float
    estimated_call_premium: float
    estimated_call_delta: float
    moneyness_percent: float
    pricing_note: str


def normal_cdf(x: float) -> float:
    """Standard normal cumulative distribution function without scipy."""

    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def _time_to_expiration_years(days_to_expiration: int) -> float:
    return max(float(days_to_expiration), 1.0) / 365.0


def black_scholes_call_price(inputs: OptionPremiumInputs) -> float:
    """Return a simplified European call price using Black-Scholes."""

    s = float(inputs.underlying_price)
    k = float(inputs.strike_price)
    t = _time_to_expiration_years(inputs.days_to_expiration)
    sigma = max(float(inputs.implied_volatility), 0.0001)
    r = float(inputs.risk_free_rate)
    q = float(inputs.dividend_yield)

    if s <= 0 or k <= 0:
        return 0.0

    d1 = (log(s / k) + (r - q + 0.5 * sigma * sigma) * t) / (sigma * sqrt(t))
    d2 = d1 - sigma * sqrt(t)

    call = s * exp(-q * t) * normal_cdf(d1) - k * exp(-r * t) * normal_cdf(d2)
    return max(call, 0.0)


def black_scholes_call_delta(inputs: OptionPremiumInputs) -> float:
    """Return the simplified Black-Scholes call delta."""

    s = float(inputs.underlying_price)
    k = float(inputs.strike_price)
    t = _time_to_expiration_years(inputs.days_to_expiration)
    sigma = max(float(inputs.implied_volatility), 0.0001)
    r = float(inputs.risk_free_rate)
    q = float(inputs.dividend_yield)

    if s <= 0 or k <= 0:
        return 0.0

    d1 = (log(s / k) + (r - q + 0.5 * sigma * sigma) * t) / (sigma * sqrt(t))
    return exp(-q * t) * normal_cdf(d1)


def estimate_implied_volatility(realized_volatility_label: str, implied_volatility_bias: str) -> float:
    """Map scenario labels to a simple implied-volatility estimate.

    Returns volatility as a decimal, for example 0.18 for 18 percent.
    """

    vol_label = str(realized_volatility_label or "normal").strip().lower()
    iv_bias = str(implied_volatility_bias or "neutral").strip().lower()

    base_by_realized = {
        "very_low": 0.11,
        "low": 0.13,
        "normal": 0.17,
        "moderate": 0.20,
        "high": 0.26,
        "very_high": 0.34,
    }

    base = base_by_realized.get(vol_label, 0.17)

    bias_adjustment = {
        "compressed": -0.025,
        "low": -0.015,
        "neutral": 0.0,
        "firm": 0.015,
        "elevated": 0.035,
        "spiking": 0.065,
    }.get(iv_bias, 0.0)

    return min(max(base + bias_adjustment, 0.06), 0.60)


def apply_skew_to_otm_call_iv(base_iv: float, skew_bias: str, target_delta: float) -> float:
    """Apply a simple call-wing skew adjustment.

    This is intentionally simplified. In a future production version, skew
    should come from option-chain data or a calibrated surface.
    """

    skew = str(skew_bias or "neutral").strip().lower()
    delta = float(target_delta)

    adjustment = 0.0
    if skew in {"call_bid", "upside_call_bid", "call_wing_bid"}:
        adjustment = 0.015 if delta <= 0.35 else 0.008
    elif skew in {"put_bid", "downside_put_bid", "defensive"}:
        adjustment = -0.005 if delta <= 0.35 else 0.0
    elif skew in {"flat", "neutral"}:
        adjustment = 0.0

    return min(max(float(base_iv) + adjustment, 0.06), 0.75)


def estimate_strike_for_target_delta(
    underlying_price: float,
    target_delta: float,
    days_to_expiration: int,
    implied_volatility: float,
    risk_free_rate: float = 0.045,
    dividend_yield: float = 0.0,
) -> float:
    """Estimate an OTM call strike matching a target call delta.

    Uses bisection over a broad strike interval. The result is rounded to the
    nearest dollar to match the current scaffold style.
    """

    s = float(underlying_price)
    target = min(max(float(target_delta), 0.05), 0.95)

    low = max(s * 0.50, 1.0)
    high = s * 1.75

    for _ in range(80):
        mid = (low + high) / 2.0
        inputs = OptionPremiumInputs(
            underlying_price=s,
            strike_price=mid,
            days_to_expiration=days_to_expiration,
            implied_volatility=implied_volatility,
            risk_free_rate=risk_free_rate,
            dividend_yield=dividend_yield,
        )
        delta = black_scholes_call_delta(inputs)

        # Higher strike means lower delta. Move bounds accordingly.
        if delta > target:
            low = mid
        else:
            high = mid

    return round((low + high) / 2.0, 0)


def _get_value(obj: Any, candidates: list[str], default: Any = None) -> Any:
    for name in candidates:
        if isinstance(obj, dict) and name in obj:
            return obj[name]
        if hasattr(obj, name):
            return getattr(obj, name)
    return default


def fallback_scenario_assumptions() -> list[PremiumScenarioAssumption]:
    """Fallback assumptions matching the current Phase 2 path scaffold."""

    return [
        PremiumScenarioAssumption(
            scenario_name="downtrend",
            display_name="Downtrend",
            modeled_total_return_percent=-8.0,
            realized_volatility_label="high",
            implied_volatility_bias="elevated",
            skew_bias="put_bid",
            path_shape="front_loaded",
            covered_call_profile="premium cushion, assignment unlikely",
            interpretation="A falling market can make the option premium useful as a partial cushion, but stock losses still dominate if the decline is large.",
        ),
        PremiumScenarioAssumption(
            scenario_name="sideways_choppy",
            display_name="Sideways Choppy",
            modeled_total_return_percent=0.0,
            realized_volatility_label="moderate",
            implied_volatility_bias="firm",
            skew_bias="neutral",
            path_shape="choppy",
            covered_call_profile="premium harvest favored",
            interpretation="A flat but noisy path is typically favorable for covered-call income because buy-and-hold has little directional gain.",
        ),
        PremiumScenarioAssumption(
            scenario_name="moderate_uptrend",
            display_name="Moderate Uptrend",
            modeled_total_return_percent=5.0,
            realized_volatility_label="normal",
            implied_volatility_bias="neutral",
            skew_bias="neutral",
            path_shape="back_loaded",
            covered_call_profile="moderate upside participation with some cap risk",
            interpretation="A moderate rise can still work if the premium plus stock appreciation outweighs the value given up above the strike.",
        ),
        PremiumScenarioAssumption(
            scenario_name="strong_rally",
            display_name="Strong Rally",
            modeled_total_return_percent=12.0,
            realized_volatility_label="low",
            implied_volatility_bias="compressed",
            skew_bias="call_bid",
            path_shape="linear",
            covered_call_profile="upside cap risk dominates",
            interpretation="A strong rally is usually the worst relative case for a covered call because buy-and-hold keeps all upside while the short call caps gains.",
        ),
        PremiumScenarioAssumption(
            scenario_name="volatile_whipsaw",
            display_name="Volatile Whipsaw",
            modeled_total_return_percent=2.0,
            realized_volatility_label="very_high",
            implied_volatility_bias="spiking",
            skew_bias="put_bid",
            path_shape="whipsaw",
            covered_call_profile="high premium but high path risk",
            interpretation="A whipsaw environment may generate more premium, but path risk and timing matter more than the final price alone.",
        ),
    ]


def load_scenario_assumptions() -> list[PremiumScenarioAssumption]:
    """Load assumptions from scenario_assumptions.py when available.

    The loader is compatibility-oriented because Phase 2 scaffold modules have
    evolved through several small steps.
    """

    try:
        from app.paid_simulator import scenario_assumptions as assumptions_module
    except Exception:
        return fallback_scenario_assumptions()

    getter = None
    for name in [
        "get_default_scenario_assumptions",
        "build_default_scenario_assumptions",
        "get_scenario_assumptions",
        "build_scenario_assumptions",
    ]:
        if hasattr(assumptions_module, name):
            getter = getattr(assumptions_module, name)
            break

    if getter is None:
        return fallback_scenario_assumptions()

    try:
        raw_items = getter()
    except Exception:
        return fallback_scenario_assumptions()

    assumptions: list[PremiumScenarioAssumption] = []
    for item in raw_items:
        assumptions.append(
            PremiumScenarioAssumption(
                scenario_name=str(_get_value(item, ["scenario_name", "name", "scenario"], "unknown")),
                display_name=str(_get_value(item, ["display_name", "scenario_display_name", "label"], "Scenario")),
                modeled_total_return_percent=float(_get_value(item, ["modeled_total_return_percent", "total_return_percent", "modeled_return"], 0.0)),
                realized_volatility_label=str(_get_value(item, ["realized_volatility_label", "volatility_label", "realized_vol_label"], "normal")),
                implied_volatility_bias=str(_get_value(item, ["implied_volatility_bias", "iv_bias"], "neutral")),
                skew_bias=str(_get_value(item, ["skew_bias", "skew"], "neutral")),
                path_shape=str(_get_value(item, ["path_shape", "shape"], "linear")),
                covered_call_profile=str(_get_value(item, ["covered_call_profile", "profile"], "scenario dependent")),
                interpretation=str(_get_value(item, ["interpretation", "plain_english_interpretation", "description"], "")),
            )
        )

    return assumptions or fallback_scenario_assumptions()


def build_option_premium_results(
    underlying_price: float = 545.25,
    target_delta: float = 0.30,
    days_to_expiration: int = 30,
    risk_free_rate: float = 0.045,
    dividend_yield: float = 0.0,
) -> list[OptionPremiumResult]:
    """Build one option-premium result per scenario assumption."""

    results: list[OptionPremiumResult] = []
    for scenario in load_scenario_assumptions():
        base_iv = estimate_implied_volatility(
            scenario.realized_volatility_label,
            scenario.implied_volatility_bias,
        )
        scenario_iv = apply_skew_to_otm_call_iv(base_iv, scenario.skew_bias, target_delta)
        strike = estimate_strike_for_target_delta(
            underlying_price=underlying_price,
            target_delta=target_delta,
            days_to_expiration=days_to_expiration,
            implied_volatility=scenario_iv,
            risk_free_rate=risk_free_rate,
            dividend_yield=dividend_yield,
        )
        inputs = OptionPremiumInputs(
            underlying_price=underlying_price,
            strike_price=strike,
            days_to_expiration=days_to_expiration,
            implied_volatility=scenario_iv,
            risk_free_rate=risk_free_rate,
            dividend_yield=dividend_yield,
        )
        premium = black_scholes_call_price(inputs)
        delta = black_scholes_call_delta(inputs)
        moneyness = (strike / underlying_price - 1.0) * 100.0
        note = (
            "Black-Scholes-style scaffold estimate using scenario-level IV and skew assumptions. "
            "Use as modeling infrastructure, not a live quote."
        )
        results.append(
            OptionPremiumResult(
                scenario_name=scenario.scenario_name,
                display_name=scenario.display_name,
                underlying_price=round(float(underlying_price), 4),
                target_delta=round(float(target_delta), 4),
                estimated_strike=round(float(strike), 4),
                days_to_expiration=int(days_to_expiration),
                implied_volatility=round(float(scenario_iv), 6),
                risk_free_rate=round(float(risk_free_rate), 6),
                dividend_yield=round(float(dividend_yield), 6),
                estimated_call_premium=round(float(premium), 4),
                estimated_call_delta=round(float(delta), 4),
                moneyness_percent=round(float(moneyness), 4),
                pricing_note=note,
            )
        )

    return results


def export_option_premium_results(output_path: Path, **kwargs: Any) -> Path:
    """Write option-premium scaffold results to CSV."""

    results = build_option_premium_results(**kwargs)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = [asdict(row) for row in results]
    fieldnames = list(rows[0].keys()) if rows else []
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return output_path
