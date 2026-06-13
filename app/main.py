"""
main.py

Top-level runner for the Covered Call Simulator.

This version supports two run modes:

    RUN_MODE = "standard"
        Uses STANDARD_N_PATHS.

    RUN_MODE = "robustness"
        Uses ROBUSTNESS_N_PATHS.

Current experiment structure:

    6 market regimes x 11 covered-call management rule variants = 66 experiments

Market regimes:

    1. baseline
    2. sideways_market
    3. bullish_market
    4. bearish_market
    5. high_volatility
    6. low_volatility

Management rule variants:

    1. hold_to_expiration
    2. close_at_50_percent_profit
    3. close_at_50_percent_profit_then_wait_1d
    4. close_at_50_percent_profit_then_wait_3d
    5. close_at_50_percent_profit_then_wait_5d
    6. close_at_50_percent_profit_then_wait_10d
    7. close_at_50_percent_profit_then_pullback_or_wait_2pct_10d
    8. close_at_50_percent_profit_then_pullback_or_wait_3pct_10d
    9. adaptive_close50_wait10_by_regime
    10. adaptive_close50_wait10_by_regime_and_cost
    11. adaptive_by_regime_dte_cost

Adaptive rule behavior is implemented inside portfolio.py.

Outputs are organized into:

    outputs/tables/path_level
    outputs/tables/cycle_level
    outputs/tables/comparison

    outputs/charts/path_level
    outputs/charts/cycle_level
    outputs/charts/comparison

    outputs/archive
"""

import sys
from dataclasses import fields, is_dataclass, replace
from pathlib import Path
from typing import Any

import pandas as pd


# =============================================================================
# User settings
# =============================================================================

RUN_MODE = "standard"          # "standard" or "robustness"

STANDARD_N_PATHS = 250
ROBUSTNESS_N_PATHS = 1000


# =============================================================================
# Project setup
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.cleanup import archive_existing_outputs
from app.config import SimulationConfig
from app.simulator import SimulationEngine
from app.reports import (
    run_full_report,
    run_cycle_report,
    save_experiment_comparison,
    save_experiment_comparison_chart,
    save_cycle_comparison,
    save_cycle_comparison_charts,
    save_management_rule_comparison,
)


# =============================================================================
# Configuration helpers
# =============================================================================

def get_n_paths_for_run_mode() -> int:
    """
    Return the number of simulation paths for the selected run mode.
    """
    mode = RUN_MODE.strip().lower()

    if mode == "standard":
        return STANDARD_N_PATHS

    if mode == "robustness":
        return ROBUSTNESS_N_PATHS

    raise ValueError(
        f"Invalid RUN_MODE: {RUN_MODE!r}. "
        'Use RUN_MODE = "standard" or RUN_MODE = "robustness".'
    )


def config_field_names() -> set[str]:
    """
    Return the field names available in SimulationConfig.

    This keeps main.py tolerant of small changes in app/config.py.
    """
    if is_dataclass(SimulationConfig):
        return {field.name for field in fields(SimulationConfig)}

    return set()


def clone_config(base_config: SimulationConfig, **changes: Any) -> SimulationConfig:
    """
    Clone a SimulationConfig while applying only valid field changes.

    If SimulationConfig is a dataclass, use dataclasses.replace().
    Invalid field names are ignored so this script remains robust if the
    config object changes slightly.
    """
    valid_fields = config_field_names()

    if valid_fields:
        valid_changes = {
            key: value
            for key, value in changes.items()
            if key in valid_fields
        }
        return replace(base_config, **valid_changes)

    new_config = SimulationConfig()

    for key, value in vars(base_config).items():
        setattr(new_config, key, value)

    for key, value in changes.items():
        if hasattr(new_config, key):
            setattr(new_config, key, value)

    return new_config


def build_base_config() -> SimulationConfig:
    """
    Build the shared base configuration.

    The number of paths is controlled by RUN_MODE.
    """
    return clone_config(
        SimulationConfig(),
        n_paths=get_n_paths_for_run_mode(),
    )


# =============================================================================
# Regime configuration
# =============================================================================

def build_base_regime_configs() -> dict[str, SimulationConfig]:
    """
    Build the six base market-regime configurations.

    Each config includes regime_name so portfolio.py can apply adaptive rules
    directly.
    """
    base = build_base_config()

    regimes = {
        "baseline": clone_config(
            base,
            regime_name="baseline",
        ),

        "sideways_market": clone_config(
            base,
            regime_name="sideways_market",
            annual_return=0.00,
            expected_annual_return=0.00,
            annual_drift=0.00,
            drift=0.00,
            mean_return=0.00,
            mean_daily_return=0.00,
            daily_drift=0.00,
        ),

        "bullish_market": clone_config(
            base,
            regime_name="bullish_market",
            annual_return=0.18,
            expected_annual_return=0.18,
            annual_drift=0.18,
            drift=0.18,
            mean_return=0.18,
            mean_daily_return=0.18 / 252.0,
            daily_drift=0.18 / 252.0,
        ),

        "bearish_market": clone_config(
            base,
            regime_name="bearish_market",
            annual_return=-0.18,
            expected_annual_return=-0.18,
            annual_drift=-0.18,
            drift=-0.18,
            mean_return=-0.18,
            mean_daily_return=-0.18 / 252.0,
            daily_drift=-0.18 / 252.0,
        ),

        "high_volatility": clone_config(
            base,
            regime_name="high_volatility",
            annual_volatility=0.45,
            volatility=0.45,
            sigma=0.45,
            daily_volatility=0.45 / (252.0 ** 0.5),
        ),

        "low_volatility": clone_config(
            base,
            regime_name="low_volatility",
            annual_volatility=0.12,
            volatility=0.12,
            sigma=0.12,
            daily_volatility=0.12 / (252.0 ** 0.5),
        ),
    }

    return regimes


# =============================================================================
# Management-rule configuration
# =============================================================================

def build_rule_configs(
    regime_name: str,
    base_config: SimulationConfig,
) -> dict[str, SimulationConfig]:
    """
    Build all management-rule variants from one market-regime base config.

    The dictionary key is the experiment-level rule name.
    The SimulationConfig.management_rule field is the actual rule understood
    by portfolio.py.
    """
    return {
        "hold_to_expiration": clone_config(
            base_config,
            management_rule="hold_to_expiration",
            wait_days_after_profit_close=0,
            pullback_fraction_after_profit_close=0.0,
            max_wait_days_after_profit_close=0,
        ),

        "close_at_50_percent_profit": clone_config(
            base_config,
            management_rule="close_at_50_percent_profit",
            wait_days_after_profit_close=0,
            pullback_fraction_after_profit_close=0.0,
            max_wait_days_after_profit_close=0,
        ),

        "close_at_50_percent_profit_then_wait_1d": clone_config(
            base_config,
            management_rule="close_at_50_percent_profit_then_wait",
            wait_days_after_profit_close=1,
            pullback_fraction_after_profit_close=0.0,
            max_wait_days_after_profit_close=0,
        ),

        "close_at_50_percent_profit_then_wait_3d": clone_config(
            base_config,
            management_rule="close_at_50_percent_profit_then_wait",
            wait_days_after_profit_close=3,
            pullback_fraction_after_profit_close=0.0,
            max_wait_days_after_profit_close=0,
        ),

        "close_at_50_percent_profit_then_wait_5d": clone_config(
            base_config,
            management_rule="close_at_50_percent_profit_then_wait",
            wait_days_after_profit_close=5,
            pullback_fraction_after_profit_close=0.0,
            max_wait_days_after_profit_close=0,
        ),

        "close_at_50_percent_profit_then_wait_10d": clone_config(
            base_config,
            management_rule="close_at_50_percent_profit_then_wait",
            wait_days_after_profit_close=10,
            pullback_fraction_after_profit_close=0.0,
            max_wait_days_after_profit_close=0,
        ),

        "close_at_50_percent_profit_then_pullback_or_wait_2pct_10d": clone_config(
            base_config,
            management_rule="close_at_50_percent_profit_then_pullback_or_wait",
            wait_days_after_profit_close=0,
            pullback_fraction_after_profit_close=0.02,
            max_wait_days_after_profit_close=10,
        ),

        "close_at_50_percent_profit_then_pullback_or_wait_3pct_10d": clone_config(
            base_config,
            management_rule="close_at_50_percent_profit_then_pullback_or_wait",
            wait_days_after_profit_close=0,
            pullback_fraction_after_profit_close=0.03,
            max_wait_days_after_profit_close=10,
        ),

        "adaptive_close50_wait10_by_regime": clone_config(
            base_config,
            management_rule="adaptive_close50_wait10_by_regime",
            wait_days_after_profit_close=0,
            pullback_fraction_after_profit_close=0.0,
            max_wait_days_after_profit_close=0,
            adaptive_wait_days_after_profit_close=10,
        ),

        "adaptive_close50_wait10_by_regime_and_cost": clone_config(
            base_config,
            management_rule="adaptive_close50_wait10_by_regime_and_cost",
            wait_days_after_profit_close=0,
            pullback_fraction_after_profit_close=0.0,
            max_wait_days_after_profit_close=0,
            adaptive_wait_days_after_profit_close=10,
        ),

        "adaptive_by_regime_dte_cost": clone_config(
            base_config,
            management_rule="adaptive_by_regime_dte_cost",
            wait_days_after_profit_close=0,
            pullback_fraction_after_profit_close=0.0,
            max_wait_days_after_profit_close=0,
            adaptive_wait_days_after_profit_close=10,
        ),
    }


def build_experiment_configs() -> dict[str, SimulationConfig]:
    """
    Build the full experiment dictionary.

    Experiment names use this format:

        regime__rule_variant
    """
    regime_configs = build_base_regime_configs()

    experiment_configs: dict[str, SimulationConfig] = {}

    for regime_name, regime_config in regime_configs.items():
        rule_configs = build_rule_configs(
            regime_name=regime_name,
            base_config=regime_config,
        )

        for rule_name, rule_config in rule_configs.items():
            experiment_name = f"{regime_name}__{rule_name}"
            experiment_configs[experiment_name] = rule_config

    return experiment_configs


# =============================================================================
# Experiment execution
# =============================================================================

def run_experiment(
    experiment_name: str,
    config: SimulationConfig,
) -> tuple[pd.DataFrame, pd.DataFrame | None]:
    """
    Run one simulation experiment and generate its path-level and cycle-level
    reports.
    """
    print("=" * 100)
    print(f"Running experiment: {experiment_name}")
    print("=" * 100)

    engine = SimulationEngine(config)
    results_df = engine.run()

    run_full_report(
        experiment_name=experiment_name,
        results=results_df,
    )

    cycle_df = None

    if hasattr(engine, "cycle_log"):
        cycle_log = getattr(engine, "cycle_log")

        if cycle_log is not None:
            cycle_df = pd.DataFrame(cycle_log)

            if not cycle_df.empty:
                run_cycle_report(
                    experiment_name=experiment_name,
                    results=cycle_df,
                )

    return results_df, cycle_df


# =============================================================================
# Main batch runner
# =============================================================================

def main() -> None:
    """
    Run all experiments and generate comparison reports.
    """
    archive_existing_outputs()

    n_paths = get_n_paths_for_run_mode()
    experiment_configs = build_experiment_configs()

    print()
    print("=" * 100)
    print("COVERED CALL SIMULATOR BATCH RUN")
    print("=" * 100)
    print(f"Run mode:              {RUN_MODE}")
    print(f"Paths per experiment:  {n_paths}")
    print(f"Total experiments:     {len(experiment_configs)}")
    print("=" * 100)
    print()

    all_results: dict[str, pd.DataFrame] = {}
    all_cycle_results: dict[str, pd.DataFrame] = {}

    for experiment_name, config in experiment_configs.items():
        results_df, cycle_df = run_experiment(
            experiment_name=experiment_name,
            config=config,
        )

        all_results[experiment_name] = results_df

        if cycle_df is not None and not cycle_df.empty:
            all_cycle_results[experiment_name] = cycle_df

    print("=" * 100)
    print("Generating comparison reports")
    print("=" * 100)

    save_experiment_comparison(all_results)
    save_experiment_comparison_chart(all_results)

    if all_cycle_results:
        save_cycle_comparison(all_cycle_results)
        save_cycle_comparison_charts(all_cycle_results)

    save_management_rule_comparison(all_results)

    print()
    print("=" * 100)
    print("Simulation batch complete.")
    print("=" * 100)
    print(f"Run mode:                    {RUN_MODE}")
    print(f"Paths per experiment:        {n_paths}")
    print(f"Total experiments completed: {len(all_results)}")
    print()
    print("Expected comparison files:")
    print("  outputs/tables/comparison/experiment_comparison.csv")
    print("  outputs/tables/comparison/cycle_level_comparison.csv")
    print("  outputs/tables/comparison/management_rule_comparison.csv")
    print("  outputs/tables/comparison/management_rule_decision_summary.csv")
    print("  outputs/tables/comparison/strategy_map.csv")
    print("=" * 100)
    print()


if __name__ == "__main__":
    main()