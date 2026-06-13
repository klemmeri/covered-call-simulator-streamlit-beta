"""
ticker_calibration.py

Ticker-specific calibration script for the Covered Call Simulator.

This script lets you test the current covered-call management rules using
ticker-like assumptions instead of only abstract market regimes.

It answers:

    For a specific ticker assumption set, which management rule works best?

Examples of ticker-style assumptions:

    SPY:
        moderate return, moderate volatility

    QQQ:
        higher return, higher volatility

    SOXL:
        very high volatility, leveraged ETF behavior

This script reads no prior simulation files.
It runs fresh simulations and saves:

    outputs/tables/comparison/ticker_calibration_summary.csv
    outputs/tables/comparison/ticker_calibration_winners.csv
    outputs/tables/comparison/ticker_calibration_report.txt

    outputs/charts/comparison/ticker_calibration_mean_outperformance.png
    outputs/charts/comparison/ticker_calibration_net_option_effect.png
    outputs/charts/comparison/ticker_calibration_transaction_cost.png
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

# These are starting calibration assumptions, not historical estimates.
# We can refine them later using real historical data.
TICKER_CONFIGS = {
    "SPY_like": {
        "start_price": 100.0,
        "annual_return": 0.08,
        "annual_volatility": 0.18,
        "dte": 30,
        "target_delta": 0.30,
    },
    "QQQ_like": {
        "start_price": 100.0,
        "annual_return": 0.10,
        "annual_volatility": 0.25,
        "dte": 30,
        "target_delta": 0.30,
    },
    "IWM_like": {
        "start_price": 100.0,
        "annual_return": 0.07,
        "annual_volatility": 0.28,
        "dte": 30,
        "target_delta": 0.30,
    },
    "TQQQ_like": {
        "start_price": 100.0,
        "annual_return": 0.15,
        "annual_volatility": 0.55,
        "dte": 30,
        "target_delta": 0.30,
    },
    "SOXL_like": {
        "start_price": 100.0,
        "annual_return": 0.18,
        "annual_volatility": 0.70,
        "dte": 30,
        "target_delta": 0.30,
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

TICKER_ORDER = list(TICKER_CONFIGS.keys())
RULE_ORDER = list(RULE_CONFIGS.keys())

MATERIALITY_THRESHOLD = 0.0050


# =============================================================================
# Output paths
# =============================================================================

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "comparison"
OUTPUT_CHART_DIR = PROJECT_ROOT / "outputs" / "charts" / "comparison"

SUMMARY_PATH = OUTPUT_TABLE_DIR / "ticker_calibration_summary.csv"
WINNERS_PATH = OUTPUT_TABLE_DIR / "ticker_calibration_winners.csv"
REPORT_PATH = OUTPUT_TABLE_DIR / "ticker_calibration_report.txt"

OUTPERFORMANCE_CHART_PATH = (
    OUTPUT_CHART_DIR / "ticker_calibration_mean_outperformance.png"
)
NET_EFFECT_CHART_PATH = (
    OUTPUT_CHART_DIR / "ticker_calibration_net_option_effect.png"
)
TRANSACTION_COST_CHART_PATH = (
    OUTPUT_CHART_DIR / "ticker_calibration_transaction_cost.png"
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


def infer_regime_name_from_ticker_settings(
    annual_return: float,
    annual_volatility: float,
) -> str:
    """
    Assign a regime-like label for adaptive-rule logic.

    The existing adaptive rules depend on config.regime_name.

    This function maps ticker-style assumptions into one of the existing
    regime names so that adaptive rules can operate.
    """

    if annual_return < 0:
        return "bearish_market"

    if abs(annual_return) <= 0.02 and annual_volatility <= 0.20:
        return "sideways_market"

    if annual_return >= 0.12 and annual_volatility <= 0.35:
        return "bullish_market"

    if annual_volatility >= 0.40:
        return "high_volatility"

    if annual_volatility <= 0.15:
        return "low_volatility"

    return "baseline"


# =============================================================================
# Simulation
# =============================================================================

def build_config(
    ticker_label: str,
    rule_label: str,
) -> SimulationConfig:
    """
    Build one simulation config.
    """

    base_config = SimulationConfig()

    ticker_settings = TICKER_CONFIGS[ticker_label]
    rule_settings = RULE_CONFIGS[rule_label]

    inferred_regime_name = infer_regime_name_from_ticker_settings(
        annual_return=ticker_settings["annual_return"],
        annual_volatility=ticker_settings["annual_volatility"],
    )

    config = clone_config(
        base_config,
        n_paths=N_PATHS,
        start_price=ticker_settings["start_price"],
        annual_return=ticker_settings["annual_return"],
        annual_volatility=ticker_settings["annual_volatility"],
        dte=ticker_settings["dte"],
        target_delta=ticker_settings["target_delta"],
        regime_name=inferred_regime_name,
        **rule_settings,
    )

    return config


def run_single_experiment(
    ticker_label: str,
    rule_label: str,
) -> dict:
    """
    Run one ticker/rule experiment and return summary metrics.
    """

    experiment_name = f"{ticker_label}__{rule_label}"

    print("=" * 100)
    print(f"Running experiment: {experiment_name}")
    print("=" * 100)

    config = build_config(
        ticker_label=ticker_label,
        rule_label=rule_label,
    )

    engine = SimulationEngine(config)
    path_results_df = engine.run()

    summary = {
        "Ticker_Label": ticker_label,
        "Rule_Label": rule_label,
        "Management_Rule": config.management_rule,
        "Inferred_Regime_Name": config.regime_name,
        "Start_Price": config.start_price,
        "Annual_Return": config.annual_return,
        "Annual_Volatility": config.annual_volatility,
        "DTE": config.dte,
        "Target_Delta": config.target_delta,
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


def run_ticker_calibration() -> pd.DataFrame:
    """
    Run all ticker calibration experiments.
    """

    rows = []

    total_experiments = len(TICKER_ORDER) * len(RULE_ORDER)

    print("")
    print("=" * 100)
    print("COVERED CALL SIMULATOR - TICKER CALIBRATION")
    print("=" * 100)
    print(f"Paths per experiment: {N_PATHS}")
    print(f"Tickers tested:       {TICKER_ORDER}")
    print(f"Rules tested:         {RULE_ORDER}")
    print(f"Total experiments:    {total_experiments}")
    print("=" * 100)
    print("")

    experiment_count = 0

    for ticker_label in TICKER_ORDER:
        for rule_label in RULE_ORDER:
            experiment_count += 1

            print(f"Progress: {experiment_count} of {total_experiments}")

            summary = run_single_experiment(
                ticker_label=ticker_label,
                rule_label=rule_label,
            )

            rows.append(summary)

    summary_df = pd.DataFrame(rows)

    summary_df["Ticker_Label"] = pd.Categorical(
        summary_df["Ticker_Label"],
        categories=TICKER_ORDER,
        ordered=True,
    )

    summary_df["Rule_Label"] = pd.Categorical(
        summary_df["Rule_Label"],
        categories=RULE_ORDER,
        ordered=True,
    )

    summary_df = summary_df.sort_values(
        ["Ticker_Label", "Rule_Label"]
    ).reset_index(drop=True)

    return summary_df


# =============================================================================
# Winners and report
# =============================================================================

def build_winners_table(summary_df: pd.DataFrame) -> pd.DataFrame:
    """
    Find the best rule for each ticker-style assumption set.
    """

    rows = []

    grouped = summary_df.groupby(
        "Ticker_Label",
        observed=False,
    )

    for ticker_label, group_df in grouped:
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
                "Ticker_Label": ticker_label,
                "Inferred_Regime_Name": best["Inferred_Regime_Name"],
                "Best_Rule_Label": best["Rule_Label"],
                "Best_Mean_Outperformance": best["Mean_Outperformance"],
                "Second_Best_Rule_Label": second_label,
                "Second_Best_Mean_Outperformance": second_outperformance,
                "Outperformance_Edge": edge,
                "Material_Edge": abs(edge) >= MATERIALITY_THRESHOLD,
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

    winners_df["Ticker_Label"] = pd.Categorical(
        winners_df["Ticker_Label"],
        categories=TICKER_ORDER,
        ordered=True,
    )

    winners_df = winners_df.sort_values(
        ["Ticker_Label"]
    ).reset_index(drop=True)

    return winners_df


def build_report(
    summary_df: pd.DataFrame,
    winners_df: pd.DataFrame,
) -> str:
    """
    Build a plain-text ticker calibration report.
    """

    lines = []

    lines.append("COVERED CALL SIMULATOR - TICKER CALIBRATION REPORT")
    lines.append("=" * 100)
    lines.append("")
    lines.append(f"Paths per experiment:       {N_PATHS}")
    lines.append(f"Materiality threshold:      {MATERIALITY_THRESHOLD:.4f}")
    lines.append(f"Summary file:               {SUMMARY_PATH}")
    lines.append(f"Winners file:               {WINNERS_PATH}")
    lines.append("")

    lines.append("-" * 100)
    lines.append("Ticker assumptions")
    lines.append("-" * 100)
    lines.append("")

    for ticker_label in TICKER_ORDER:
        settings = TICKER_CONFIGS[ticker_label]
        inferred_regime = infer_regime_name_from_ticker_settings(
            annual_return=settings["annual_return"],
            annual_volatility=settings["annual_volatility"],
        )

        lines.append(f"{ticker_label}:")
        lines.append(f"    annual_return:      {settings['annual_return']:.4f}")
        lines.append(f"    annual_volatility:  {settings['annual_volatility']:.4f}")
        lines.append(f"    dte:                {settings['dte']}")
        lines.append(f"    target_delta:       {settings['target_delta']:.2f}")
        lines.append(f"    inferred_regime:    {inferred_regime}")
        lines.append("")

    lines.append("-" * 100)
    lines.append("Winner summary")
    lines.append("-" * 100)
    lines.append("")

    for _, row in winners_df.iterrows():
        lines.append(
            f"{row['Ticker_Label']:<12} | "
            f"Regime={row['Inferred_Regime_Name']:<16} | "
            f"Best={row['Best_Rule_Label']:<32} | "
            f"Outperf={format_decimal(row['Best_Mean_Outperformance'])} | "
            f"Second={row['Second_Best_Rule_Label']:<32} | "
            f"Edge={format_decimal(row['Outperformance_Edge'])} | "
            f"Material={row['Material_Edge']} | "
            f"Net option={format_currency(row['Best_Mean_Net_Option_Effect'])} | "
            f"Cost={format_currency(row['Best_Mean_Total_Transaction_Cost'])}"
        )

    lines.append("")
    lines.append("-" * 100)
    lines.append("Rule details by ticker")
    lines.append("-" * 100)
    lines.append("")

    for ticker_label in TICKER_ORDER:
        ticker_df = summary_df[
            summary_df["Ticker_Label"].astype(str) == ticker_label
        ].copy()

        lines.append(f"Ticker assumption set: {ticker_label}")
        lines.append("-" * 100)

        if ticker_df.empty:
            lines.append("No data available.")
            lines.append("")
            continue

        for _, row in ticker_df.iterrows():
            lines.append(
                f"    {str(row['Rule_Label']):<34} | "
                f"Outperf={format_decimal(row['Mean_Outperformance'])} | "
                f"Net option={format_currency(row['Mean_Net_Option_Effect'])} | "
                f"Cost={format_currency(row['Mean_Total_Transaction_Cost'])} | "
                f"Cycles={format_decimal(row['Mean_Option_Cycles'], 2)} | "
                f"Assignments={format_decimal(row['Mean_Assignments'], 2)}"
            )

        lines.append("")

    lines.append("=" * 100)
    lines.append("Interpretation")
    lines.append("=" * 100)
    lines.append("")
    lines.append(
        "This script uses ticker-like assumptions rather than historical ticker "
        "data. The purpose is to see how the current rules behave under "
        "plausible return and volatility profiles."
    )
    lines.append("")
    lines.append(
        "The inferred regime is used only so the adaptive rules know which "
        "branch to follow. Later, this can be replaced with a real regime "
        "classification model."
    )
    lines.append("")
    lines.append(
        "Do not overinterpret small edges. A result is treated as material only "
        f"when the outperformance edge is at least {MATERIALITY_THRESHOLD:.4f}."
    )
    lines.append("")
    lines.append(
        "If a ticker-like assumption set produces a rule preference that differs "
        "from the current adaptive decision map by a material amount, it may "
        "justify adding ticker-specific calibration to the simulator."
    )

    return "\n".join(lines)


# =============================================================================
# Charts
# =============================================================================

def save_grouped_bar_chart(
    summary_df: pd.DataFrame,
    metric: str,
    title: str,
    ylabel: str,
    output_path: Path,
) -> None:
    """
    Save a grouped bar chart by ticker assumption and rule.
    """

    plot_df = summary_df.copy()
    plot_df[metric] = pd.to_numeric(plot_df[metric], errors="coerce")
    plot_df = plot_df.dropna(subset=[metric])

    if plot_df.empty:
        return

    pivot = plot_df.pivot(
        index="Ticker_Label",
        columns="Rule_Label",
        values=metric,
    )

    pivot = pivot.reindex(TICKER_ORDER)
    pivot = pivot[RULE_ORDER]

    ax = pivot.plot(kind="bar", figsize=(15, 7))
    ax.axhline(0, linewidth=1)
    ax.set_title(title)
    ax.set_xlabel("Ticker Assumption Set")
    ax.set_ylabel(ylabel)

    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()


def save_charts(summary_df: pd.DataFrame) -> None:
    """
    Save ticker calibration charts.
    """

    save_grouped_bar_chart(
        summary_df=summary_df,
        metric="Mean_Outperformance",
        title="Ticker Calibration - Mean Outperformance",
        ylabel="Mean Outperformance",
        output_path=OUTPERFORMANCE_CHART_PATH,
    )

    save_grouped_bar_chart(
        summary_df=summary_df,
        metric="Mean_Net_Option_Effect",
        title="Ticker Calibration - Mean Net Option Effect",
        ylabel="Mean Net Option Effect",
        output_path=NET_EFFECT_CHART_PATH,
    )

    save_grouped_bar_chart(
        summary_df=summary_df,
        metric="Mean_Total_Transaction_Cost",
        title="Ticker Calibration - Mean Transaction Cost",
        ylabel="Mean Transaction Cost",
        output_path=TRANSACTION_COST_CHART_PATH,
    )


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_CHART_DIR.mkdir(parents=True, exist_ok=True)

    summary_df = run_ticker_calibration()
    winners_df = build_winners_table(summary_df)

    summary_df.to_csv(SUMMARY_PATH, index=False)
    winners_df.to_csv(WINNERS_PATH, index=False)

    report_text = build_report(summary_df, winners_df)
    REPORT_PATH.write_text(report_text, encoding="utf-8")

    save_charts(summary_df)

    print("")
    print("=" * 100)
    print("Ticker calibration complete.")
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