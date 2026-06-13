"""
scenario_assumptions.py

Phase 2 scenario-assumptions scaffold for the paid covered-call simulator.

This module defines the modeled scenario assumptions used by the Phase 2
scaffold. It is intentionally separate from the working v0.1 dashboard and
from the existing simulator engine.

Important:
    The modeled_total_return_percent values are aligned with the current
    scenario_price_paths.py scaffold so the assumption-consistency checker can
    compare the assumptions CSV with the final generated price-path returns.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]
OUTPUT_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "paid_simulator"
    / "scenario_assumptions_scaffold.csv"
)


@dataclass(frozen=True)
class ScenarioAssumption:
    """One modeled market-path assumption set for the Phase 2 scaffold."""

    scenario_name: str
    scenario_display_name: str
    modeled_total_return_percent: float
    realized_volatility_label: str
    implied_volatility_bias: str
    skew_bias: str
    path_shape: str
    covered_call_profile: str
    plain_english_interpretation: str

    @property
    def name(self) -> str:
        """Compatibility alias for older scaffold modules."""
        return self.scenario_name

    @property
    def display_name(self) -> str:
        """Compatibility alias for older scaffold modules."""
        return self.scenario_display_name

    @property
    def total_return_percent(self) -> float:
        """Compatibility alias for older scaffold modules."""
        return self.modeled_total_return_percent


# These returns are intentionally aligned with the current price-path scaffold:
# downtrend -8%, sideways 0%, moderate uptrend +5%, strong rally +12%, whipsaw +2%.
def get_default_scenario_assumptions() -> list[ScenarioAssumption]:
    """Return the default Phase 2 scenario assumptions."""
    return [
        ScenarioAssumption(
            scenario_name="downtrend",
            scenario_display_name="Downtrend",
            modeled_total_return_percent=-8.0,
            realized_volatility_label="Elevated",
            implied_volatility_bias="Rising IV",
            skew_bias="Put skew firmer",
            path_shape="front_loaded",
            covered_call_profile="Premium cushions part of the decline, but stock loss dominates if the selloff is large.",
            plain_english_interpretation="A downtrend is where the covered call can help relative to buy-and-hold because option premium offsets some stock loss.",
        ),
        ScenarioAssumption(
            scenario_name="sideways_choppy",
            scenario_display_name="Sideways Choppy",
            modeled_total_return_percent=0.0,
            realized_volatility_label="Moderate",
            implied_volatility_bias="Stable to slightly lower IV",
            skew_bias="Neutral skew",
            path_shape="choppy",
            covered_call_profile="Premium harvest is usually favorable when price finishes near the starting level.",
            plain_english_interpretation="A sideways path is typically favorable for covered-call income because the short call may expire with limited intrinsic value.",
        ),
        ScenarioAssumption(
            scenario_name="moderate_uptrend",
            scenario_display_name="Moderate Uptrend",
            modeled_total_return_percent=5.0,
            realized_volatility_label="Moderate",
            implied_volatility_bias="Slightly falling IV",
            skew_bias="Neutral to mild call bid",
            path_shape="back_loaded",
            covered_call_profile="The covered call can still perform well if the rally does not move too far beyond the call strike.",
            plain_english_interpretation="A moderate uptrend can be acceptable for covered calls if premium plus retained upside offsets any call cap.",
        ),
        ScenarioAssumption(
            scenario_name="strong_rally",
            scenario_display_name="Strong Rally",
            modeled_total_return_percent=12.0,
            realized_volatility_label="Low to moderate",
            implied_volatility_bias="Falling IV",
            skew_bias="Call wing interest possible",
            path_shape="linear",
            covered_call_profile="This is usually the weakest relative scenario because the short call caps upside participation.",
            plain_english_interpretation="A strong rally is the classic covered-call opportunity cost: the strategy may make money but lag buy-and-hold.",
        ),
        ScenarioAssumption(
            scenario_name="volatile_whipsaw",
            scenario_display_name="Volatile Whipsaw",
            modeled_total_return_percent=2.0,
            realized_volatility_label="High",
            implied_volatility_bias="Two-sided IV risk",
            skew_bias="Unstable skew",
            path_shape="whipsaw",
            covered_call_profile="Premium helps, but large path swings can make management and assignment risk more important.",
            plain_english_interpretation="A volatile whipsaw path tests whether premium income is enough to compensate for difficult intraperiod movement.",
        ),
    ]


# Compatibility aliases for earlier/later scaffold names.
def build_default_scenario_assumptions() -> list[ScenarioAssumption]:
    return get_default_scenario_assumptions()


def build_scenario_assumptions() -> list[ScenarioAssumption]:
    return get_default_scenario_assumptions()


def get_scenario_assumptions() -> list[ScenarioAssumption]:
    return get_default_scenario_assumptions()


def assumptions_to_dataframe(assumptions: Iterable[ScenarioAssumption]) -> pd.DataFrame:
    """Convert scenario assumptions to a pandas DataFrame."""
    return pd.DataFrame([asdict(item) for item in assumptions])


def build_assumptions_dataframe() -> pd.DataFrame:
    """Return the default assumptions as a DataFrame."""
    return assumptions_to_dataframe(get_default_scenario_assumptions())


def save_scenario_assumptions_csv(output_path: Path | None = None) -> Path:
    """Write the default scenario assumptions CSV and return its path."""
    path = output_path or OUTPUT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    df = build_assumptions_dataframe()
    df.to_csv(path, index=False)
    return path


def main() -> None:
    path = save_scenario_assumptions_csv()
    print(f"Scenario assumptions written: {path}")
    print(build_assumptions_dataframe().to_string(index=False))


if __name__ == "__main__":
    main()
