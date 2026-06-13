"""
reports.py

Reporting utilities for the Covered Call Simulator.

Supports management-rule sensitivity tests:

    1. hold_to_expiration

    2. close_at_50_percent_profit

    3. close_at_50_percent_profit_then_wait_Nd

       Example:
           close_at_50_percent_profit_then_wait_10d

    4. close_at_50_percent_profit_then_pullback_or_wait_Xpct_Nd

       Example:
           close_at_50_percent_profit_then_pullback_or_wait_2pct_10d
           close_at_50_percent_profit_then_pullback_or_wait_3pct_10d

    5. adaptive_close50_wait10_by_regime

       Original adaptive rule:
           bearish_market and sideways_market:
               close_at_50_percent_profit

           all other regimes:
               close_at_50_percent_profit_then_wait_10d

    6. adaptive_close50_wait10_by_regime_and_cost

       Cost-aware adaptive rule:
           bearish_market:
               close_at_50_percent_profit

           sideways_market:
               if transaction costs are high:
                   hold_to_expiration
               otherwise:
                   close_at_50_percent_profit

           all other regimes:
               close_at_50_percent_profit_then_wait_10d

    7. adaptive_by_regime_dte_cost

       Simplified DTE-aware, cost-aware adaptive rule:
           bearish_market:
               close_at_50_percent_profit

           sideways_market:
               short DTE:
                   hold_to_expiration
               longer DTE:
                   close_at_50_percent_profit unless costs are high

           baseline, bullish_market, high_volatility, low_volatility:
               DTE < 45:
                   close_at_50_percent_profit_then_wait_10d
               DTE >= 45:
                   hold_to_expiration

Transaction-cost reporting:

    This version summarizes:

        total_transaction_cost
        total_commission_cost
        total_slippage_cost
        total_gross_premium_collected
        total_gross_buyback_cost

Main output files:

    outputs/tables/path_level/*_path_level_results.csv
    outputs/tables/path_level/*_path_level_summary.csv
    outputs/tables/cycle_level/*_cycle_level_summary.csv

    outputs/tables/comparison/experiment_comparison.csv
    outputs/tables/comparison/cycle_level_comparison.csv
    outputs/tables/comparison/management_rule_comparison.csv
    outputs/tables/comparison/management_rule_decision_summary.csv
    outputs/tables/comparison/strategy_map.csv
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import re

import matplotlib.pyplot as plt
import pandas as pd


# ---------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------

OUTPERFORMANCE_MATERIALITY_THRESHOLD = 0.005

RULE_DISPLAY_ORDER = [
    "hold_to_expiration",
    "close_at_50_percent_profit",
    "close_at_50_percent_profit_then_wait_1d",
    "close_at_50_percent_profit_then_wait_3d",
    "close_at_50_percent_profit_then_wait_5d",
    "close_at_50_percent_profit_then_wait_10d",
    "close_at_50_percent_profit_then_pullback_or_wait_2pct_10d",
    "close_at_50_percent_profit_then_pullback_or_wait_3pct_10d",
    "adaptive_close50_wait10_by_regime",
    "adaptive_close50_wait10_by_regime_and_cost",
    "adaptive_by_regime_dte_cost",
]

RULE_LABELS = {
    "hold_to_expiration": "Hold",
    "close_at_50_percent_profit": "Close50",
    "close_at_50_percent_profit_then_wait": "Wait",
    "close_at_50_percent_profit_then_wait_1d": "Wait1d",
    "close_at_50_percent_profit_then_wait_3d": "Wait3d",
    "close_at_50_percent_profit_then_wait_5d": "Wait5d",
    "close_at_50_percent_profit_then_wait_10d": "Wait10d",
    "close_at_50_percent_profit_then_pullback_or_wait_2pct_10d": "Pullback2pctOr10d",
    "close_at_50_percent_profit_then_pullback_or_wait_3pct_10d": "Pullback3pctOr10d",
    "adaptive_close50_wait10_by_regime": "AdaptiveClose50Wait10",
    "adaptive_close50_wait10_by_regime_and_cost": "AdaptiveClose50Wait10CostAware",
    "adaptive_by_regime_dte_cost": "AdaptiveRegimeDTECost",
}


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUTS_DIR = PROJECT_ROOT / "outputs"

TABLES_DIR = OUTPUTS_DIR / "tables"
CHARTS_DIR = OUTPUTS_DIR / "charts"

PATH_LEVEL_TABLE_DIR = TABLES_DIR / "path_level"
CYCLE_LEVEL_TABLE_DIR = TABLES_DIR / "cycle_level"
COMPARISON_TABLE_DIR = TABLES_DIR / "comparison"

PATH_LEVEL_CHART_DIR = CHARTS_DIR / "path_level"
CYCLE_LEVEL_CHART_DIR = CHARTS_DIR / "cycle_level"
COMPARISON_CHART_DIR = CHARTS_DIR / "comparison"


def ensure_output_dirs() -> None:
    """
    Create all output directories if they do not already exist.
    """

    for folder in [
        PATH_LEVEL_TABLE_DIR,
        CYCLE_LEVEL_TABLE_DIR,
        COMPARISON_TABLE_DIR,
        PATH_LEVEL_CHART_DIR,
        CYCLE_LEVEL_CHART_DIR,
        COMPARISON_CHART_DIR,
    ]:
        folder.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------
# Column helpers
# ---------------------------------------------------------------------

def clean_experiment_name(name: str) -> str:
    """
    Make an experiment name safe for file names.
    """

    return (
        str(name)
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
    )


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """
    Find the first matching column from a list of candidate names.

    Matching is case-insensitive.
    """

    if df is None or df.empty:
        return None

    lower_map = {str(col).lower(): col for col in df.columns}

    for candidate in candidates:
        key = candidate.lower()
        if key in lower_map:
            return lower_map[key]

    return None


def numeric_mean(df: pd.DataFrame, candidates: list[str]) -> float | None:
    """
    Return the mean of the first matching numeric column.
    """

    col = find_column(df, candidates)

    if col is None:
        return None

    values = pd.to_numeric(df[col], errors="coerce")

    if values.dropna().empty:
        return None

    return float(values.mean())


def numeric_median(df: pd.DataFrame, candidates: list[str]) -> float | None:
    """
    Return the median of the first matching numeric column.
    """

    col = find_column(df, candidates)

    if col is None:
        return None

    values = pd.to_numeric(df[col], errors="coerce")

    if values.dropna().empty:
        return None

    return float(values.median())


def normalize_rule_variant(rule_variant: str) -> str:
    """
    Normalize a management-rule variant.

    This mainly protects against accidental leading/trailing underscores.
    """

    return str(rule_variant).strip().strip("_")


def parse_experiment_name(
    experiment_name: str,
) -> tuple[str, str, int | None, float | None, int | None]:
    """
    Parse experiment name into:

        regime
        rule_variant
        wait_days
        pullback_percent
        max_wait_days

    Current main.py experiment names use a double separator:

        regime__rule_variant

    Examples:

        bullish_market__close_at_50_percent_profit_then_wait_10d
        bullish_market__close_at_50_percent_profit_then_pullback_or_wait_3pct_10d
        bullish_market__adaptive_close50_wait10_by_regime
        bullish_market__adaptive_close50_wait10_by_regime_and_cost
        bullish_market__adaptive_by_regime_dte_cost
    """

    name = str(experiment_name).strip()

    known_rule_prefixes = [
        "adaptive_by_regime_dte_cost",
        "adaptive_close50_wait10_by_regime_and_cost",
        "adaptive_close50_wait10_by_regime",
        "close_at_50_percent_profit_then_pullback_or_wait_",
        "close_at_50_percent_profit_then_wait_",
        "close_at_50_percent_profit",
        "hold_to_expiration",
    ]

    regime = name
    rule_variant = "unknown"

    if "__" in name:
        possible_regime, possible_rule = name.split("__", 1)
        possible_rule = normalize_rule_variant(possible_rule)

        if any(possible_rule.startswith(prefix) for prefix in known_rule_prefixes):
            regime = possible_regime.strip().strip("_")
            rule_variant = possible_rule
        else:
            regime = name.strip().strip("_")
            rule_variant = "unknown"
    else:
        suffixes = [
            "adaptive_by_regime_dte_cost",
            "adaptive_close50_wait10_by_regime_and_cost",
            "adaptive_close50_wait10_by_regime",
            "close_at_50_percent_profit_then_pullback_or_wait_",
            "close_at_50_percent_profit_then_wait_",
            "close_at_50_percent_profit",
            "hold_to_expiration",
        ]

        matched = False

        for suffix in suffixes:
            marker = f"_{suffix}"

            if marker in name:
                split_index = name.find(marker)
                regime = name[:split_index].strip().strip("_")
                rule_variant = name[split_index + 1:].strip().strip("_")
                matched = True
                break

        if not matched:
            regime = name.strip().strip("_")
            rule_variant = "unknown"

    rule_variant = normalize_rule_variant(rule_variant)

    if rule_variant in {
        "adaptive_close50_wait10_by_regime",
        "adaptive_close50_wait10_by_regime_and_cost",
        "adaptive_by_regime_dte_cost",
    }:
        return regime, rule_variant, None, None, None

    pullback_match = re.match(
        r"close_at_50_percent_profit_then_pullback_or_wait_"
        r"(\d+(?:\.\d+)?|\d+p\d+)pct_(\d+)d$",
        rule_variant,
    )

    if pullback_match:
        pct_text = pullback_match.group(1).replace("p", ".")
        pullback_percent = float(pct_text)
        max_wait_days = int(pullback_match.group(2))

        pct_label = (
            str(int(pullback_percent))
            if pullback_percent.is_integer()
            else str(pullback_percent).replace(".", "p")
        )

        canonical_rule = (
            "close_at_50_percent_profit_then_pullback_or_wait_"
            f"{pct_label}pct_{max_wait_days}d"
        )

        return regime, canonical_rule, None, pullback_percent, max_wait_days

    wait_match = re.match(
        r"close_at_50_percent_profit_then_wait_(\d+)d$",
        rule_variant,
    )

    if wait_match:
        wait_days = int(wait_match.group(1))
        canonical_rule = f"close_at_50_percent_profit_then_wait_{wait_days}d"

        return regime, canonical_rule, wait_days, None, None

    if rule_variant == "close_at_50_percent_profit":
        return regime, rule_variant, 0, None, None

    if rule_variant == "hold_to_expiration":
        return regime, rule_variant, None, None, None

    return regime, rule_variant, None, None, None


def get_rule_label(rule_variant: str) -> str:
    """
    Return short rule label for table and chart column names.
    """

    rule_variant = normalize_rule_variant(rule_variant)

    if rule_variant in RULE_LABELS:
        return RULE_LABELS[rule_variant]

    wait_match = re.match(
        r"close_at_50_percent_profit_then_wait_(\d+)d$",
        str(rule_variant),
    )

    if wait_match:
        return f"Wait{wait_match.group(1)}d"

    pullback_match = re.match(
        r"close_at_50_percent_profit_then_pullback_or_wait_"
        r"(\d+(?:p\d+)?|\d+(?:\.\d+)?)pct_(\d+)d$",
        str(rule_variant),
    )

    if pullback_match:
        pct = pullback_match.group(1).replace("p", ".")
        days = pullback_match.group(2)

        if pct.endswith(".0"):
            pct = pct[:-2]

        return f"Pullback{pct}pctOr{days}d"

    return str(rule_variant)


def format_decimal(value: float | None, digits: int = 4) -> str:
    """
    Format a numeric value for text output.
    """

    if value is None or pd.isna(value):
        return "NA"

    return f"{value:.{digits}f}"


def format_currency(value: float | None) -> str:
    """
    Format a numeric value as dollars for text output.
    """

    if value is None or pd.isna(value):
        return "NA"

    return f"${value:,.2f}"


# ---------------------------------------------------------------------
# Metric aliases
# ---------------------------------------------------------------------

OUTPERFORMANCE_COLUMNS = [
    "outperformance",
    "mean_outperformance",
    "avg_outperformance",
    "covered_call_minus_buy_and_hold",
    "cc_minus_bh",
]

NET_OPTION_COLUMNS = [
    "net_option",
    "net_option_effect",
    "option_net",
    "total_net_option",
    "option_pnl",
]

ASSIGNMENT_COLUMNS = [
    "assignment",
    "assignments",
    "total_assignments",
    "num_assignments",
    "assignment_count",
]

OPTION_CYCLE_COLUMNS = [
    "option_cyc",
    "option_cycles",
    "cycles",
    "num_cycles",
    "cycle_count",
]

TOTAL_PREMIUM_COLUMNS = [
    "total_prem",
    "total_premium",
    "total_premium_collected",
    "total_premiums",
    "premiums",
]

TOTAL_GROSS_PREMIUM_COLUMNS = [
    "total_gross_premium_collected",
    "gross_premium_collected",
    "total_gross_premium",
]

TOTAL_BUYBACK_COLUMNS = [
    "total_buyb",
    "total_buyback_cost",
    "total_buybacks",
    "buybacks",
    "buyback_cost",
]

TOTAL_GROSS_BUYBACK_COLUMNS = [
    "total_gross_buyback_cost",
    "gross_buyback_cost",
    "total_gross_buybacks",
]

TOTAL_MISSED_UPSIDE_COLUMNS = [
    "total_miss",
    "total_missed_upside",
    "missed_upside",
]

TOTAL_TRANSACTION_COST_COLUMNS = [
    "total_transaction_cost",
    "transaction_cost",
    "total_costs",
]

TOTAL_COMMISSION_COST_COLUMNS = [
    "total_commission_cost",
    "commission_cost",
    "commissions",
    "total_commissions",
]

TOTAL_SLIPPAGE_COST_COLUMNS = [
    "total_slippage_cost",
    "slippage_cost",
    "slippage",
    "total_slippage",
]

COVERED_CALL_RETURN_COLUMNS = [
    "covered_call_return",
    "covered_call_ret",
    "cc_return",
]

BUY_AND_HOLD_RETURN_COLUMNS = [
    "buy_and_hold_return",
    "buy_hold_return",
    "bh_return",
]

FINAL_COVERED_CALL_VALUE_COLUMNS = [
    "final_cover",
    "final_covered_call_value",
    "final_covered_call",
    "final_cc_value",
]

FINAL_BUY_AND_HOLD_VALUE_COLUMNS = [
    "final_buy_and_hold_value",
    "final_buy_hold_value",
    "final_bh_value",
]


# ---------------------------------------------------------------------
# Path-level reports
# ---------------------------------------------------------------------

def summarize_path_level_results(results: pd.DataFrame) -> dict[str, Any]:
    """
    Calculate path-level summary metrics for one experiment.
    """

    return {
        "Number_Paths": int(len(results)),
        "Mean_Covered_Call_Return": numeric_mean(results, COVERED_CALL_RETURN_COLUMNS),
        "Mean_Buy_And_Hold_Return": numeric_mean(results, BUY_AND_HOLD_RETURN_COLUMNS),
        "Mean_Outperformance": numeric_mean(results, OUTPERFORMANCE_COLUMNS),
        "Median_Outperformance": numeric_median(results, OUTPERFORMANCE_COLUMNS),
        "Mean_Net_Option_Effect": numeric_mean(results, NET_OPTION_COLUMNS),
        "Median_Net_Option_Effect": numeric_median(results, NET_OPTION_COLUMNS),
        "Mean_Total_Premiums": numeric_mean(results, TOTAL_PREMIUM_COLUMNS),
        "Mean_Total_Gross_Premiums": numeric_mean(results, TOTAL_GROSS_PREMIUM_COLUMNS),
        "Mean_Total_Buybacks": numeric_mean(results, TOTAL_BUYBACK_COLUMNS),
        "Mean_Total_Gross_Buybacks": numeric_mean(results, TOTAL_GROSS_BUYBACK_COLUMNS),
        "Mean_Missed_Upside": numeric_mean(results, TOTAL_MISSED_UPSIDE_COLUMNS),
        "Mean_Total_Transaction_Cost": numeric_mean(results, TOTAL_TRANSACTION_COST_COLUMNS),
        "Mean_Total_Commission_Cost": numeric_mean(results, TOTAL_COMMISSION_COST_COLUMNS),
        "Mean_Total_Slippage_Cost": numeric_mean(results, TOTAL_SLIPPAGE_COST_COLUMNS),
        "Mean_Assignments": numeric_mean(results, ASSIGNMENT_COLUMNS),
        "Mean_Option_Cycles": numeric_mean(results, OPTION_CYCLE_COLUMNS),
        "Mean_Final_Covered_Call_Value": numeric_mean(results, FINAL_COVERED_CALL_VALUE_COLUMNS),
        "Mean_Final_Buy_And_Hold_Value": numeric_mean(results, FINAL_BUY_AND_HOLD_VALUE_COLUMNS),
    }


def run_full_report(experiment_name: str, results: pd.DataFrame) -> pd.DataFrame:
    """
    Save path-level results and summary for one experiment.
    """

    ensure_output_dirs()

    safe_name = clean_experiment_name(experiment_name)

    path_results_file = PATH_LEVEL_TABLE_DIR / f"{safe_name}_path_level_results.csv"
    path_summary_file = PATH_LEVEL_TABLE_DIR / f"{safe_name}_path_level_summary.csv"

    results.to_csv(path_results_file, index=False)

    (
        regime,
        rule_variant,
        wait_days,
        pullback_percent,
        max_wait_days,
    ) = parse_experiment_name(experiment_name)

    summary = summarize_path_level_results(results)

    summary_df = pd.DataFrame([summary])
    summary_df.insert(0, "Experiment", experiment_name)
    summary_df.insert(1, "Regime", regime)
    summary_df.insert(2, "Management_Rule", rule_variant)
    summary_df.insert(3, "Management_Label", get_rule_label(rule_variant))
    summary_df.insert(4, "Wait_Days", wait_days)
    summary_df.insert(5, "Pullback_Percent", pullback_percent)
    summary_df.insert(6, "Max_Wait_Days", max_wait_days)

    summary_df.to_csv(path_summary_file, index=False)

    save_path_level_histogram(
        experiment_name=experiment_name,
        results=results,
        metric_candidates=OUTPERFORMANCE_COLUMNS,
        metric_label="Outperformance",
    )

    save_path_level_histogram(
        experiment_name=experiment_name,
        results=results,
        metric_candidates=NET_OPTION_COLUMNS,
        metric_label="Net Option Effect",
    )

    save_path_level_histogram(
        experiment_name=experiment_name,
        results=results,
        metric_candidates=TOTAL_TRANSACTION_COST_COLUMNS,
        metric_label="Transaction Cost",
    )

    return summary_df


def save_path_level_histogram(
    experiment_name: str,
    results: pd.DataFrame,
    metric_candidates: list[str],
    metric_label: str,
) -> None:
    """
    Save a histogram for a selected path-level metric.
    """

    ensure_output_dirs()

    col = find_column(results, metric_candidates)

    if col is None:
        return

    values = pd.to_numeric(results[col], errors="coerce").dropna()

    if values.empty:
        return

    safe_name = clean_experiment_name(experiment_name)
    safe_metric = clean_experiment_name(metric_label.lower())

    plt.figure(figsize=(9, 5))
    plt.hist(values, bins=30)
    plt.title(f"{experiment_name}: {metric_label}")
    plt.xlabel(metric_label)
    plt.ylabel("Path Count")
    plt.tight_layout()

    chart_file = PATH_LEVEL_CHART_DIR / f"{safe_name}_{safe_metric}_histogram.png"
    plt.savefig(chart_file, dpi=150)
    plt.close()


# ---------------------------------------------------------------------
# Cycle-level reports
# ---------------------------------------------------------------------

def run_cycle_report(experiment_name: str, results: pd.DataFrame) -> pd.DataFrame:
    """
    Save simple cycle-level summary for one experiment.
    """

    ensure_output_dirs()

    safe_name = clean_experiment_name(experiment_name)

    (
        regime,
        rule_variant,
        wait_days,
        pullback_percent,
        max_wait_days,
    ) = parse_experiment_name(experiment_name)

    cycle_summary = {
        "Experiment": experiment_name,
        "Regime": regime,
        "Management_Rule": rule_variant,
        "Management_Label": get_rule_label(rule_variant),
        "Wait_Days": wait_days,
        "Pullback_Percent": pullback_percent,
        "Max_Wait_Days": max_wait_days,
        "Mean_Option_Cycles": numeric_mean(results, OPTION_CYCLE_COLUMNS),
        "Mean_Assignments": numeric_mean(results, ASSIGNMENT_COLUMNS),
        "Mean_Total_Premiums": numeric_mean(results, TOTAL_PREMIUM_COLUMNS),
        "Mean_Total_Gross_Premiums": numeric_mean(results, TOTAL_GROSS_PREMIUM_COLUMNS),
        "Mean_Total_Buybacks": numeric_mean(results, TOTAL_BUYBACK_COLUMNS),
        "Mean_Total_Gross_Buybacks": numeric_mean(results, TOTAL_GROSS_BUYBACK_COLUMNS),
        "Mean_Missed_Upside": numeric_mean(results, TOTAL_MISSED_UPSIDE_COLUMNS),
        "Mean_Net_Option_Effect": numeric_mean(results, NET_OPTION_COLUMNS),
        "Mean_Total_Transaction_Cost": numeric_mean(results, TOTAL_TRANSACTION_COST_COLUMNS),
        "Mean_Total_Commission_Cost": numeric_mean(results, TOTAL_COMMISSION_COST_COLUMNS),
        "Mean_Total_Slippage_Cost": numeric_mean(results, TOTAL_SLIPPAGE_COST_COLUMNS),
    }

    cycle_summary_df = pd.DataFrame([cycle_summary])

    cycle_summary_file = CYCLE_LEVEL_TABLE_DIR / f"{safe_name}_cycle_level_summary.csv"
    cycle_summary_df.to_csv(cycle_summary_file, index=False)

    return cycle_summary_df


# ---------------------------------------------------------------------
# Experiment-level comparison reports
# ---------------------------------------------------------------------

def build_experiment_summary_table(
    all_results: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Build one summary row per experiment.
    """

    rows = []

    for experiment_name, results in all_results.items():
        (
            regime,
            rule_variant,
            wait_days,
            pullback_percent,
            max_wait_days,
        ) = parse_experiment_name(experiment_name)

        summary = summarize_path_level_results(results)
        summary["Experiment"] = experiment_name
        summary["Regime"] = regime
        summary["Management_Rule"] = rule_variant
        summary["Management_Label"] = get_rule_label(rule_variant)
        summary["Wait_Days"] = wait_days
        summary["Pullback_Percent"] = pullback_percent
        summary["Max_Wait_Days"] = max_wait_days

        rows.append(summary)

    df = pd.DataFrame(rows)

    leading_cols = [
        "Experiment",
        "Regime",
        "Management_Rule",
        "Management_Label",
        "Wait_Days",
        "Pullback_Percent",
        "Max_Wait_Days",
    ]

    other_cols = [col for col in df.columns if col not in leading_cols]

    return df[leading_cols + other_cols]


def save_experiment_comparison(
    all_results: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Save comparison table across all experiments.
    """

    ensure_output_dirs()

    comparison_df = build_experiment_summary_table(all_results)

    comparison_file = COMPARISON_TABLE_DIR / "experiment_comparison.csv"
    comparison_df.to_csv(comparison_file, index=False)

    return comparison_df


def save_experiment_comparison_chart(
    all_results: dict[str, pd.DataFrame],
) -> None:
    """
    Save a chart comparing mean outperformance across experiments.
    """

    ensure_output_dirs()

    comparison_df = build_experiment_summary_table(all_results)

    if "Mean_Outperformance" not in comparison_df.columns:
        return

    plot_df = comparison_df.dropna(subset=["Mean_Outperformance"]).copy()

    if plot_df.empty:
        return

    plot_df["Label"] = (
        plot_df["Regime"]
        + "\n"
        + plot_df["Management_Rule"].map(get_rule_label)
    )

    plt.figure(figsize=(18, 7))
    plt.bar(plot_df["Label"], plot_df["Mean_Outperformance"])
    plt.axhline(0, linewidth=1)
    plt.title("Mean Outperformance by Experiment")
    plt.xlabel("Experiment")
    plt.ylabel("Mean Outperformance")
    plt.xticks(rotation=60, ha="right")
    plt.tight_layout()

    chart_file = COMPARISON_CHART_DIR / "experiment_mean_outperformance_comparison.png"
    plt.savefig(chart_file, dpi=150)
    plt.close()


# ---------------------------------------------------------------------
# Cycle-level comparison reports
# ---------------------------------------------------------------------

def save_cycle_comparison(
    all_results: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Save cycle-related comparison table across all experiments.
    """

    ensure_output_dirs()

    rows = []

    for experiment_name, results in all_results.items():
        (
            regime,
            rule_variant,
            wait_days,
            pullback_percent,
            max_wait_days,
        ) = parse_experiment_name(experiment_name)

        rows.append(
            {
                "Experiment": experiment_name,
                "Regime": regime,
                "Management_Rule": rule_variant,
                "Management_Label": get_rule_label(rule_variant),
                "Wait_Days": wait_days,
                "Pullback_Percent": pullback_percent,
                "Max_Wait_Days": max_wait_days,
                "Mean_Option_Cycles": numeric_mean(results, OPTION_CYCLE_COLUMNS),
                "Mean_Assignments": numeric_mean(results, ASSIGNMENT_COLUMNS),
                "Mean_Total_Premiums": numeric_mean(results, TOTAL_PREMIUM_COLUMNS),
                "Mean_Total_Gross_Premiums": numeric_mean(results, TOTAL_GROSS_PREMIUM_COLUMNS),
                "Mean_Total_Buybacks": numeric_mean(results, TOTAL_BUYBACK_COLUMNS),
                "Mean_Total_Gross_Buybacks": numeric_mean(results, TOTAL_GROSS_BUYBACK_COLUMNS),
                "Mean_Missed_Upside": numeric_mean(results, TOTAL_MISSED_UPSIDE_COLUMNS),
                "Mean_Net_Option_Effect": numeric_mean(results, NET_OPTION_COLUMNS),
                "Mean_Total_Transaction_Cost": numeric_mean(results, TOTAL_TRANSACTION_COST_COLUMNS),
                "Mean_Total_Commission_Cost": numeric_mean(results, TOTAL_COMMISSION_COST_COLUMNS),
                "Mean_Total_Slippage_Cost": numeric_mean(results, TOTAL_SLIPPAGE_COST_COLUMNS),
            }
        )

    cycle_df = pd.DataFrame(rows)

    cycle_file = COMPARISON_TABLE_DIR / "cycle_level_comparison.csv"
    cycle_df.to_csv(cycle_file, index=False)

    return cycle_df


def save_cycle_comparison_charts(
    all_results: dict[str, pd.DataFrame],
) -> None:
    """
    Save cycle-level comparison charts.
    """

    ensure_output_dirs()

    cycle_df = save_cycle_comparison(all_results)

    for metric in [
        "Mean_Option_Cycles",
        "Mean_Assignments",
        "Mean_Total_Transaction_Cost",
    ]:
        if metric not in cycle_df.columns:
            continue

        plot_df = cycle_df.dropna(subset=[metric]).copy()

        if plot_df.empty:
            continue

        plot_df["Label"] = (
            plot_df["Regime"]
            + "\n"
            + plot_df["Management_Rule"].map(get_rule_label)
        )

        plt.figure(figsize=(18, 7))
        plt.bar(plot_df["Label"], plot_df[metric])
        plt.title(metric.replace("_", " "))
        plt.xlabel("Experiment")
        plt.ylabel(metric.replace("_", " "))
        plt.xticks(rotation=60, ha="right")
        plt.tight_layout()

        chart_file = COMPARISON_CHART_DIR / f"{metric.lower()}_comparison.png"
        plt.savefig(chart_file, dpi=150)
        plt.close()


# ---------------------------------------------------------------------
# Management-rule comparison reports
# ---------------------------------------------------------------------

def build_management_rule_comparison(
    all_results: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Build a wide comparison table with one row per regime and metric columns
    for each management rule variant.
    """

    summary_df = build_experiment_summary_table(all_results)

    metrics = [
        "Mean_Outperformance",
        "Mean_Net_Option_Effect",
        "Mean_Assignments",
        "Mean_Option_Cycles",
        "Mean_Total_Premiums",
        "Mean_Total_Gross_Premiums",
        "Mean_Total_Buybacks",
        "Mean_Total_Gross_Buybacks",
        "Mean_Missed_Upside",
        "Mean_Total_Transaction_Cost",
        "Mean_Total_Commission_Cost",
        "Mean_Total_Slippage_Cost",
        "Mean_Covered_Call_Return",
        "Mean_Buy_And_Hold_Return",
        "Mean_Final_Covered_Call_Value",
        "Mean_Final_Buy_And_Hold_Value",
    ]

    regimes = sorted(summary_df["Regime"].dropna().unique())

    observed_rules = list(summary_df["Management_Rule"].dropna().unique())

    ordered_rules = [
        rule for rule in RULE_DISPLAY_ORDER
        if rule in observed_rules
    ]

    for rule in observed_rules:
        if rule not in ordered_rules:
            ordered_rules.append(rule)

    rows = []

    for regime in regimes:
        regime_df = summary_df[summary_df["Regime"] == regime]

        row: dict[str, Any] = {
            "Regime": regime,
        }

        for rule in ordered_rules:
            rule_df = regime_df[regime_df["Management_Rule"] == rule]
            label = get_rule_label(rule)

            if rule_df.empty:
                for metric in metrics:
                    row[f"{label}_{metric}"] = None
                continue

            rule_row = rule_df.iloc[0]

            for metric in metrics:
                value = pd.to_numeric(rule_row.get(metric), errors="coerce")
                row[f"{label}_{metric}"] = None if pd.isna(value) else float(value)

        rows.append(row)

    return pd.DataFrame(rows)


def build_strategy_map(summary_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build one practical recommendation row per regime.

    The best rule is selected by highest Mean_Outperformance.

    If the best rule beats the second-best rule by less than
    OUTPERFORMANCE_MATERIALITY_THRESHOLD, the signal is treated as weak.
    """

    rows = []

    regimes = sorted(summary_df["Regime"].dropna().unique())

    for regime in regimes:
        regime_df = summary_df[summary_df["Regime"] == regime].copy()

        regime_df["Mean_Outperformance"] = pd.to_numeric(
            regime_df["Mean_Outperformance"],
            errors="coerce",
        )

        regime_df["Mean_Net_Option_Effect"] = pd.to_numeric(
            regime_df["Mean_Net_Option_Effect"],
            errors="coerce",
        )

        regime_df["Mean_Total_Transaction_Cost"] = pd.to_numeric(
            regime_df.get("Mean_Total_Transaction_Cost"),
            errors="coerce",
        )

        regime_df = regime_df.dropna(subset=["Mean_Outperformance"])

        if regime_df.empty:
            rows.append(
                {
                    "Regime": regime,
                    "Recommended_Action": "No recommendation available.",
                    "Preferred_Rule": "insufficient_data",
                    "Preferred_Label": "NA",
                    "Signal_Strength": "none",
                    "Best_Mean_Outperformance": None,
                    "Second_Best_Mean_Outperformance": None,
                    "Outperformance_Edge": None,
                    "Best_Net_Option_Effect": None,
                    "Best_Transaction_Cost": None,
                    "Second_Best_Rule": None,
                    "Second_Best_Label": "NA",
                    "Main_Reason": "No numeric outperformance data was available.",
                }
            )
            continue

        ranked = regime_df.sort_values(
            by="Mean_Outperformance",
            ascending=False,
        ).reset_index(drop=True)

        best = ranked.iloc[0]
        second = ranked.iloc[1] if len(ranked) > 1 else None

        best_rule = best["Management_Rule"]
        best_label = get_rule_label(best_rule)
        best_outperf = float(best["Mean_Outperformance"])
        best_net = float(best["Mean_Net_Option_Effect"])

        best_transaction_cost = None

        if "Mean_Total_Transaction_Cost" in best.index:
            value = pd.to_numeric(best["Mean_Total_Transaction_Cost"], errors="coerce")
            best_transaction_cost = None if pd.isna(value) else float(value)

        if second is not None:
            second_rule = second["Management_Rule"]
            second_label = get_rule_label(second_rule)
            second_outperf = float(second["Mean_Outperformance"])
            edge = best_outperf - second_outperf
        else:
            second_rule = "none"
            second_label = "none"
            second_outperf = None
            edge = None

        if edge is None:
            signal_strength = "none"
        elif abs(edge) < OUTPERFORMANCE_MATERIALITY_THRESHOLD:
            signal_strength = "weak"
        else:
            signal_strength = "meaningful"

        recommended_action = build_recommended_action(
            preferred_rule=best_rule,
            signal_strength=signal_strength,
        )

        main_reason = build_main_reason(
            preferred_rule=best_rule,
            second_rule=second_rule,
            best_outperf=best_outperf,
            second_outperf=second_outperf,
            edge=edge,
            best_net=best_net,
            best_transaction_cost=best_transaction_cost,
            signal_strength=signal_strength,
        )

        rows.append(
            {
                "Regime": regime,
                "Recommended_Action": recommended_action,
                "Preferred_Rule": best_rule,
                "Preferred_Label": best_label,
                "Signal_Strength": signal_strength,
                "Best_Mean_Outperformance": best_outperf,
                "Second_Best_Mean_Outperformance": second_outperf,
                "Outperformance_Edge": edge,
                "Best_Net_Option_Effect": best_net,
                "Best_Transaction_Cost": best_transaction_cost,
                "Second_Best_Rule": second_rule,
                "Second_Best_Label": second_label,
                "Main_Reason": main_reason,
            }
        )

    return pd.DataFrame(rows)


def build_recommended_action(
    preferred_rule: str,
    signal_strength: str,
) -> str:
    """
    Convert preferred rule into plain-English action.
    """

    preferred_rule = normalize_rule_variant(preferred_rule)

    if signal_strength == "weak":
        return (
            "No strong rule edge; choose based on turnover, assignment risk, "
            "and execution costs."
        )

    if preferred_rule == "hold_to_expiration":
        return "Prefer holding covered calls to expiration."

    if preferred_rule == "close_at_50_percent_profit":
        return "Prefer closing at 50% profit and immediately reselling calls."

    if preferred_rule == "adaptive_close50_wait10_by_regime":
        return (
            "Prefer the adaptive rule: close at 50% profit and immediately "
            "resell in bearish/sideways regimes; otherwise close at 50% profit "
            "and wait 10 trading days before selling the next call."
        )

    if preferred_rule == "adaptive_close50_wait10_by_regime_and_cost":
        return (
            "Prefer the cost-aware adaptive rule: close at 50% profit and "
            "immediately resell in bearish regimes; in sideways regimes, use "
            "Close50 only when transaction costs are below the cost threshold "
            "and otherwise hold to expiration; in other regimes, close at 50% "
            "profit and wait 10 trading days before selling the next call."
        )

    if preferred_rule == "adaptive_by_regime_dte_cost":
        return (
            "Prefer the DTE-aware adaptive rule: use Close50 in bearish markets; "
            "in sideways markets, hold short-DTE calls to expiration and use "
            "Close50 for longer DTE unless transaction costs are high; in other "
            "regimes, use Wait10d for DTE below 45 and hold to expiration for "
            "DTE of 45 or higher."
        )

    wait_match = re.match(
        r"close_at_50_percent_profit_then_wait_(\d+)d$",
        str(preferred_rule),
    )

    if wait_match:
        wait_days = wait_match.group(1)
        return (
            f"Prefer closing at 50% profit, then waiting {wait_days} trading "
            "days before selling the next call."
        )

    pullback_match = re.match(
        r"close_at_50_percent_profit_then_pullback_or_wait_"
        r"(\d+(?:p\d+)?|\d+(?:\.\d+)?)pct_(\d+)d$",
        str(preferred_rule),
    )

    if pullback_match:
        pct = pullback_match.group(1).replace("p", ".")
        days = pullback_match.group(2)

        if pct.endswith(".0"):
            pct = pct[:-2]

        return (
            f"Prefer closing at 50% profit, then waiting for a {pct}% pullback "
            f"or {days} trading days before selling the next call."
        )

    return "No recommendation available."


def build_main_reason(
    preferred_rule: str,
    second_rule: str,
    best_outperf: float | None,
    second_outperf: float | None,
    edge: float | None,
    best_net: float | None,
    best_transaction_cost: float | None,
    signal_strength: str,
) -> str:
    """
    Build concise explanation for the strategy map.
    """

    best_label = get_rule_label(preferred_rule)
    second_label = get_rule_label(second_rule)

    cost_text = ""

    if best_transaction_cost is not None and not pd.isna(best_transaction_cost):
        cost_text = (
            f" Mean transaction cost was "
            f"{format_currency(best_transaction_cost)}."
        )

    if edge is None:
        return "Only one rule had valid numeric results." + cost_text

    if signal_strength == "weak":
        return (
            f"{best_label} had the highest mean outperformance, but its edge "
            f"over {second_label} was only {format_decimal(edge, 4)}, below "
            f"the {OUTPERFORMANCE_MATERIALITY_THRESHOLD:.4f} materiality threshold."
            f" Its mean net option effect was {format_currency(best_net)}."
            f"{cost_text}"
        )

    return (
        f"{best_label} beat {second_label} by "
        f"{format_decimal(edge, 4)} in mean outperformance. "
        f"Its mean net option effect was {format_currency(best_net)}."
        f"{cost_text}"
    )


def build_management_rule_decision_summary(
    summary_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build regime-level decision summary.

    This is equivalent to the strategy map, but kept under the old file name
    for continuity.
    """

    return build_strategy_map(summary_df)


def save_management_rule_comparison(
    all_results: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Save management-rule comparison tables and charts.
    """

    ensure_output_dirs()

    summary_df = build_experiment_summary_table(all_results)

    comparison_df = build_management_rule_comparison(all_results)
    decision_df = build_management_rule_decision_summary(summary_df)
    strategy_map_df = decision_df.copy()

    comparison_file = COMPARISON_TABLE_DIR / "management_rule_comparison.csv"
    decision_file = COMPARISON_TABLE_DIR / "management_rule_decision_summary.csv"
    strategy_map_file = COMPARISON_TABLE_DIR / "strategy_map.csv"

    comparison_df.to_csv(comparison_file, index=False)
    decision_df.to_csv(decision_file, index=False)
    strategy_map_df.to_csv(strategy_map_file, index=False)

    save_management_rule_charts(summary_df)

    return comparison_df, decision_df


def save_management_rule_charts(summary_df: pd.DataFrame) -> None:
    """
    Save management-rule comparison charts for all rule variants.
    """

    ensure_output_dirs()

    chart_specs = [
        (
            "Mean_Outperformance",
            "Mean Outperformance by Regime and Management Rule",
            "Mean Outperformance",
            "management_rule_outperformance_comparison.png",
        ),
        (
            "Mean_Net_Option_Effect",
            "Mean Net Option Effect by Regime and Management Rule",
            "Mean Net Option Effect",
            "management_rule_net_effect_comparison.png",
        ),
        (
            "Mean_Option_Cycles",
            "Mean Option Cycles by Regime and Management Rule",
            "Mean Option Cycles",
            "management_rule_cycle_comparison.png",
        ),
        (
            "Mean_Total_Transaction_Cost",
            "Mean Transaction Cost by Regime and Management Rule",
            "Mean Transaction Cost",
            "management_rule_transaction_cost_comparison.png",
        ),
    ]

    for metric, title, ylabel, filename in chart_specs:
        if metric not in summary_df.columns:
            continue

        plot_df = summary_df.dropna(subset=[metric]).copy()

        if plot_df.empty:
            continue

        pivot = plot_df.pivot(
            index="Regime",
            columns="Management_Rule",
            values=metric,
        )

        ordered_columns = [
            rule for rule in RULE_DISPLAY_ORDER
            if rule in pivot.columns
        ]

        for rule in pivot.columns:
            if rule not in ordered_columns:
                ordered_columns.append(rule)

        pivot = pivot[ordered_columns]
        pivot.columns = [get_rule_label(col) for col in pivot.columns]

        ax = pivot.plot(kind="bar", figsize=(16, 7))
        ax.axhline(0, linewidth=1)
        ax.set_title(title)
        ax.set_xlabel("Regime")
        ax.set_ylabel(ylabel)

        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()

        chart_file = COMPARISON_CHART_DIR / filename
        plt.savefig(chart_file, dpi=150)
        plt.close()