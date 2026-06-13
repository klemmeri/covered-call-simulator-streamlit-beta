"""
scenario_library.py

Scenario library for the paid Covered Call Simulator.

This module defines reusable illustrative price-path scenarios.

Purpose:
    Let the simulator test covered-call behavior under different path shapes:

        - moderate uptrend
        - downtrend
        - sideways choppy
        - volatile two-sided
        - strong rally

These are not forecasts. They are deterministic educational scenarios used
to demonstrate how covered-call equity behaves under different market paths.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PriceScenario:
    """
    One deterministic illustrative price-path scenario.

    Attributes
    ----------
    name:
        Machine-readable scenario name.

    display_name:
        Human-readable scenario label.

    description:
        Plain-English scenario description.

    daily_returns:
        Decimal daily returns used to generate the path.
    """

    name: str
    display_name: str
    description: str
    daily_returns: list[float]


SCENARIOS: dict[str, PriceScenario] = {
    "moderate_uptrend": PriceScenario(
        name="moderate_uptrend",
        display_name="Moderate Uptrend",
        description=(
            "A mostly rising path with small pullbacks. This is useful for "
            "testing whether the covered call keeps up with buy-and-hold "
            "when the stock rises but does not immediately break through the "
            "short-call strike."
        ),
        daily_returns=[
            0.012,
            -0.006,
            0.004,
            0.018,
            -0.010,
            0.006,
            0.009,
        ],
    ),
    "downtrend": PriceScenario(
        name="downtrend",
        display_name="Downtrend",
        description=(
            "A declining path with minor rebounds. This is useful for showing "
            "how covered-call premium can partially buffer a stock decline."
        ),
        daily_returns=[
            -0.010,
            -0.008,
            0.004,
            -0.012,
            -0.006,
            0.003,
            -0.009,
        ],
    ),
    "sideways_choppy": PriceScenario(
        name="sideways_choppy",
        display_name="Sideways Choppy",
        description=(
            "A back-and-forth path with little net direction. This is often "
            "a favorable educational scenario for covered calls because the "
            "stock does not strongly outrun the short strike."
        ),
        daily_returns=[
            0.006,
            -0.005,
            0.004,
            -0.006,
            0.005,
            -0.003,
            0.002,
        ],
    ),
    "volatile_two_sided": PriceScenario(
        name="volatile_two_sided",
        display_name="Volatile Two-Sided",
        description=(
            "A larger-swing path that moves both up and down. This is useful "
            "for testing whether the short call liability and stock movement "
            "remain properly marked through a noisy path."
        ),
        daily_returns=[
            0.018,
            -0.022,
            0.026,
            -0.018,
            0.015,
            -0.012,
            0.010,
        ],
    ),
    "strong_rally": PriceScenario(
        name="strong_rally",
        display_name="Strong Rally",
        description=(
            "A persistent upward path. This is useful for demonstrating the "
            "covered-call tradeoff: the stock gains value, but the short call "
            "becomes more expensive and may eventually cap upside."
        ),
        daily_returns=[
            0.018,
            0.016,
            0.014,
            0.018,
            0.012,
            0.015,
            0.014,
        ],
    ),
}


DEFAULT_SCENARIO_NAME = "moderate_uptrend"


def list_scenarios() -> list[dict[str, object]]:
    """
    Return compact descriptions of all available scenarios.
    """
    rows: list[dict[str, object]] = []

    for scenario in SCENARIOS.values():
        rows.append(
            {
                "name": scenario.name,
                "display_name": scenario.display_name,
                "steps": len(scenario.daily_returns),
                "total_simple_return_percent": round(
                    sum(scenario.daily_returns) * 100.0,
                    2,
                ),
                "description": scenario.description,
            }
        )

    return rows


def get_scenario(
    scenario_name: str = DEFAULT_SCENARIO_NAME,
) -> PriceScenario:
    """
    Return a scenario by name.

    Raises
    ------
    ValueError
        If the scenario name is unknown.
    """
    normalized_name = scenario_name.strip().lower()

    if normalized_name not in SCENARIOS:
        available = ", ".join(sorted(SCENARIOS))
        raise ValueError(
            f"Unknown scenario '{scenario_name}'. Available scenarios: {available}"
        )

    return SCENARIOS[normalized_name]


def get_scenario_daily_returns(
    scenario_name: str = DEFAULT_SCENARIO_NAME,
) -> list[float]:
    """
    Return daily returns for a named scenario.
    """
    scenario = get_scenario(scenario_name=scenario_name)
    return list(scenario.daily_returns)


def generate_price_path_from_returns(
    starting_price: float,
    daily_returns: list[float],
) -> list[float]:
    """
    Generate a price path from a starting price and daily returns.
    """
    if starting_price <= 0:
        raise ValueError("Starting price must be greater than zero.")

    prices: list[float] = []
    current_price = starting_price

    for daily_return in daily_returns:
        current_price = round(current_price * (1.0 + daily_return), 2)
        prices.append(current_price)

    return prices


def generate_scenario_price_path(
    starting_price: float,
    scenario_name: str = DEFAULT_SCENARIO_NAME,
) -> list[float]:
    """
    Generate a price path for a named scenario.
    """
    daily_returns = get_scenario_daily_returns(scenario_name=scenario_name)

    return generate_price_path_from_returns(
        starting_price=starting_price,
        daily_returns=daily_returns,
    )


def describe_scenario(
    scenario_name: str = DEFAULT_SCENARIO_NAME,
) -> dict[str, object]:
    """
    Return a compact dictionary describing one scenario.
    """
    scenario = get_scenario(scenario_name=scenario_name)

    return {
        "name": scenario.name,
        "display_name": scenario.display_name,
        "description": scenario.description,
        "steps": len(scenario.daily_returns),
        "daily_returns": list(scenario.daily_returns),
        "total_simple_return_percent": round(
            sum(scenario.daily_returns) * 100.0,
            2,
        ),
    }
