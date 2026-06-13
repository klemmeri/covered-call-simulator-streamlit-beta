"""
cost_sensitivity.py

Transaction-cost sensitivity test for the Covered Call Simulator.

Purpose
-------
This script tests whether the current adaptive covered-call rule remains stable
under different commission and slippage assumptions.

Main question
-------------
At what transaction-cost level does Close50 stop being preferred in:

    1. bearish_market
    2. sideways_market

Cost tiers tested
-----------------
Low cost:
    commission = $0.65 per contract
    slippage   = $0.01 per share

Medium cost:
    commission = $1.00 per contract
    slippage   = $0.02 per share

High cost:
    commission = $2.00 per contract
    slippage   = $0.05 per share

Output files
------------
outputs/tables/comparison/cost_sensitivity_summary.csv
outputs/tables/comparison/cost_sensitivity_regime_winners.csv
outputs/tables/comparison/cost_sensitivity_close50_stability.csv
outputs/tables/comparison/cost_sensitivity_report.txt

Important
---------
This is a standalone script.

It does not replace main.py.
It does not change the normal simulator workflow.
It simply reruns the simulator under different transaction-cost assumptions.
"""

from __future__ import annotations

import sys
from dataclasses import is_dataclass, replace
from pathlib import Path

import pandas as pd


# =============================================================================
# Path setup
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

COST_TIERS = {
    "low": {
        "option_commission_per_contract": 0.65,
        "option_slippage_per_share": 0.01,
    },
    "medium": {
        "option_commission_per_contract": 1.00,
        "option_slippage_per_share": 0.02,
    },
    "high": {
        "option_commission_per_contract": 2.00,
        "option_slippage_per_share": 0.05,
    },
}

MANAGEMENT_RULES = [
    "hold_to_expiration",
    "close_at_50_percent_profit",
    "close_at_50_percent_profit_then_wait_1d",
    "close_at_50_percent_profit_then_wait_3d",
    "close_at_50_percent_profit_then_wait_5d",
    "close_at_50_percent_profit_then_wait_10d",
    "close_at_50_percent_profit_then_pullback_or_wait_2pct_10d",
    "close_at_50_percent_profit_then_pullback_or_wait_3pct_10d",
    "adaptive_close50_wait10_by_regime",
]

DISPLAY_LABELS = {
    "hold_to_expiration": "HoldToExpiration",
    "close_at_50_percent_profit": "Close50",
    "close_at_50_percent_profit_then_wait_1d": "Close50Wait1",
    "close_at_50_percent_profit_then_wait_3d": "Close50Wait3",
    "close_at_50_percent_profit_then_wait_5d": "Close50Wait5",
    "close_at_50_percent_profit_then_wait_10d": "Close50Wait10",
    "close_at_50_percent_profit_then_pullback_or_wait_2pct_10d": "Close50Pullback2PctWait10",
    "close_at_50_percent_profit_then_pullback_or_wait_3pct_10d": "Close50Pullback3PctWait10",
    "adaptive_close50_wait10_by_regime": "AdaptiveClose50Wait10",
}

FOCUS_REGIMES = [
    "bearish_market",
    "sideways_market",
]


# =============================================================================
# Configuration helpers
# =============================================================================

def safe_replace(config: SimulationConfig, **updates) -> SimulationConfig:
    """
    Replace fields in a dataclass config safely.

    Only fields that actually exist in SimulationConfig are replaced.
    This prevents crashes if SimulationConfig changes later.
    """

    if not is_dataclass(config):
        raise TypeError("SimulationConfig must be a dataclass.")

    valid_fields = set(config.__dataclass_fields__.keys())

    filtered_updates = {
        key: value
        for key, value in updates.items()
        if key in valid_fields
    }

    return replace(config, **filtered_updates)


def load_regime_configs() -> dict[str, SimulationConfig]:
    """
    Load the six market-regime configs from app.main.

    This keeps this sensitivity test consistent with the main simulator.
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
        print("Using fallback regime configs instead.")
        print("")
        print("Import error was:")
        print(f"    {exc}")
        print("")
        print(
            "If this warning appears, the sensitivity test may not exactly "
            "match the regime definitions in main.py."
        )
        print("")

        regime_names = [
            "baseline",
            "sideways_market",
            "bullish_market",
            "bearish_market",
            "high_volatility",
            "low_volatility",
        ]

        regime_configs = {
            regime_name: safe_replace(
                SimulationConfig(),
                regime_name=regime_name,
                n_paths=N_PATHS,
            )
            for regime_name in regime_names
        }

    cleaned_configs = {}

    for regime_name, config in regime_configs.items():
        cleaned_configs[regime_name] = safe_replace(
            config,
            regime_name=regime_name,
            n_paths=N_PATHS,
        )

    return cleaned_configs


# =============================================================================
# DataFrame column helpers
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

    If none are present, return None.
    """

    for name in possible_names:
        if name in df.columns:
            return name

    return None


# =============================================================================
# Simulation helpers
# =============================================================================

def run_engine(config: SimulationConfig) -> pd.DataFrame:
    """
    Run the SimulationEngine and return the path-level DataFrame.

    This handles either design:

        1. engine.run() returns the DataFrame directly
        2. engine.run() stores the DataFrame in engine.path_results_df
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
    cost_tier: str,
    regime_name: str,
    management_rule: str,
    commission: float,
    slippage: float,
) -> dict:
    """
    Summarize one simulation run into one row.

    Your current simulator uses these key columns:

        final_covered_call_value
        final_buy_and_hold_value
        outperformance
        net_option_effect
        total_transaction_cost
        total_commission_cost
        total_slippage_cost
    """

    final_value_col = get_column(
        path_results,
        [
            "final_covered_call_value",
            "final_portfolio_value",
            "Final_Portfolio_Value",
            "ending_portfolio_value",
            "Ending_Portfolio_Value",
        ],
    )

    buy_hold_col = get_column(
        path_results,
        [
            "final_buy_and_hold_value",
            "buy_and_hold_final_value",
            "Buy_And_Hold_Final_Value",
            "final_buy_and_hold_value",
            "Final_Buy_And_Hold_Value",
        ],
    )

    outperformance_col = get_optional_column(
        path_results,
        [
            "outperformance",
            "Outperformance",
            "mean_outperformance",
            "Mean_Outperformance",
        ],
    )

    option_effect_col = get_optional_column(
        path_results,
        [
            "net_option_effect",
            "Net_Option_Effect",
            "total_net_option_effect",
            "Total_Net_Option_Effect",
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

    gross_premium_col = get_optional_column(
        path_results,
        [
            "total_gross_premium_collected",
            "Total_Gross_Premium_Collected",
            "total_gross_premiums",
            "Total_Gross_Premiums",
            "total_premium_collected",
        ],
    )

    gross_buyback_col = get_optional_column(
        path_results,
        [
            "total_gross_buyback_cost",
            "Total_Gross_Buyback_Cost",
            "total_gross_buybacks",
            "Total_Gross_Buybacks",
            "total_buyback_cost",
        ],
    )

    assignments_col = get_optional_column(
        path_results,
        [
            "assignments",
            "Assignments",
            "total_assignments",
            "Total_Assignments",
        ],
    )

    option_cycles_col = get_optional_column(
        path_results,
        [
            "option_cycles",
            "Option_Cycles",
            "total_option_cycles",
            "Total_Option_Cycles",
        ],
    )

    if outperformance_col is not None:
        outperformance = path_results[outperformance_col]
    else:
        outperformance = path_results[final_value_col] - path_results[buy_hold_col]

    summary = {
        "Cost_Tier": cost_tier,
        "Commission_Per_Contract": commission,
        "Slippage_Per_Share": slippage,
        "Regime": regime_name,
        "Management_Rule": management_rule,
        "Display_Label": DISPLAY_LABELS.get(management_rule, management_rule),
        "Mean_Final_Covered_Call_Value": path_results[final_value_col].mean(),
        "Median_Final_Covered_Call_Value": path_results[final_value_col].median(),
        "Mean_Final_Buy_And_Hold_Value": path_results[buy_hold_col].mean(),
        "Median_Final_Buy_And_Hold_Value": path_results[buy_hold_col].median(),
        "Mean_Outperformance": outperformance.mean(),
        "Median_Outperformance": outperformance.median(),
        "Percent_Outperforming_Buy_And_Hold": (outperformance > 0).mean() * 100,
    }

    if option_effect_col is not None:
        summary["Mean_Net_Option_Effect"] = path_results[option_effect_col].mean()
    else:
        summary["Mean_Net_Option_Effect"] = float("nan")

    if transaction_cost_col is not None:
        summary["Mean_Total_Transaction_Cost"] = path_results[
            transaction_cost_col
        ].mean()
    else:
        summary["Mean_Total_Transaction_Cost"] = float("nan")

    if commission_cost_col is not None:
        summary["Mean_Total_Commission_Cost"] = path_results[
            commission_cost_col
        ].mean()
    else:
        summary["Mean_Total_Commission_Cost"] = float("nan")

    if slippage_cost_col is not None:
        summary["Mean_Total_Slippage_Cost"] = path_results[
            slippage_cost_col
        ].mean()
    else:
        summary["Mean_Total_Slippage_Cost"] = float("nan")

    if gross_premium_col is not None:
        summary["Mean_Total_Gross_Premiums"] = path_results[
            gross_premium_col
        ].mean()
    else:
        summary["Mean_Total_Gross_Premiums"] = float("nan")

    if gross_buyback_col is not None:
        summary["Mean_Total_Gross_Buybacks"] = path_results[
            gross_buyback_col
        ].mean()
    else:
        summary["Mean_Total_Gross_Buybacks"] = float("nan")

    if assignments_col is not None:
        summary["Mean_Assignments"] = path_results[assignments_col].mean()
    else:
        summary["Mean_Assignments"] = float("nan")

    if option_cycles_col is not None:
        summary["Mean_Option_Cycles"] = path_results[option_cycles_col].mean()
    else:
        summary["Mean_Option_Cycles"] = float("nan")

    return summary


def run_one_experiment(
    base_config: SimulationConfig,
    cost_tier: str,
    commission: float,
    slippage: float,
    regime_name: str,
    management_rule: str,
) -> dict:
    """
    Run one cost-tier / regime / management-rule experiment.
    """

    config = safe_replace(
        base_config,
        n_paths=N_PATHS,
        regime_name=regime_name,
        management_rule=management_rule,
        option_commission_per_contract=commission,
        option_slippage_per_share=slippage,
    )

    path_results = run_engine(config)

    return summarize_path_results(
        path_results=path_results,
        cost_tier=cost_tier,
        regime_name=regime_name,
        management_rule=management_rule,
        commission=commission,
        slippage=slippage,
    )


# =============================================================================
# Analysis logic
# =============================================================================

def build_regime_winners(summary_df: pd.DataFrame) -> pd.DataFrame:
    """
    Find the best management rule for each cost tier and market regime.
    """

    idx = (
        summary_df
        .groupby(["Cost_Tier", "Regime"])["Mean_Outperformance"]
        .idxmax()
    )

    winners_df = (
        summary_df
        .loc[idx]
        .copy()
        .sort_values(["Cost_Tier", "Regime"])
        .reset_index(drop=True)
    )

    winners_df = winners_df.rename(
        columns={
            "Management_Rule": "Winning_Management_Rule",
            "Display_Label": "Winning_Display_Label",
            "Mean_Outperformance": "Winning_Mean_Outperformance",
            "Median_Outperformance": "Winning_Median_Outperformance",
            "Mean_Net_Option_Effect": "Winning_Mean_Net_Option_Effect",
            "Mean_Total_Transaction_Cost": "Winning_Mean_Total_Transaction_Cost",
            "Mean_Total_Commission_Cost": "Winning_Mean_Total_Commission_Cost",
            "Mean_Total_Slippage_Cost": "Winning_Mean_Total_Slippage_Cost",
        }
    )

    return winners_df


def analyze_close50_stability(summary_df: pd.DataFrame) -> pd.DataFrame:
    """
    Determine whether Close50 remains the winner in bearish and sideways regimes.
    """

    rows = []

    for cost_tier in COST_TIERS.keys():
        for regime_name in FOCUS_REGIMES:
            subset = summary_df[
                (summary_df["Cost_Tier"] == cost_tier)
                & (summary_df["Regime"] == regime_name)
            ].copy()

            if subset.empty:
                continue

            subset["Rank_By_Mean_Outperformance"] = (
                subset["Mean_Outperformance"]
                .rank(method="min", ascending=False)
                .astype(int)
            )

            winner_row = subset.loc[subset["Mean_Outperformance"].idxmax()]

            close50_rows = subset[
                subset["Management_Rule"] == "close_at_50_percent_profit"
            ]

            if close50_rows.empty:
                raise RuntimeError(
                    f"Close50 result missing for {cost_tier}, {regime_name}."
                )

            close50_row = close50_rows.iloc[0]

            rows.append(
                {
                    "Cost_Tier": cost_tier,
                    "Regime": regime_name,
                    "Close50_Mean_Outperformance": close50_row[
                        "Mean_Outperformance"
                    ],
                    "Close50_Median_Outperformance": close50_row[
                        "Median_Outperformance"
                    ],
                    "Close50_Percent_Outperforming_Buy_And_Hold": close50_row[
                        "Percent_Outperforming_Buy_And_Hold"
                    ],
                    "Close50_Mean_Net_Option_Effect": close50_row[
                        "Mean_Net_Option_Effect"
                    ],
                    "Close50_Mean_Total_Transaction_Cost": close50_row[
                        "Mean_Total_Transaction_Cost"
                    ],
                    "Close50_Mean_Total_Commission_Cost": close50_row[
                        "Mean_Total_Commission_Cost"
                    ],
                    "Close50_Mean_Total_Slippage_Cost": close50_row[
                        "Mean_Total_Slippage_Cost"
                    ],
                    "Close50_Mean_Option_Cycles": close50_row[
                        "Mean_Option_Cycles"
                    ],
                    "Winning_Rule": winner_row["Management_Rule"],
                    "Winning_Label": winner_row["Display_Label"],
                    "Winning_Mean_Outperformance": winner_row[
                        "Mean_Outperformance"
                    ],
                    "Winning_Median_Outperformance": winner_row[
                        "Median_Outperformance"
                    ],
                    "Winning_Mean_Total_Transaction_Cost": winner_row[
                        "Mean_Total_Transaction_Cost"
                    ],
                    "Close50_Rank": close50_row[
                        "Rank_By_Mean_Outperformance"
                    ],
                    "Close50_Is_Winner": (
                        winner_row["Management_Rule"]
                        == "close_at_50_percent_profit"
                    ),
                    "Close50_Gap_To_Winner": (
                        close50_row["Mean_Outperformance"]
                        - winner_row["Mean_Outperformance"]
                    ),
                }
            )

    return pd.DataFrame(rows)


# =============================================================================
# Report writer
# =============================================================================

def write_report(
    summary_df: pd.DataFrame,
    winners_df: pd.DataFrame,
    close50_stability_df: pd.DataFrame,
    output_path: Path,
) -> None:
    """
    Write the plain-text transaction-cost sensitivity report.
    """

    lines = []

    lines.append("Covered Call Simulator — Transaction-Cost Sensitivity Report")
    lines.append("=" * 72)
    lines.append("")
    lines.append(f"Paths per experiment: {N_PATHS}")
    lines.append(f"Cost tiers tested:     {len(COST_TIERS)}")
    lines.append(f"Market regimes:        {summary_df['Regime'].nunique()}")
    lines.append(f"Management rules:      {len(MANAGEMENT_RULES)}")
    lines.append(f"Total experiments:     {len(summary_df)}")
    lines.append("")

    lines.append("Cost Tiers")
    lines.append("-" * 72)

    for cost_tier, settings in COST_TIERS.items():
        lines.append(
            f"{cost_tier:<8} "
            f"commission = ${settings['option_commission_per_contract']:.2f} "
            f"per contract, "
            f"slippage = ${settings['option_slippage_per_share']:.2f} "
            f"per share"
        )

    lines.append("")
    lines.append("Regime Winners by Cost Tier")
    lines.append("-" * 72)

    for _, row in winners_df.iterrows():
        lines.append(
            f"{row['Cost_Tier']:<8} | "
            f"{row['Regime']:<18} | "
            f"{row['Winning_Display_Label']:<30} | "
            f"Mean outperformance: ${row['Winning_Mean_Outperformance']:>10,.2f} | "
            f"Mean transaction cost: "
            f"${row['Winning_Mean_Total_Transaction_Cost']:>8,.2f}"
        )

    lines.append("")
    lines.append("Close50 Stability in Bearish and Sideways Markets")
    lines.append("-" * 72)

    for _, row in close50_stability_df.iterrows():
        status = "WINNER" if row["Close50_Is_Winner"] else "NOT WINNER"

        lines.append(
            f"{row['Cost_Tier']:<8} | "
            f"{row['Regime']:<18} | "
            f"Close50 rank: {int(row['Close50_Rank'])} | "
            f"{status:<10} | "
            f"Close50 mean outperformance: "
            f"${row['Close50_Mean_Outperformance']:>10,.2f} | "
            f"Winner: {row['Winning_Label']:<30} | "
            f"Gap to winner: ${row['Close50_Gap_To_Winner']:>10,.2f}"
        )

    lines.append("")
    lines.append("Practical Interpretation")
    lines.append("-" * 72)

    failed_rows = close50_stability_df[
        close50_stability_df["Close50_Is_Winner"] == False
    ]

    if failed_rows.empty:
        lines.append(
            "Close50 remained the top rule in both bearish_market and "
            "sideways_market across all tested transaction-cost tiers."
        )
        lines.append("")
        lines.append(
            "Conclusion: the current adaptive rule remains stable under the "
            "low, medium, and high transaction-cost assumptions tested here."
        )
    else:
        lines.append(
            "Close50 stopped being the top rule in at least one focus regime."
        )
        lines.append("")

        for _, row in failed_rows.iterrows():
            lines.append(
                f"- In {row['Regime']} under {row['Cost_Tier']} costs, "
                f"Close50 ranked #{int(row['Close50_Rank'])}. "
                f"The winning rule was {row['Winning_Label']}. "
                f"Close50 lagged by "
                f"${abs(row['Close50_Gap_To_Winner']):,.2f}."
            )

        lines.append("")
        lines.append(
            "Conclusion: if this result persists under a larger robustness run, "
            "the adaptive rule may need a transaction-cost-aware adjustment."
        )

    lines.append("")
    lines.append("Recommended Next Step")
    lines.append("-" * 72)
    lines.append(
        "If Close50 narrowly wins or narrowly loses in bearish_market or "
        "sideways_market, rerun this script with N_PATHS = 1000 before changing "
        "the adaptive rule."
    )

    output_path.write_text("\n".join(lines), encoding="utf-8")


# =============================================================================
# Main script
# =============================================================================

def main() -> None:
    output_dir = PROJECT_ROOT / "outputs" / "tables" / "comparison"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("")
    print("Covered Call Simulator — Transaction-Cost Sensitivity Test")
    print("=" * 72)
    print(f"Project root:          {PROJECT_ROOT}")
    print(f"Paths per experiment:  {N_PATHS}")
    print(f"Cost tiers:            {len(COST_TIERS)}")
    print(f"Management rules:      {len(MANAGEMENT_RULES)}")
    print("")

    regime_configs = load_regime_configs()
    regime_names = list(regime_configs.keys())

    print("Market regimes loaded:")
    for regime_name in regime_names:
        print(f"  {regime_name}")

    total_experiments = (
        len(COST_TIERS)
        * len(regime_names)
        * len(MANAGEMENT_RULES)
    )

    print("")
    print(f"Total experiments:     {total_experiments}")
    print("")

    summary_rows = []
    experiment_counter = 0

    for cost_tier, cost_settings in COST_TIERS.items():
        commission = cost_settings["option_commission_per_contract"]
        slippage = cost_settings["option_slippage_per_share"]

        print("")
        print("=" * 72)
        print(
            f"Running cost tier: {cost_tier} "
            f"(commission ${commission:.2f}, slippage ${slippage:.2f}/share)"
        )
        print("=" * 72)

        for regime_name, base_config in regime_configs.items():
            print("")
            print(f"Regime: {regime_name}")

            for management_rule in MANAGEMENT_RULES:
                experiment_counter += 1
                label = DISPLAY_LABELS.get(management_rule, management_rule)

                print(
                    f"  [{experiment_counter:>3} / {total_experiments}] "
                    f"{label}"
                )

                row = run_one_experiment(
                    base_config=base_config,
                    cost_tier=cost_tier,
                    commission=commission,
                    slippage=slippage,
                    regime_name=regime_name,
                    management_rule=management_rule,
                )

                summary_rows.append(row)

    summary_df = pd.DataFrame(summary_rows)

    winners_df = build_regime_winners(summary_df)
    close50_stability_df = analyze_close50_stability(summary_df)

    summary_path = output_dir / "cost_sensitivity_summary.csv"
    winners_path = output_dir / "cost_sensitivity_regime_winners.csv"
    close50_path = output_dir / "cost_sensitivity_close50_stability.csv"
    report_path = output_dir / "cost_sensitivity_report.txt"

    summary_df.to_csv(summary_path, index=False)
    winners_df.to_csv(winners_path, index=False)
    close50_stability_df.to_csv(close50_path, index=False)

    write_report(
        summary_df=summary_df,
        winners_df=winners_df,
        close50_stability_df=close50_stability_df,
        output_path=report_path,
    )

    print("")
    print("=" * 72)
    print("Cost sensitivity test complete.")
    print("=" * 72)
    print("")
    print("Saved files:")
    print(f"  {summary_path}")
    print(f"  {winners_path}")
    print(f"  {close50_path}")
    print(f"  {report_path}")
    print("")
    print("Close50 stability check:")
    print("")
    print(close50_stability_df.to_string(index=False))
    print("")


if __name__ == "__main__":
    main()