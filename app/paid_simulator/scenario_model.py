"""
scenario_model.py

Phase 2 modeling scaffold for the Covered Call Strategy Stress Test.

This module is intentionally add-only and independent of the current paid
simulator engine. It defines a small, explicit scenario-model layer that can be
expanded later without disturbing the working v0.1 dashboard.

Current purpose:
    1. Define market-path scenario assumptions in one place.
    2. Provide simple validation for scenario definitions.
    3. Produce a readable scenario summary table.
    4. Prepare the project for more realistic scenario analytics in Phase 2.

Important:
    These scenarios are not forecasts. They are modeled stress-test paths used
    to understand covered-call tradeoffs versus buy-and-hold.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class ScenarioDefinition:
    """Definition of one modeled market path."""

    scenario_name: str
    display_name: str
    total_return_percent: float
    volatility_label: str
    path_shape: str
    interpretation: str

    def to_dict(self) -> dict[str, object]:
        """Return a dictionary representation suitable for CSV/report output."""
        return asdict(self)


DEFAULT_SCENARIOS: tuple[ScenarioDefinition, ...] = (
    ScenarioDefinition(
        scenario_name="downtrend",
        display_name="Downtrend",
        total_return_percent=-8.0,
        volatility_label="Moderate",
        path_shape="steady decline",
        interpretation=(
            "Covered calls may outperform buy-and-hold because option premium can "
            "partially cushion the stock decline."
        ),
    ),
    ScenarioDefinition(
        scenario_name="sideways_choppy",
        display_name="Sideways Choppy",
        total_return_percent=0.0,
        volatility_label="Moderate to high",
        path_shape="range-bound with noise",
        interpretation=(
            "Covered calls often work well when the stock moves sideways because "
            "premium income can accumulate while upside opportunity cost is limited."
        ),
    ),
    ScenarioDefinition(
        scenario_name="moderate_uptrend",
        display_name="Moderate Uptrend",
        total_return_percent=5.0,
        volatility_label="Moderate",
        path_shape="gradual rise",
        interpretation=(
            "Covered calls may still perform reasonably, but gains can begin to lag "
            "buy-and-hold if the short call limits upside participation."
        ),
    ),
    ScenarioDefinition(
        scenario_name="strong_rally",
        display_name="Strong Rally",
        total_return_percent=12.0,
        volatility_label="Low to moderate",
        path_shape="persistent rally",
        interpretation=(
            "Covered calls commonly lag buy-and-hold in strong rallies because the "
            "short call caps part of the upside."
        ),
    ),
    ScenarioDefinition(
        scenario_name="volatile_whipsaw",
        display_name="Volatile Whipsaw",
        total_return_percent=2.0,
        volatility_label="High",
        path_shape="large two-way movement",
        interpretation=(
            "The result depends on path, timing, and management rules. Premium helps, "
            "but large swings can create assignment, roll, or opportunity-cost issues."
        ),
    ),
)


def get_default_scenarios() -> tuple[ScenarioDefinition, ...]:
    """Return the default Phase 2 scenario definitions."""
    return DEFAULT_SCENARIOS


def scenarios_to_dataframe(scenarios: Iterable[ScenarioDefinition] | None = None) -> pd.DataFrame:
    """Return scenario definitions as a pandas DataFrame."""
    scenario_list = list(scenarios if scenarios is not None else DEFAULT_SCENARIOS)
    return pd.DataFrame([scenario.to_dict() for scenario in scenario_list])


def validate_scenarios(scenarios: Iterable[ScenarioDefinition] | None = None) -> tuple[list[str], list[str]]:
    """
    Validate scenario definitions.

    Returns
    -------
    errors, warnings
        Blocking errors and nonblocking warnings.
    """
    errors: list[str] = []
    warnings: list[str] = []
    scenario_list = list(scenarios if scenarios is not None else DEFAULT_SCENARIOS)

    if not scenario_list:
        errors.append("At least one scenario definition is required.")
        return errors, warnings

    names_seen: set[str] = set()
    for index, scenario in enumerate(scenario_list, start=1):
        if not scenario.scenario_name.strip():
            errors.append(f"Scenario {index} has a blank scenario_name.")
        if not scenario.display_name.strip():
            errors.append(f"Scenario {index} has a blank display_name.")
        if scenario.scenario_name in names_seen:
            errors.append(f"Duplicate scenario_name detected: {scenario.scenario_name}")
        names_seen.add(scenario.scenario_name)

        if scenario.total_return_percent < -100:
            errors.append(
                f"Scenario {scenario.scenario_name} has total_return_percent below -100%."
            )
        if abs(scenario.total_return_percent) > 30:
            warnings.append(
                f"Scenario {scenario.display_name} has a large modeled total return "
                f"({scenario.total_return_percent:.1f}%). Confirm this is intentional."
            )
        if not scenario.interpretation.strip():
            warnings.append(f"Scenario {scenario.display_name} has no interpretation text.")

    has_down = any(s.total_return_percent < 0 for s in scenario_list)
    has_up = any(s.total_return_percent > 0 for s in scenario_list)
    has_flat = any(abs(s.total_return_percent) < 1e-9 for s in scenario_list)

    if not has_down:
        warnings.append("Scenario set has no declining-market path.")
    if not has_up:
        warnings.append("Scenario set has no rising-market path.")
    if not has_flat:
        warnings.append("Scenario set has no flat/sideways path.")

    return errors, warnings


def build_scenario_summary_text(scenarios: Iterable[ScenarioDefinition] | None = None) -> str:
    """Build a plain-English summary of the scenario set."""
    scenario_list = list(scenarios if scenarios is not None else DEFAULT_SCENARIOS)
    errors, warnings = validate_scenarios(scenario_list)

    lines: list[str] = []
    lines.append("Phase 2 Scenario Model Scaffold")
    lines.append("=" * 80)
    lines.append("")
    lines.append("Purpose")
    lines.append("-" * 80)
    lines.append(
        "This scaffold centralizes modeled market paths for covered-call stress testing. "
        "The scenarios are not forecasts; they are controlled paths for comparing income, "
        "downside cushion, and upside give-up."
    )
    lines.append("")
    lines.append("Scenario definitions")
    lines.append("-" * 80)

    for scenario in scenario_list:
        lines.append(
            f"{scenario.display_name}: {scenario.total_return_percent:+.1f}% total return, "
            f"{scenario.volatility_label} volatility, {scenario.path_shape}."
        )
        lines.append(f"  Interpretation: {scenario.interpretation}")

    lines.append("")
    lines.append("Validation")
    lines.append("-" * 80)
    if errors:
        lines.append("Errors:")
        for error in errors:
            lines.append(f"  - {error}")
    else:
        lines.append("Errors: none")

    if warnings:
        lines.append("Warnings:")
        for warning in warnings:
            lines.append(f"  - {warning}")
    else:
        lines.append("Warnings: none")

    return "\n".join(lines)


if __name__ == "__main__":
    print(build_scenario_summary_text())
