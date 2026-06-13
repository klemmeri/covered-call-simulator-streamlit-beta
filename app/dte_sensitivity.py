"""
dte_sensitivity.py

DTE sensitivity test for the Covered Call Simulator.

Purpose
-------
This standalone script tests whether the preferred covered-call management
rule changes when the option Days to Expiration (DTE) changes.

Rules compared
--------------
1. HoldToExpiration
2. Close50
3. Wait10d
4. AdaptiveClose50Wait10
5. AdaptiveClose50Wait10CostAware

DTE values tested
-----------------
7
14
21
30
45

Output files
------------
outputs/tables/comparison/dte_sensitivity_summary.csv
outputs/tables/comparison/dte_sensitivity_winners.csv
outputs/tables/comparison/dte_sensitivity_report.txt

outputs/charts/comparison/dte_sensitivity_mean_outperformance.png
outputs/charts/comparison/dte_sensitivity_net_option_effect.png
outputs/charts/comparison/dte_sensitivity_transaction_cost.png

Important
---------
This script does not modify main.py.

It reuses the existing regime structure from app.main and the existing
SimulationEngine.

If this script cannot find the correct DTE field in SimulationConfig, it will
raise a clear error listing the available config fields.
"""

from __future__ import annotations

import sys
from dataclasses import fields, is_dataclass, replace
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd


# =============================================================================
# Paths
# =============================================================================

CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


from app.config import SimulationConfig
from app.simulator import SimulationEngine


# =============================================================================
# User settings
# =============================================================================

N_PATHS = 1000

DTE_VALUES = [
    7,
    14,
    21,
    30,
    45,
]

REGIME_ORDER = [
    "baseline",
    "sideways_market",
    "bullish_market",
    "bearish_market",
    "high_volatility",
    "low_volatility",
]

RULE_CONFIGS = {
    "HoldToExpiration": {
        "management_rule": "hold_to_expiration",
        "wait_days_after_profit_close": 0,
        "pullback_fraction_after_profit_close": 0.0,
        "max_wait_days_after_profit_close": 0,
        "adaptive_wait_days_after_profit_close": 10,
    },
    "Close50": {
        "management_rule": "close_at_50_percent_profit",
        "wait_days_after_profit_close": 0,
        "pullback_fraction_after_profit_close": 0.0,
        "max_wait_days_after_profit_close": 0,
        "adaptive_wait_days_after_profit_close": 10,
    },
    "Wait10d": {
        "management_rule": "close_at_50_percent_profit_then_wait",
        "wait_days_after_profit_close": 10,
        "pullback_fraction_after_profit_close": 0.0,
        "max_wait_days_after_profit_close": 0,
        "adaptive_wait_days_after_profit_close": 10,
    },
    "AdaptiveClose50Wait10": {
        "management_rule": "adaptive_close50_wait10_by_regime",
        "wait_days_after_profit_close": 0,
        "pullback_fraction_after_profit_close": 0.0,
        "max_wait_days_after_profit_close": 0,
        "adaptive_wait_days_after_profit_close": 10,
    },
    "AdaptiveClose50Wait10CostAware": {
        "management_rule": "adaptive_close50_wait10_by_regime_and_cost",
        "wait_days_after_profit_close": 0,
        "pullback_fraction_after_profit_close": 0.0,
        "max_wait_days_after_profit_close": 0,
        "adaptive_wait_days_after_profit_close": 10,
    },
}

RULE_ORDER = list(RULE_CONFIGS.keys())

# The script will set every matching DTE field it finds.
# Only existing SimulationConfig fields are used.
DTE_FIELD_CANDIDATES = [
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


# =============================================================================
# Output paths
# =============================================================================

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "comparison"
OUTPUT_CHART_DIR = PROJECT_ROOT / "outputs" / "charts" / "comparison"

SUMMARY_PATH = OUTPUT_TABLE_DIR / "dte_sensitivity_summary.csv"
WINNERS_PATH = OUTPUT_TABLE_DIR / "dte_sensitivity_winners.csv"
REPORT_PATH = OUTPUT_TABLE_DIR / "dte_sensitivity_report.txt"

OUTPERFORMANCE_CHART_PATH = (
    OUTPUT_CHART_DIR / "dte_sensitivity_mean_outperformance.png"
)
NET_EFFECT_CHART_PATH = (
    OUTPUT_CHART_DIR / "dte_sensitivity_net_option_effect.png"
)
TRANSACTION_COST_CHART_PATH = (
    OUTPUT_CHART_DIR / "dte_sensitivity_transaction_cost.png"
)


# =============================================================================
# Config helpers
# =============================================================================

def config_field_names(config: SimulationConfig | None = None) -> set[str]:
    """
    Return SimulationConfig dataclass field names.
    """

    target = config if config is not None else SimulationConfig()

    if is_dataclass(target):
        return {field.name for field in fields(target)}

    return set(vars(target).keys())


def clone_config(base_config: SimulationConfig, **changes: Any) -> SimulationConfig:
    """
    Clone a SimulationConfig while applying only valid field changes.
    """

    valid_fields = config_field_names(base_config)

    valid_changes = {
        key: value
        for key, value in changes.items()
        if key in valid_fields
    }

    if is_dataclass(base_config):
        return replace(base_config, **valid_changes)

    new_config = SimulationConfig()

    for key, value in vars(base_config).items():
        setattr(new_config, key, value)

    for key, value in valid_changes.items():
        setattr(new_config, key, value)

    return new_config


def find_available_dte_fields(config: SimulationConfig) -> list[str]:
    """
    Return DTE field names that exist in SimulationConfig.
    """

    valid_fields = config_field_names(config)

    return [
        field_name
        for field_name in DTE_FIELD_CANDIDATES
        if field_name in valid_fields
    ]


def apply_dte_to_config(
    base_config: SimulationConfig,
    dte: int,
) -> SimulationConfig:
    """
    Apply DTE to every recognized DTE-related config field.

    This makes the script robust to the exact field name used in config.py.
    """

    available_dte_fields = find_available_dte_fields(base_config)

    if not available_dte_fields:
        valid_fields = sorted(config_field_names(base_config))

        raise KeyError(
            "Could not find a recognized DTE field in SimulationConfig.\n\n"
            "The script looked for these possible field names:\n"
            f"{DTE_FIELD_CANDIDATES}\n\n"
            "Available SimulationConfig fields are:\n"
            f"{valid_fields}\n\n"
            "Fix: add the correct DTE field name to DTE_FIELD_CANDIDATES "
            "near the top of app/dte_sensitivity.py."
        )

    changes = {
        field_name: dte
        for field_name in available_dte_fields
    }

    return clone_config(base_config, **changes)


def load_regime_configs() -> dict[str, SimulationConfig]:
    """
    Load the six base market-regime configs from app.main.

    This keeps DTE sensitivity testing consistent with the main simulator.
    """

    try:
        from app.main import build_base_regime_configs

        regime_configs = build_base_regime_configs()

        if not isinstance(regime_configs, dict):
            raise TypeError(
                "build_base_regime_configs() did not return a dictionary."
            )

        print("Loaded regime configs from app.main.build_base_regime_configs().")

    except Exception as exc:
        print("")
        print("WARNING:")
        print("Could not import build_base_regime_configs() from app.main.")
        print("Using fallback SimulationConfig() regime configs.")
        print("")
        print("Import error was:")
        print(f"    {exc}")
        print("")

        regime_configs = {
            regime_name: clone_config(
                SimulationConfig(),
                regime_name=regime_name,
            )
            for regime_name in REGIME_ORDER
        }

    cleaned_configs = {}

    for regime_name in REGIME_ORDER:
        if regime_name not in regime_configs:
            continue

        cleaned_configs[regime_name] = clone_config(
            regime_configs[regime_name],
            regime_name=regime_name,
            n_paths=N_PATHS,
        )

    return cleaned_configs


def build_experiment_config(
    base_config: SimulationConfig,
    dte: int,
    rule_label: str,
) -> SimulationConfig:
    """
    Build one config for one DTE/rule combination.
    """

    config = apply_dte_to_config(
        base_config=base_config,
        dte=dte,
    )

    rule_changes = RULE_CONFIGS[rule_label].copy()
    rule_changes["n_paths"] = N_PATHS

    config = clone_config(config, **rule_changes)

    return config


# =============================================================================
# DataFrame helpers
# =============================================================================

def get_column(df: pd.DataFrame, possible_names: list[str]) -> str:
    """
    Return the first available column name from possible_names.
    """

    for name in possible_names:
        if name in df.columns:
            return name

    raise KeyError(
        "Could not find any of these columns:\n"
        f"{possible_names}\n\n"
        "Available columns are:\n"
        f"{list(df.columns)}"
    )


def get_optional_column(df: pd.DataFrame, possible_names: list[str]) -> str | None:
    """
    Return the first available column name from possible_names.
    """

    for name in possible_names:
        if name in df.columns:
            return name

    return None


def mean_or_nan(df: pd.DataFrame, column: str | None) -> float:
    """
    Return numeric mean or NaN.
    """

    if column is None:
        return float("nan")

    values = pd.to_numeric(df[column], errors="coerce")

    if values.dropna().empty:
        return float("nan")

    return float(values.mean())


def median_or_nan(df: pd.DataFrame, column: str | None) -> float:
    """
    Return numeric median or NaN.
    """

    if column is None:
        return float("nan")

    values = pd.to_numeric(df[column], errors="coerce")

    if values.dropna().empty:
        return float("nan")

    return float(values.median())


# =============================================================================
# Simulation helpers
# =============================================================================

def run_engine(config: SimulationConfig) -> pd.DataFrame:
    """
    Run SimulationEngine and return the path-level result DataFrame.
    """

    engine = SimulationEngine(config)
    result = engine.run()

    if isinstance(result, pd.DataFrame):
        return result

    if hasattr(engine, "path_results_df"):
        if isinstance(engine.path_results_df, pd.DataFrame):
            return engine.path_results_df

    raise RuntimeError(
        "SimulationEngine did not return a DataFrame and did not expose "
        "engine.path_results_df."
    )


def summarize_path_results(
    path_results: pd.DataFrame,
    dte: int,
    regime: str,
    rule_label: str,
) -> dict[str, Any]:
    """
    Summarize one simulation result.
    """

    final_value_col = get_column(
        path_results,
        [
            "final_covered_call_value",
            "final_portfolio_value",
            "ending_portfolio_value",
        ],
    )

    buy_hold_col = get_column(
        path_results,
        [
            "final_buy_and_hold_value",
            "buy_and_hold_final_value",
        ],
    )

    outperformance_col = get_optional_column(
        path_results,
        [
            "outperformance",
            "Outperformance",
        ],
    )

    net_effect_col = get_optional_column(
        path_results,
        [
            "net_option_effect",
            "Net_Option_Effect",
        ],
    )

    transaction_cost_col = get_optional_column(
        path_results,
        [
            "total_transaction_cost",
            "Total_Transaction_Cost",
        ],
    )

    commission_cost_col = get_optional_column(
        path_results,
        [
            "total_commission_cost",
            "Total_Commission_Cost",
        ],
    )

    slippage_cost_col = get_optional_column(
        path_results,
        [
            "total_slippage_cost",
            "Total_Slippage_Cost",
        ],
    )

    option_cycles_col = get_optional_column(
        path_results,
        [
            "option_cycles",
            "Option_Cycles",
        ],
    )

    assignments_col = get_optional_column(
        path_results,
        [
            "assignments",
            "Assignments",
        ],
    )

    if outperformance_col is not None:
        outperformance = pd.to_numeric(
            path_results[outperformance_col],
            errors="coerce",
        )
    else:
        outperformance = (
            pd.to_numeric(path_results[final_value_col], errors="coerce")
            - pd.to_numeric(path_results[buy_hold_col], errors="coerce")
        )

    return {
        "DTE": dte,
        "Regime": regime,
        "Rule_Label": rule_label,
        "Mean_Final_Covered_Call_Value": mean_or_nan(path_results, final_value_col),
        "Mean_Final_Buy_And_Hold_Value": mean_or_nan(path_results, buy_hold_col),
        "Mean_Outperformance": float(outperformance.mean()),
        "Median_Outperformance": float(outperformance.median()),
        "Percent_Outperforming_Buy_And_Hold": float((outperformance > 0).mean() * 100),
        "Mean_Net_Option_Effect": mean_or_nan(path_results, net_effect_col),
        "Median_Net_Option_Effect": median_or_nan(path_results, net_effect_col),
        "Mean_Total_Transaction_Cost": mean_or_nan(path_results, transaction_cost_col),
        "Mean_Total_Commission_Cost": mean_or_nan(path_results, commission_cost_col),
        "Mean_Total_Slippage_Cost": mean_or_nan(path_results, slippage_cost_col),
        "Mean_Option_Cycles": mean_or_nan(path_results, option_cycles_col),
        "Mean_Assignments": mean_or_nan(path_results, assignments_col),
    }


def run_one_experiment(
    base_config: SimulationConfig,
    dte: int,
    regime: str,
    rule_label: str,
) -> dict[str, Any]:
    """
    Run one DTE/regime/rule experiment.
    """

    config = build_experiment_config(
        base_config=base_config,
        dte=dte,
        rule_label=rule_label,
    )

    path_results = run_engine(config)

    return summarize_path_results(
        path_results=path_results,
        dte=dte,
        regime=regime,
        rule_label=rule_label,
    )


# =============================================================================
# Analysis
# =============================================================================

def build_winners(summary_df: pd.DataFrame) -> pd.DataFrame:
    """
    Find the best rule for each DTE/regime pair by mean outperformance.
    """

    df = summary_df.copy()
    df["Mean_Outperformance"] = pd.to_numeric(
        df["Mean_Outperformance"],
        errors="coerce",
    )

    df = df.dropna(subset=["Mean_Outperformance"])

    idx = (
        df
        .groupby(["DTE", "Regime"])["Mean_Outperformance"]
        .idxmax()
    )

    winners = (
        df
        .loc[idx]
        .copy()
        .sort_values(["DTE", "Regime"])
        .reset_index(drop=True)
    )

    winners = winners.rename(
        columns={
            "Rule_Label": "Winning_Rule",
            "Mean_Outperformance": "Winning_Mean_Outperformance",
            "Mean_Net_Option_Effect": "Winning_Mean_Net_Option_Effect",
            "Mean_Total_Transaction_Cost": "Winning_Mean_Total_Transaction_Cost",
        }
    )

    return winners


def format_decimal(value: Any, digits: int = 4) -> str:
    """
    Format a decimal value.
    """

    numeric = pd.to_numeric(value, errors="coerce")

    if pd.isna(numeric):
        return "NA"

    return f"{float(numeric):,.{digits}f}"


def format_currency(value: Any) -> str:
    """
    Format a dollar value.
    """

    numeric = pd.to_numeric(value, errors="coerce")

    if pd.isna(numeric):
        return "NA"

    return f"${float(numeric):,.2f}"


def build_report(summary_df: pd.DataFrame, winners_df: pd.DataFrame) -> str:
    """
    Build a plain-text DTE sensitivity report.
    """

    lines = []

    lines.append("Covered Call Simulator — DTE Sensitivity Report")
    lines.append("=" * 78)
    lines.append("")
    lines.append(f"Paths per experiment: {N_PATHS}")
    lines.append(f"DTE values tested:    {DTE_VALUES}")
    lines.append(f"Regimes tested:       {len(REGIME_ORDER)}")
    lines.append(f"Rules tested:         {len(RULE_ORDER)}")
    lines.append(
        f"Total experiments:    {len(DTE_VALUES) * len(REGIME_ORDER) * len(RULE_ORDER)}"
    )
    lines.append("")

    lines.append("Rules compared:")
    for rule in RULE_ORDER:
        lines.append(f"    {rule}")
    lines.append("")

    for dte in DTE_VALUES:
        lines.append("-" * 78)
        lines.append(f"DTE: {dte}")
        lines.append("-" * 78)

        dte_winners = winners_df[winners_df["DTE"] == dte].copy()

        if dte_winners.empty:
            lines.append("No winner data available.")
            lines.append("")
            continue

        for regime in REGIME_ORDER:
            regime_rows = dte_winners[dte_winners["Regime"] == regime]

            if regime_rows.empty:
                lines.append(f"{regime:<18} no data")
                continue

            row = regime_rows.iloc[0]

            lines.append(
                f"{regime:<18} "
                f"winner: {row['Winning_Rule']:<34} "
                f"outperf: {format_decimal(row['Winning_Mean_Outperformance']):>10} "
                f"net option: {format_currency(row['Winning_Mean_Net_Option_Effect']):>12} "
                f"cost: {format_currency(row['Winning_Mean_Total_Transaction_Cost']):>10}"
            )

        lines.append("")

    lines.append("=" * 78)
    lines.append("DTE Stability Summary")
    lines.append("=" * 78)
    lines.append("")

    for regime in REGIME_ORDER:
        regime_winners = winners_df[winners_df["Regime"] == regime].copy()

        if regime_winners.empty:
            lines.append(f"{regime}: no data")
            continue

        winner_sequence = [
            f"{int(row['DTE'])}DTE={row['Winning_Rule']}"
            for _, row in regime_winners.sort_values("DTE").iterrows()
        ]

        unique_winners = list(regime_winners["Winning_Rule"].dropna().unique())

        lines.append(f"{regime}:")
        lines.append(f"    Winner sequence: {', '.join(winner_sequence)}")
        lines.append(f"    Unique winners:  {', '.join(unique_winners)}")

        if len(unique_winners) == 1:
            lines.append("    Interpretation: Rule preference is stable across tested DTE values.")
        else:
            lines.append("    Interpretation: Rule preference changes with DTE.")

        lines.append("")

    lines.append("=" * 78)
    lines.append("Practical Interpretation")
    lines.append("=" * 78)
    lines.append("")
    lines.append(
        "This report tests whether the current regime-based rule is sensitive "
        "to the option DTE. If the same rule wins across most DTE values within "
        "a regime, the regime rule is robust. If the winner changes, DTE should "
        "be included as another decision variable."
    )
    lines.append("")
    lines.append(
        "If the adaptive rules remain near the best fixed rules across DTE values, "
        "the current adaptive framework is likely stable. If not, the next step "
        "would be to create a DTE-aware adaptive rule."
    )

    return "\n".join(lines)


# =============================================================================
# Charts
# =============================================================================

def save_grouped_chart(
    summary_df: pd.DataFrame,
    metric: str,
    title: str,
    ylabel: str,
    output_path: Path,
) -> None:
    """
    Save a grouped chart showing each rule by DTE.

    To keep the chart readable, this averages across regimes.
    """

    plot_df = summary_df.copy()
    plot_df[metric] = pd.to_numeric(plot_df[metric], errors="coerce")
    plot_df = plot_df.dropna(subset=[metric])

    if plot_df.empty:
        return

    grouped = (
        plot_df
        .groupby(["DTE", "Rule_Label"], as_index=False)[metric]
        .mean()
    )

    pivot = grouped.pivot(
        index="DTE",
        columns="Rule_Label",
        values=metric,
    )

    pivot = pivot.reindex(DTE_VALUES)
    pivot = pivot[RULE_ORDER]

    ax = pivot.plot(kind="bar", figsize=(14, 7))
    ax.axhline(0, linewidth=1)
    ax.set_title(title)
    ax.set_xlabel("DTE")
    ax.set_ylabel(ylabel)

    plt.xticks(rotation=0)
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()


def save_charts(summary_df: pd.DataFrame) -> None:
    """
    Save DTE sensitivity charts.
    """

    save_grouped_chart(
        summary_df=summary_df,
        metric="Mean_Outperformance",
        title="DTE Sensitivity — Mean Outperformance by Rule",
        ylabel="Mean Outperformance",
        output_path=OUTPERFORMANCE_CHART_PATH,
    )

    save_grouped_chart(
        summary_df=summary_df,
        metric="Mean_Net_Option_Effect",
        title="DTE Sensitivity — Mean Net Option Effect by Rule",
        ylabel="Mean Net Option Effect",
        output_path=NET_EFFECT_CHART_PATH,
    )

    save_grouped_chart(
        summary_df=summary_df,
        metric="Mean_Total_Transaction_Cost",
        title="DTE Sensitivity — Mean Transaction Cost by Rule",
        ylabel="Mean Transaction Cost",
        output_path=TRANSACTION_COST_CHART_PATH,
    )


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_CHART_DIR.mkdir(parents=True, exist_ok=True)

    regime_configs = load_regime_configs()

    if not regime_configs:
        raise RuntimeError("No regime configs were loaded.")

    first_config = next(iter(regime_configs.values()))
    dte_fields = find_available_dte_fields(first_config)

    print("")
    print("Covered Call Simulator — DTE Sensitivity Test")
    print("=" * 78)
    print(f"Project root:          {PROJECT_ROOT}")
    print(f"Paths per experiment:  {N_PATHS}")
    print(f"DTE values:            {DTE_VALUES}")
    print(f"Regimes:               {len(regime_configs)}")
    print(f"Rules:                 {len(RULE_ORDER)}")
    print(f"Total experiments:     {len(DTE_VALUES) * len(regime_configs) * len(RULE_ORDER)}")
    print(f"DTE config fields:     {dte_fields}")
    print("")

    if not dte_fields:
        raise KeyError(
            "No DTE fields found in SimulationConfig. "
            "Update DTE_FIELD_CANDIDATES in this script."
        )

    summary_rows = []
    experiment_counter = 0
    total_experiments = len(DTE_VALUES) * len(regime_configs) * len(RULE_ORDER)

    for dte in DTE_VALUES:
        print("")
        print("=" * 78)
        print(f"Running DTE = {dte}")
        print("=" * 78)

        for regime, base_config in regime_configs.items():
            print("")
            print(f"Regime: {regime}")

            for rule_label in RULE_ORDER:
                experiment_counter += 1

                print(
                    f"  [{experiment_counter:>3} / {total_experiments}] "
                    f"{rule_label}"
                )

                row = run_one_experiment(
                    base_config=base_config,
                    dte=dte,
                    regime=regime,
                    rule_label=rule_label,
                )

                summary_rows.append(row)

    summary_df = pd.DataFrame(summary_rows)

    winners_df = build_winners(summary_df)

    summary_df.to_csv(SUMMARY_PATH, index=False)
    winners_df.to_csv(WINNERS_PATH, index=False)

    report_text = build_report(
        summary_df=summary_df,
        winners_df=winners_df,
    )

    REPORT_PATH.write_text(report_text, encoding="utf-8")

    save_charts(summary_df)

    print("")
    print("=" * 78)
    print("DTE sensitivity test complete.")
    print("=" * 78)
    print("")
    print("Saved files:")
    print(f"  {SUMMARY_PATH}")
    print(f"  {WINNERS_PATH}")
    print(f"  {REPORT_PATH}")
    print(f"  {OUTPERFORMANCE_CHART_PATH}")
    print(f"  {NET_EFFECT_CHART_PATH}")
    print(f"  {TRANSACTION_COST_CHART_PATH}")
    print("")


if __name__ == "__main__":
    main()