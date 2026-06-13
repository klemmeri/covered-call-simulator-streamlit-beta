"""
scenario_price_paths.py

Phase 2 scaffold: deterministic price-path generation for paid simulator scenarios.

This module deliberately stays separate from the working v0.1 dashboard and simulator
engine. It accepts scenario-definition objects from scenario_model.py, but it is
intentionally tolerant of field-name differences between scaffold versions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

import pandas as pd


@dataclass(frozen=True)
class PricePathPoint:
    """One point on a modeled scenario price path."""

    scenario_name: str
    scenario_display_name: str
    step: int
    total_steps: int
    starting_price: float
    price: float
    final_target_price: float
    modeled_return: float
    modeled_return_percent: float
    path_shape: str
    volatility_label: str
    interpretation: str


def _get_field(obj: Any, names: list[str], default: Any = None) -> Any:
    """Return the first available attribute or dictionary key from names."""
    if isinstance(obj, dict):
        for name in names:
            if name in obj:
                return obj[name]
        return default

    for name in names:
        if hasattr(obj, name):
            return getattr(obj, name)
    return default


def _scenario_name(scenario: Any) -> str:
    return str(
        _get_field(
            scenario,
            ["name", "scenario_name", "key", "id", "label", "display_name"],
            "scenario",
        )
    )


def _scenario_display_name(scenario: Any) -> str:
    return str(
        _get_field(
            scenario,
            ["display_name", "scenario_display_name", "title", "name", "scenario_name"],
            _scenario_name(scenario),
        )
    )


def _scenario_path_shape(scenario: Any) -> str:
    return str(
        _get_field(
            scenario,
            ["path_shape", "shape", "price_path_shape", "path_type"],
            "linear",
        )
    ).strip().lower()


def _scenario_volatility_label(scenario: Any) -> str:
    return str(
        _get_field(
            scenario,
            ["volatility_label", "vol_label", "volatility", "volatility_regime"],
            "moderate",
        )
    )


def _scenario_interpretation(scenario: Any) -> str:
    return str(
        _get_field(
            scenario,
            ["interpretation", "plain_english_interpretation", "description", "notes"],
            "Modeled scenario path for Phase 2 scaffold testing.",
        )
    )


def _scenario_total_return(scenario: Any) -> float:
    """
    Return total modeled return as a decimal.

    Handles both decimal forms, such as 0.08, and percent forms, such as 8.0.
    """
    raw = _get_field(
        scenario,
        [
            "total_return",
            "modeled_return",
            "total_modeled_return",
            "return_value",
            "scenario_return",
            "total_return_percent",
            "modeled_return_percent",
            "total_modeled_return_percent",
            "return_percent",
        ],
        0.0,
    )

    try:
        value = float(raw)
    except Exception:
        return 0.0

    # Values with magnitude above 1 are assumed to be percentages, e.g. 8.0 -> 0.08.
    if abs(value) > 1.0:
        return value / 100.0
    return value


def _progress_fraction(step: int, steps: int, shape: str) -> float:
    """Map a step number to a 0-1 progress fraction for the selected path shape."""
    if steps <= 0:
        return 1.0

    t = step / steps
    shape = (shape or "linear").strip().lower()

    if shape in {"linear", "straight", "steady"}:
        return t
    if shape in {"front_loaded", "front-loaded", "early", "fast_start"}:
        return t ** 0.55
    if shape in {"back_loaded", "back-loaded", "late", "slow_start"}:
        return t ** 1.85
    if shape in {"choppy", "sideways_choppy", "mean_reverting"}:
        # Choppy oscillation around a shallow trend.
        oscillation = 0.08 * ((-1) ** step) * (1.0 - abs(2.0 * t - 1.0) * 0.35)
        return min(max(t + oscillation, 0.0), 1.0)
    if shape in {"whipsaw", "volatile_whipsaw"}:
        if t < 0.35:
            return 1.20 * t
        if t < 0.70:
            return 0.42 - 0.60 * (t - 0.35)
        return 0.21 + 0.79 * ((t - 0.70) / 0.30)

    return t


def generate_price_path(
    scenario: Any,
    starting_price: float = 545.25,
    steps: int = 30,
) -> list[PricePathPoint]:
    """Generate one deterministic price path for one scenario definition."""
    if starting_price <= 0:
        raise ValueError("starting_price must be positive")
    if steps < 1:
        raise ValueError("steps must be at least 1")

    scenario_name = _scenario_name(scenario)
    display_name = _scenario_display_name(scenario)
    total_return = _scenario_total_return(scenario)
    path_shape = _scenario_path_shape(scenario)
    volatility_label = _scenario_volatility_label(scenario)
    interpretation = _scenario_interpretation(scenario)
    final_target_price = starting_price * (1.0 + total_return)

    points: list[PricePathPoint] = []
    for step in range(steps + 1):
        fraction = _progress_fraction(step, steps, path_shape)
        price = starting_price * (1.0 + total_return * fraction)
        points.append(
            PricePathPoint(
                scenario_name=scenario_name,
                scenario_display_name=display_name,
                step=step,
                total_steps=steps,
                starting_price=round(starting_price, 4),
                price=round(price, 4),
                final_target_price=round(final_target_price, 4),
                modeled_return=round(total_return, 8),
                modeled_return_percent=round(total_return * 100.0, 4),
                path_shape=path_shape,
                volatility_label=volatility_label,
                interpretation=interpretation,
            )
        )

    return points


def generate_all_price_paths(
    scenarios: Iterable[Any],
    starting_price: float = 545.25,
    steps: int = 30,
) -> pd.DataFrame:
    """Generate deterministic price paths for all scenarios and return a DataFrame."""
    rows: list[dict[str, Any]] = []
    for scenario in scenarios:
        for point in generate_price_path(scenario, starting_price=starting_price, steps=steps):
            rows.append(asdict(point))
    return pd.DataFrame(rows)


def save_price_paths_csv(
    scenarios: Iterable[Any],
    output_path: str | None = None,
    starting_price: float = 545.25,
    steps: int = 30,
) -> pd.DataFrame:
    """Generate all scaffold price paths and optionally save them to CSV."""
    df = generate_all_price_paths(scenarios=scenarios, starting_price=starting_price, steps=steps)
    if output_path:
        from pathlib import Path

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out, index=False)
    return df
