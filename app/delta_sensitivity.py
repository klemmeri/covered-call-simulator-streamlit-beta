"""
delta_sensitivity.py

Delta sensitivity test for the Covered Call Simulator.

This script tests whether the preferred covered-call management rule changes
when the target short-call delta changes.

It compares selected management rules across:

    6 market regimes
    5 target delta values
    6 management rules

Total experiments:

    6 x 5 x 6 = 180 experiments

This script does not replace app/main.py.
It is a standalone research script, similar to dte_sensitivity.py.

Outputs are saved to:

    outputs/tables/comparison/delta_sensitivity_summary.csv
    outputs/tables/comparison/delta_sensitivity_winners.csv
    outputs/tables/comparison/delta_sensitivity_report.txt

    outputs/charts/comparison/delta_sensitivity_mean_outperformance.png
    outputs/charts/comparison/delta_sensitivity_net_option_effect.png
    outputs/charts/comparison/delta_sensitivity_transaction_cost.png
"""

import copy
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# =============================================================================
# Import project modules
# =============================================================================

CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import SimulationConfig
from app.simulator import SimulationEngine


# =============================================================================
# User settings
# =============================================================================

N_PATHS = 250

DELTA_VALUES = [
    0.20,
    0.25,
    0.30,
    0.35,
    0.40,
]

REGIME_CONFIGS = {
    "baseline": {
        "annual_return": 0.08,
        "annual_volatility": 0.25,
    },
    "sideways_market": {
        "annual_return": 0.00,
        "annual_volatility": 0.15,
    },
    "bullish_market": {
        "annual_return": 0.18,
        "annual_volatility": 0.22,
    },
    "bearish_market": {
        "annual_return": -0.12,
        "annual_volatility": 0.30,
    },
    "high_volatility": {
        "annual_return": 0.08,
        "annual_volatility": 0.45,
    },
    "low_volatility": {
        "annual_return": 0.06,
        "annual_volatility": 0.12,
    },
}

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
    "AdaptiveRegimeDTECost": {
        "management_rule": "adaptive_by_regime_dte_cost",
        "wait_days_after_profit_close": 0,
        "pullback_fraction_after_profit_close": 0.0,
        "max_wait_days_after_profit_close": 0,
        "adaptive_wait_days_after_profit_close": 10,
    },
}

REGIME_ORDER = list(REGIME_CONFIGS.keys())
RULE_ORDER = list(RULE_CONFIGS.keys())


# =============================================================================
# Output paths
# =============================================================================

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "comparison"
OUTPUT_CHART_DIR = PROJECT_ROOT / "outputs" / "charts" / "comparison"

SUMMARY_PATH = OUTPUT_TABLE_DIR / "delta_sensitivity_summary.csv"
WINNERS_PATH = OUTPUT_TABLE_DIR / "delta_sensitivity_winners.csv"
REPORT_PATH = OUTPUT_TABLE_DIR / "delta_sensitivity_report.txt"

OUTPERFORMANCE_CHART_PATH = (
    OUTPUT_CHART_DIR / "delta_sensitivity_mean_outperformance.png"
)
NET_EFFECT_CHART_PATH = (
    OUTPUT_CHART_DIR / "delta_sensitivity_net_option_effect.png"
)
TRANSACTION_COST_CHART_PATH = (
    OUTPUT_CHART_DIR / "delta_sensitivity_transaction_cost.png"
)


# =============================================================================
# Helpers
# =============================================================================

def clone_config(base_config: SimulationConfig, **updates) -> SimulationConfig:
    """
    Copy a SimulationConfig and update selected fields.
    """

    config = copy.deepcopy(base_config)

    for key, value in updates.items():
        if not hasattr(config, key):
            raise AttributeError(
                f"SimulationConfig has no field named '{key}'."
            )
        setattr(config, key, value)

    return config


def get_metric(df: pd.DataFrame, column_name: str) -> float:
    """
    Safely get the mean of a numeric result column.
    """

    if column_name not in df.columns:
        return float("nan")

    values = pd.to_numeric(df[column_name], errors="coerce")

    if values.dropna().empty:
        return float("nan")

    return float(values.mean())


def format_decimal(value: object, digits: int = 4) -> str:
    """
    Format decimal values.
    """

    value = pd.to_numeric(value, errors="coerce")

    if pd.isna(value):
        return "NA"

    return f"{float(value):,.{digits}f}"


def format_currency(value: object) -> str:
    """
    Format dollar values.
    """

    value = pd.to_numeric(value, errors="coerce")

    if pd.isna(value):
        return "NA"

    return f"${float(value):,.2f}"


# =============================================================================
# Simulation
# =============================================================================

def build_config(
    regime_name: str,
    target_delta: float,
    rule_label: str,
) -> SimulationConfig:
    """
    Build one simulation config.
    """

    base_config = SimulationConfig()

    regime_settings = REGIME_CONFIGS[regime_name]
    rule_settings = RULE_CONFIGS[rule_label]

    config = clone_config(
        base_config,
        n_paths=N_PATHS,
        regime_name=regime_name,
        target_delta=target_delta,
        annual_return=regime_settings["annual_return"],
        annual_volatility=regime_settings["annual_volatility"],
        **rule_settings,
    )

    return config


def run_single_experiment(
    regime_name: str,
    target_delta: float,
    rule_label: str,
) -> dict:
    """
    Run one regime/delta/rule experiment and return summary metrics.
    """

    experiment_name = (
        f"{regime_name}__delta_{target_delta:.2f}__{rule_label}"
    )

    print("=" * 100)
    print(f"Running experiment: {experiment_name}")
    print("=" * 100)

    config = build_config(
        regime_name=regime_name,
        target_delta=target_delta,
        rule_label=rule_label,
    )

    engine = SimulationEngine(config)
    path_results_df = engine.run()

    summary = {
        "Regime": regime_name,
        "Target_Delta": target_delta,
        "Rule_Label": rule_label,
        "Management_Rule": config.management_rule,
        "N_Paths": config.n_paths,
        "Mean_Outperformance": get_metric(
            path_results_df,
            "outperformance",
        ),
        "Mean_Net_Option_Effect": get_metric(
            path_results_df,
            "net_option_effect",
        ),
        "Mean_Total_Transaction_Cost": get_metric(
            path_results_df,
            "total_transaction_cost",
        ),
        "Mean_Total_Commission_Cost": get_metric(
            path_results_df,
            "total_commission_cost",
        ),
        "Mean_Total_Slippage_Cost": get_metric(
            path_results_df,
            "total_slippage_cost",
        ),
        "Mean_Option_Cycles": get_metric(
            path_results_df,
            "option_cycles",
        ),
        "Mean_Assignments": get_metric(
            path_results_df,
            "assignments",
        ),
    }

    return summary


def run_delta_sensitivity() -> pd.DataFrame:
    """
    Run the full delta sensitivity test.
    """

    rows = []

    total_experiments = (
        len(REGIME_ORDER)
        * len(DELTA_VALUES)
        * len(RULE_ORDER)
    )

    print("")
    print("=" * 100)
    print("COVERED CALL SIMULATOR - DELTA SENSITIVITY TEST")
    print("=" * 100)
    print(f"Paths per experiment: {N_PATHS}")
    print(f"Delta values:          {DELTA_VALUES}")
    print(f"Total experiments:     {total_experiments}")
    print("=" * 100)
    print("")

    experiment_count = 0

    for regime_name in REGIME_ORDER:
        for target_delta in DELTA_VALUES:
            for rule_label in RULE_ORDER:
                experiment_count += 1

                print(
                    f"Progress: {experiment_count} of {total_experiments}"
                )

                summary = run_single_experiment(
                    regime_name=regime_name,
                    target_delta=target_delta,
                    rule_label=rule_label,
                )

                rows.append(summary)

    summary_df = pd.DataFrame(rows)

    summary_df["Regime"] = pd.Categorical(
        summary_df["Regime"],
        categories=REGIME_ORDER,
        ordered=True,
    )

    summary_df["Rule_Label"] = pd.Categorical(
        summary_df["Rule_Label"],
        categories=RULE_ORDER,
        ordered=True,
    )

    summary_df = summary_df.sort_values(
        ["Regime", "Target_Delta", "Rule_Label"]
    ).reset_index(drop=True)

    return summary_df


# =============================================================================
# Winners and report
# =============================================================================

def build_winners_table(summary_df: pd.DataFrame) -> pd.DataFrame:
    """
    Find the best rule for each regime and target delta.
    """

    rows = []

    grouped = summary_df.groupby(
        ["Regime", "Target_Delta"],
        observed=False,
    )

    for (regime_name, target_delta), group_df in grouped:
        group_df = group_df.copy()
        group_df["Mean_Outperformance"] = pd.to_numeric(
            group_df["Mean_Outperformance"],
            errors="coerce",
        )

        group_df = group_df.dropna(subset=["Mean_Outperformance"])

        if group_df.empty:
            continue

        sorted_df = group_df.sort_values(
            "Mean_Outperformance",
            ascending=False,
        ).reset_index(drop=True)

        best = sorted_df.iloc[0]

        if len(sorted_df) > 1:
            second = sorted_df.iloc[1]
            second_label = second["Rule_Label"]
            second_outperformance = second["Mean_Outperformance"]
            edge = (
                best["Mean_Outperformance"]
                - second["Mean_Outperformance"]
            )
        else:
            second_label = ""
            second_outperformance = float("nan")
            edge = float("nan")

        rows.append(
            {
                "Regime": regime_name,
                "Target_Delta": target_delta,
                "Best_Rule_Label": best["Rule_Label"],
                "Best_Mean_Outperformance": best[
                    "Mean_Outperformance"
                ],
                "Second_Best_Rule_Label": second_label,
                "Second_Best_Mean_Outperformance": second_outperformance,
                "Outperformance_Edge": edge,
                "Best_Mean_Net_Option_Effect": best[
                    "Mean_Net_Option_Effect"
                ],
                "Best_Mean_Total_Transaction_Cost": best[
                    "Mean_Total_Transaction_Cost"
                ],
                "Best_Mean_Option_Cycles": best[
                    "Mean_Option_Cycles"
                ],
                "Best_Mean_Assignments": best[
                    "Mean_Assignments"
                ],
            }
        )

    winners_df = pd.DataFrame(rows)

    winners_df["Regime"] = pd.Categorical(
        winners_df["Regime"],
        categories=REGIME_ORDER,
        ordered=True,
    )

    winners_df = winners_df.sort_values(
        ["Regime", "Target_Delta"]
    ).reset_index(drop=True)

    return winners_df


def build_decision_matrix(winners_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build regime x delta matrix of winning labels.
    """

    matrix = winners_df.pivot(
        index="Regime",
        columns="Target_Delta",
        values="Best_Rule_Label",
    )

    matrix = matrix.reindex(REGIME_ORDER)
    matrix = matrix.reindex(columns=DELTA_VALUES)

    return matrix


def build_report(
    summary_df: pd.DataFrame,
    winners_df: pd.DataFrame,
) -> str:
    """
    Build a plain-text delta sensitivity report.
    """

    matrix = build_decision_matrix(winners_df)

    lines = []

    lines.append("COVERED CALL SIMULATOR - DELTA SENSITIVITY REPORT")
    lines.append("=" * 100)
    lines.append("")
    lines.append(f"Paths per experiment: {N_PATHS}")
    lines.append(f"Delta values tested:  {DELTA_VALUES}")
    lines.append(f"Summary file:         {SUMMARY_PATH}")
    lines.append(f"Winners file:         {WINNERS_PATH}")
    lines.append("")

    lines.append("-" * 100)
    lines.append("Decision map: best rule by regime and target delta")
    lines.append("-" * 100)
    lines.append("")

    lines.append(matrix.to_string())
    lines.append("")

    lines.append("-" * 100)
    lines.append("Detailed winners")
    lines.append("-" * 100)
    lines.append("")

    for _, row in winners_df.iterrows():
        lines.append(
            f"{row['Regime']:<18} "
            f"Delta={float(row['Target_Delta']):.2f} | "
            f"Best={row['Best_Rule_Label']:<32} | "
            f"Outperf={format_decimal(row['Best_Mean_Outperformance'])} | "
            f"Second={row['Second_Best_Rule_Label']:<32} | "
            f"Edge={format_decimal(row['Outperformance_Edge'])} | "
            f"Net option={format_currency(row['Best_Mean_Net_Option_Effect'])} | "
            f"Cost={format_currency(row['Best_Mean_Total_Transaction_Cost'])}"
        )

    lines.append("")
    lines.append("=" * 100)
    lines.append("Interpretation guide")
    lines.append("=" * 100)
    lines.append("")
    lines.append(
        "This test asks whether the preferred covered-call management rule "
        "changes as the target short-call delta changes."
    )
    lines.append("")
    lines.append(
        "Lower deltas are farther out of the money. They usually collect less "
        "premium but leave more upside room."
    )
    lines.append("")
    lines.append(
        "Higher deltas are closer to the money. They usually collect more "
        "premium but create more assignment risk and more upside limitation."
    )
    lines.append("")
    lines.append(
        "If the same rule wins across most deltas in a regime, that regime is "
        "delta-stable."
    )
    lines.append("")
    lines.append(
        "If the winning rule changes with delta, then target_delta should be "
        "included in the adaptive decision map."
    )
    lines.append("")
    lines.append(
        "Small edges should not be overinterpreted. Use the edge column to "
        "separate meaningful differences from simulation noise."
    )

    return "\n".join(lines)


# =============================================================================
# Charts
# =============================================================================

def save_line_chart(
    summary_df: pd.DataFrame,
    metric: str,
    title: str,
    ylabel: str,
    output_path: Path,
) -> None:
    """
    Save a line chart for each regime and rule combination.
    """

    plot_df = summary_df.copy()
    plot_df[metric] = pd.to_numeric(plot_df[metric], errors="coerce")
    plot_df = plot_df.dropna(subset=[metric])

    if plot_df.empty:
        return

    fig, ax = plt.subplots(figsize=(14, 8))

    for regime_name in REGIME_ORDER:
        for rule_label in RULE_ORDER:
            subset = plot_df[
                (plot_df["Regime"].astype(str) == regime_name)
                & (plot_df["Rule_Label"].astype(str) == rule_label)
            ].copy()

            if subset.empty:
                continue

            subset = subset.sort_values("Target_Delta")

            line_label = f"{regime_name} - {rule_label}"

            ax.plot(
                subset["Target_Delta"],
                subset[metric],
                marker="o",
                linewidth=1,
                label=line_label,
            )

    ax.axhline(0, linewidth=1)
    ax.set_title(title)
    ax.set_xlabel("Target Call Delta")
    ax.set_ylabel(ylabel)
    ax.legend(fontsize=7, ncol=2)

    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()


def save_charts(summary_df: pd.DataFrame) -> None:
    """
    Save delta sensitivity charts.
    """

    save_line_chart(
        summary_df=summary_df,
        metric="Mean_Outperformance",
        title="Delta Sensitivity - Mean Outperformance",
        ylabel="Mean Outperformance",
        output_path=OUTPERFORMANCE_CHART_PATH,
    )

    save_line_chart(
        summary_df=summary_df,
        metric="Mean_Net_Option_Effect",
        title="Delta Sensitivity - Mean Net Option Effect",
        ylabel="Mean Net Option Effect",
        output_path=NET_EFFECT_CHART_PATH,
    )

    save_line_chart(
        summary_df=summary_df,
        metric="Mean_Total_Transaction_Cost",
        title="Delta Sensitivity - Mean Transaction Cost",
        ylabel="Mean Transaction Cost",
        output_path=TRANSACTION_COST_CHART_PATH,
    )


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_CHART_DIR.mkdir(parents=True, exist_ok=True)

    summary_df = run_delta_sensitivity()
    winners_df = build_winners_table(summary_df)

    summary_df.to_csv(SUMMARY_PATH, index=False)
    winners_df.to_csv(WINNERS_PATH, index=False)

    report_text = build_report(summary_df, winners_df)
    REPORT_PATH.write_text(report_text, encoding="utf-8")

    save_charts(summary_df)

    print("")
    print("=" * 100)
    print("Delta sensitivity test complete.")
    print("=" * 100)
    print("")
    print("Saved files:")
    print(f"  {SUMMARY_PATH}")
    print(f"  {WINNERS_PATH}")
    print(f"  {REPORT_PATH}")
    print(f"  {OUTPERFORMANCE_CHART_PATH}")
    print(f"  {NET_EFFECT_CHART_PATH}")
    print(f"  {TRANSACTION_COST_CHART_PATH}")
    print("")
    print("Done.")
    print("")


if __name__ == "__main__":
    main()