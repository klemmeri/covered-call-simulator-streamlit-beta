"""
cost_threshold_search.py

Fine transaction-cost threshold search for the Covered Call Simulator.

Purpose
-------
The broader cost-sensitivity test showed:

    - In bearish_market, Close50 remains best even under high transaction costs.
    - In sideways_market, Close50 stops being best under high transaction costs.

This script focuses only on sideways_market and compares:

    1. hold_to_expiration
    2. close_at_50_percent_profit

Main question
-------------
At approximately what transaction-cost level does Close50 stop beating
HoldToExpiration in sideways_market?

Output files
------------
outputs/tables/comparison/cost_threshold_search_summary.csv
outputs/tables/comparison/cost_threshold_search_report.txt

Important
---------
This is a standalone diagnostic script.

It does not change main.py.
It does not change portfolio.py.
It does not change the existing adaptive rule.
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

REGIME_NAME = "sideways_market"

MANAGEMENT_RULES = [
    "hold_to_expiration",
    "close_at_50_percent_profit",
]

DISPLAY_LABELS = {
    "hold_to_expiration": "HoldToExpiration",
    "close_at_50_percent_profit": "Close50",
}

# These are designed to bracket the transition from medium to high costs.
#
# Medium tier from previous test:
#     commission = 1.00
#     slippage   = 0.02
#
# High tier from previous test:
#     commission = 2.00
#     slippage   = 0.05

COST_GRID = [
    {"cost_case": "C0.65_S0.01", "commission": 0.65, "slippage": 0.01},
    {"cost_case": "C1.00_S0.02", "commission": 1.00, "slippage": 0.02},
    {"cost_case": "C1.25_S0.025", "commission": 1.25, "slippage": 0.025},
    {"cost_case": "C1.50_S0.03", "commission": 1.50, "slippage": 0.03},
    {"cost_case": "C1.75_S0.04", "commission": 1.75, "slippage": 0.04},
    {"cost_case": "C2.00_S0.05", "commission": 2.00, "slippage": 0.05},
    {"cost_case": "C2.50_S0.06", "commission": 2.50, "slippage": 0.06},
]


# =============================================================================
# Config helpers
# =============================================================================

def safe_replace(config: SimulationConfig, **updates) -> SimulationConfig:
    """
    Replace fields in a SimulationConfig dataclass safely.

    Only fields that exist in SimulationConfig are replaced.
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


def load_sideways_config() -> SimulationConfig:
    """
    Load the sideways_market config from app.main.

    This keeps the threshold test consistent with the main simulator.
    """

    try:
        from app.main import build_base_regime_configs

        regime_configs = build_base_regime_configs()

        if REGIME_NAME not in regime_configs:
            raise KeyError(
                f"{REGIME_NAME} was not found in build_base_regime_configs()."
            )

        config = regime_configs[REGIME_NAME]

        print("Loaded sideways_market config from app.main.build_base_regime_configs().")

    except Exception as exc:
        print("")
        print("WARNING:")
        print("Could not import sideways_market config from app.main.")
        print("Using fallback SimulationConfig().")
        print("")
        print("Import error was:")
        print(f"    {exc}")
        print("")

        config = SimulationConfig()

    config = safe_replace(
        config,
        regime_name=REGIME_NAME,
        n_paths=N_PATHS,
    )

    return config


# =============================================================================
# DataFrame helpers
# =============================================================================

def get_column(df: pd.DataFrame, possible_names: list[str]) -> str:
    """
    Return the first matching column name.
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
    Return the first matching column name, or None.
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
    Run the SimulationEngine and return path-level results.
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


def summarize_results(
    path_results: pd.DataFrame,
    cost_case: str,
    commission: float,
    slippage: float,
    management_rule: str,
) -> dict:
    """
    Summarize one simulation run.
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
            "final_buy_and_hold_value",
        ],
    )

    outperformance_col = get_optional_column(
        path_results,
        [
            "outperformance",
            "Outperformance",
        ],
    )

    net_option_effect_col = get_optional_column(
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

    if outperformance_col is not None:
        outperformance = path_results[outperformance_col]
    else:
        outperformance = path_results[final_value_col] - path_results[buy_hold_col]

    summary = {
        "Cost_Case": cost_case,
        "Commission_Per_Contract": commission,
        "Slippage_Per_Share": slippage,
        "Regime": REGIME_NAME,
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

    if net_option_effect_col is not None:
        summary["Mean_Net_Option_Effect"] = path_results[net_option_effect_col].mean()
    else:
        summary["Mean_Net_Option_Effect"] = float("nan")

    if transaction_cost_col is not None:
        summary["Mean_Total_Transaction_Cost"] = path_results[transaction_cost_col].mean()
    else:
        summary["Mean_Total_Transaction_Cost"] = float("nan")

    if commission_cost_col is not None:
        summary["Mean_Total_Commission_Cost"] = path_results[commission_cost_col].mean()
    else:
        summary["Mean_Total_Commission_Cost"] = float("nan")

    if slippage_cost_col is not None:
        summary["Mean_Total_Slippage_Cost"] = path_results[slippage_cost_col].mean()
    else:
        summary["Mean_Total_Slippage_Cost"] = float("nan")

    if option_cycles_col is not None:
        summary["Mean_Option_Cycles"] = path_results[option_cycles_col].mean()
    else:
        summary["Mean_Option_Cycles"] = float("nan")

    return summary


def run_one_case(
    base_config: SimulationConfig,
    cost_case: str,
    commission: float,
    slippage: float,
    management_rule: str,
) -> dict:
    """
    Run one cost case and one management rule.
    """

    config = safe_replace(
        base_config,
        regime_name=REGIME_NAME,
        n_paths=N_PATHS,
        management_rule=management_rule,
        option_commission_per_contract=commission,
        option_slippage_per_share=slippage,
    )

    path_results = run_engine(config)

    return summarize_results(
        path_results=path_results,
        cost_case=cost_case,
        commission=commission,
        slippage=slippage,
        management_rule=management_rule,
    )


# =============================================================================
# Analysis
# =============================================================================

def build_comparison(summary_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare Close50 against HoldToExpiration for each cost case.
    """

    rows = []

    for cost_case in summary_df["Cost_Case"].unique():
        subset = summary_df[summary_df["Cost_Case"] == cost_case].copy()

        close50 = subset[
            subset["Management_Rule"] == "close_at_50_percent_profit"
        ].iloc[0]

        hold = subset[
            subset["Management_Rule"] == "hold_to_expiration"
        ].iloc[0]

        close50_minus_hold = (
            close50["Mean_Outperformance"]
            - hold["Mean_Outperformance"]
        )

        if close50_minus_hold > 0:
            winner = "Close50"
        elif close50_minus_hold < 0:
            winner = "HoldToExpiration"
        else:
            winner = "Tie"

        rows.append(
            {
                "Cost_Case": cost_case,
                "Commission_Per_Contract": close50["Commission_Per_Contract"],
                "Slippage_Per_Share": close50["Slippage_Per_Share"],
                "Close50_Mean_Outperformance": close50["Mean_Outperformance"],
                "HoldToExpiration_Mean_Outperformance": hold["Mean_Outperformance"],
                "Close50_Minus_HoldToExpiration": close50_minus_hold,
                "Winner": winner,
                "Close50_Mean_Transaction_Cost": close50[
                    "Mean_Total_Transaction_Cost"
                ],
                "HoldToExpiration_Mean_Transaction_Cost": hold[
                    "Mean_Total_Transaction_Cost"
                ],
                "Close50_Mean_Option_Cycles": close50["Mean_Option_Cycles"],
                "HoldToExpiration_Mean_Option_Cycles": hold["Mean_Option_Cycles"],
            }
        )

    comparison_df = pd.DataFrame(rows)

    comparison_df = comparison_df.sort_values(
        ["Commission_Per_Contract", "Slippage_Per_Share"]
    ).reset_index(drop=True)

    return comparison_df


def find_breakpoint(comparison_df: pd.DataFrame) -> dict:
    """
    Find the first cost case where Close50 no longer beats HoldToExpiration.
    """

    losing_rows = comparison_df[
        comparison_df["Close50_Minus_HoldToExpiration"] <= 0
    ]

    if losing_rows.empty:
        return {
            "Found_Breakpoint": False,
            "Message": (
                "Close50 beat HoldToExpiration in every tested cost case."
            ),
        }

    first_loss = losing_rows.iloc[0]

    return {
        "Found_Breakpoint": True,
        "Cost_Case": first_loss["Cost_Case"],
        "Commission_Per_Contract": first_loss["Commission_Per_Contract"],
        "Slippage_Per_Share": first_loss["Slippage_Per_Share"],
        "Close50_Minus_HoldToExpiration": first_loss[
            "Close50_Minus_HoldToExpiration"
        ],
        "Winner": first_loss["Winner"],
    }


def write_report(
    comparison_df: pd.DataFrame,
    breakpoint_info: dict,
    output_path: Path,
) -> None:
    """
    Write plain-text threshold-search report.
    """

    lines = []

    lines.append("Covered Call Simulator — Cost Threshold Search")
    lines.append("=" * 72)
    lines.append("")
    lines.append(f"Regime tested:          {REGIME_NAME}")
    lines.append(f"Paths per experiment:   {N_PATHS}")
    lines.append("Rules compared:         Close50 vs HoldToExpiration")
    lines.append("")

    lines.append("Cost Grid Results")
    lines.append("-" * 72)

    for _, row in comparison_df.iterrows():
        lines.append(
            f"{row['Cost_Case']:<14} | "
            f"commission ${row['Commission_Per_Contract']:.2f}, "
            f"slippage ${row['Slippage_Per_Share']:.3f}/share | "
            f"Close50 - Hold: "
            f"{row['Close50_Minus_HoldToExpiration']:> .6f} | "
            f"Winner: {row['Winner']}"
        )

    lines.append("")
    lines.append("Threshold Interpretation")
    lines.append("-" * 72)

    if breakpoint_info["Found_Breakpoint"]:
        lines.append(
            "Close50 first failed to beat HoldToExpiration at:"
        )
        lines.append("")
        lines.append(
            f"    Cost case:  {breakpoint_info['Cost_Case']}"
        )
        lines.append(
            f"    Commission: ${breakpoint_info['Commission_Per_Contract']:.2f} "
            "per contract"
        )
        lines.append(
            f"    Slippage:   ${breakpoint_info['Slippage_Per_Share']:.3f} "
            "per share"
        )
        lines.append(
            f"    Close50 minus HoldToExpiration: "
            f"{breakpoint_info['Close50_Minus_HoldToExpiration']:.6f}"
        )
        lines.append("")
        lines.append(
            "Practical conclusion: in sideways_market, Close50 should be used "
            "only when costs are below this region. At or above this region, "
            "lower-turnover management should be preferred."
        )
    else:
        lines.append(breakpoint_info["Message"])
        lines.append("")
        lines.append(
            "Practical conclusion: the tested cost range did not find a point "
            "where HoldToExpiration beats Close50."
        )

    lines.append("")
    lines.append("Recommended Rule Refinement")
    lines.append("-" * 72)
    lines.append(
        "Use Close50 in bearish_market regardless of tested cost tier."
    )
    lines.append(
        "Use Close50 in sideways_market only when transaction costs are not high."
    )
    lines.append(
        "Use lower-turnover management in sideways_market when costs are high."
    )

    output_path.write_text("\n".join(lines), encoding="utf-8")


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    output_dir = PROJECT_ROOT / "outputs" / "tables" / "comparison"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("")
    print("Covered Call Simulator — Cost Threshold Search")
    print("=" * 72)
    print(f"Project root:          {PROJECT_ROOT}")
    print(f"Regime tested:         {REGIME_NAME}")
    print(f"Paths per experiment:  {N_PATHS}")
    print(f"Cost cases:            {len(COST_GRID)}")
    print(f"Rules compared:        {len(MANAGEMENT_RULES)}")
    print(f"Total experiments:     {len(COST_GRID) * len(MANAGEMENT_RULES)}")
    print("")

    base_config = load_sideways_config()

    summary_rows = []
    experiment_number = 0
    total_experiments = len(COST_GRID) * len(MANAGEMENT_RULES)

    for cost_case in COST_GRID:
        case_name = cost_case["cost_case"]
        commission = cost_case["commission"]
        slippage = cost_case["slippage"]

        print("")
        print("=" * 72)
        print(
            f"Cost case: {case_name} "
            f"(commission ${commission:.2f}, "
            f"slippage ${slippage:.3f}/share)"
        )
        print("=" * 72)

        for management_rule in MANAGEMENT_RULES:
            experiment_number += 1
            label = DISPLAY_LABELS.get(management_rule, management_rule)

            print(
                f"  [{experiment_number:>2} / {total_experiments}] "
                f"{label}"
            )

            row = run_one_case(
                base_config=base_config,
                cost_case=case_name,
                commission=commission,
                slippage=slippage,
                management_rule=management_rule,
            )

            summary_rows.append(row)

    summary_df = pd.DataFrame(summary_rows)
    comparison_df = build_comparison(summary_df)
    breakpoint_info = find_breakpoint(comparison_df)

    summary_path = output_dir / "cost_threshold_search_summary.csv"
    comparison_path = output_dir / "cost_threshold_search_comparison.csv"
    report_path = output_dir / "cost_threshold_search_report.txt"

    summary_df.to_csv(summary_path, index=False)
    comparison_df.to_csv(comparison_path, index=False)

    write_report(
        comparison_df=comparison_df,
        breakpoint_info=breakpoint_info,
        output_path=report_path,
    )

    print("")
    print("=" * 72)
    print("Cost threshold search complete.")
    print("=" * 72)
    print("")
    print("Saved files:")
    print(f"  {summary_path}")
    print(f"  {comparison_path}")
    print(f"  {report_path}")
    print("")
    print("Close50 versus HoldToExpiration:")
    print("")
    print(comparison_df.to_string(index=False))
    print("")

    if breakpoint_info["Found_Breakpoint"]:
        print("Breakpoint found:")
        print(
            f"  {breakpoint_info['Cost_Case']} "
            f"commission ${breakpoint_info['Commission_Per_Contract']:.2f}, "
            f"slippage ${breakpoint_info['Slippage_Per_Share']:.3f}/share"
        )
    else:
        print("No breakpoint found in tested range.")

    print("")


if __name__ == "__main__":
    main()