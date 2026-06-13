"""
historical_window_calibration.py

Historical window calibration for the Covered Call Simulator.

This script reads historical ticker price CSV files from:

    data/historical_prices

It tests whether the preferred covered-call management rule changes when the
historical calibration window changes.

This is a standalone diagnostic script.

It does not modify app/main.py.

Input files:

    data/historical_prices/SPY.csv
    data/historical_prices/QQQ.csv
    data/historical_prices/IWM.csv
    data/historical_prices/TQQQ.csv
    data/historical_prices/SOXL.csv

Each file should contain at least:

    Date
    Close

or:

    Date
    Adj Close

Windows tested:

    252 trading days   roughly 1 year
    504 trading days   roughly 2 years
    756 trading days   roughly 3 years
    1260 trading days  roughly 5 years
    full available history in the CSV

Outputs:

    outputs/tables/comparison/historical_window_calibration_summary.csv
    outputs/tables/comparison/historical_window_calibration_winners.csv
    outputs/tables/comparison/historical_window_calibration_report.txt

Purpose:

    The previous historical ticker calibration used the full downloaded
    historical period.

    This script checks whether the result is stable across different lookback
    windows.

    If the same practical rule keeps winning across windows, the result is
    more robust.

    If the best rule changes materially by window, then historical calibration
    should remain diagnostic and should not drive automatic recommendations yet.
"""

import copy
import sys
from pathlib import Path

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
from app.regime_detection import detect_regime


# =============================================================================
# User settings
# =============================================================================

N_PATHS = 250

TRADING_DAYS_PER_YEAR = 252

MATERIALITY_THRESHOLD = 0.0050

TICKERS = [
    "SPY",
    "QQQ",
    "IWM",
    "TQQQ",
    "SOXL",
]

WINDOW_CONFIGS = [
    {
        "Window_Label": "1Y",
        "Window_Trading_Days": 252,
        "Use_Full_History": False,
    },
    {
        "Window_Label": "2Y",
        "Window_Trading_Days": 504,
        "Use_Full_History": False,
    },
    {
        "Window_Label": "3Y",
        "Window_Trading_Days": 756,
        "Use_Full_History": False,
    },
    {
        "Window_Label": "5Y",
        "Window_Trading_Days": 1260,
        "Use_Full_History": False,
    },
    {
        "Window_Label": "Full",
        "Window_Trading_Days": None,
        "Use_Full_History": True,
    },
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
    "AdaptiveRegimeDTECost": {
        "management_rule": "adaptive_by_regime_dte_cost",
        "wait_days_after_profit_close": 0,
        "pullback_fraction_after_profit_close": 0.0,
        "max_wait_days_after_profit_close": 0,
        "adaptive_wait_days_after_profit_close": 10,
    },
}

RULE_ORDER = list(RULE_CONFIGS.keys())


# =============================================================================
# Paths
# =============================================================================

DATA_DIR = PROJECT_ROOT / "data" / "historical_prices"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "comparison"

SUMMARY_PATH = OUTPUT_TABLE_DIR / "historical_window_calibration_summary.csv"
WINNERS_PATH = OUTPUT_TABLE_DIR / "historical_window_calibration_winners.csv"
REPORT_PATH = OUTPUT_TABLE_DIR / "historical_window_calibration_report.txt"


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


def format_percent(value: object, digits: int = 2) -> str:
    """
    Format decimal values as percentages.
    """

    value = pd.to_numeric(value, errors="coerce")

    if pd.isna(value):
        return "NA"

    return f"{100.0 * float(value):,.{digits}f}%"


def format_currency(value: object) -> str:
    """
    Format dollar values.
    """

    value = pd.to_numeric(value, errors="coerce")

    if pd.isna(value):
        return "NA"

    return f"${float(value):,.2f}"


def find_price_column(df: pd.DataFrame) -> str:
    """
    Find the best available price column.
    """

    possible_columns = [
        "Adj Close",
        "Adj_Close",
        "Adjusted Close",
        "Adjusted_Close",
        "Close",
        "close",
    ]

    for column in possible_columns:
        if column in df.columns:
            return column

    raise ValueError(
        "Could not find a price column. Expected one of: "
        "Adj Close, Adj_Close, Adjusted Close, Adjusted_Close, Close, close."
    )


def read_price_file(ticker: str) -> pd.DataFrame:
    """
    Read one historical price CSV file.
    """

    csv_path = DATA_DIR / f"{ticker}.csv"

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Missing historical price file: {csv_path}"
        )

    df = pd.read_csv(csv_path)

    if "Date" not in df.columns and "date" not in df.columns:
        raise ValueError(
            f"{csv_path} must contain a Date column."
        )

    date_column = "Date" if "Date" in df.columns else "date"
    price_column = find_price_column(df)

    clean_df = df[[date_column, price_column]].copy()
    clean_df.columns = ["Date", "Price"]

    clean_df["Date"] = pd.to_datetime(
        clean_df["Date"],
        errors="coerce",
    )

    clean_df["Price"] = pd.to_numeric(
        clean_df["Price"],
        errors="coerce",
    )

    clean_df = clean_df.dropna(subset=["Date", "Price"])
    clean_df = clean_df.sort_values("Date").reset_index(drop=True)

    if len(clean_df) < 30:
        raise ValueError(
            f"{csv_path} has fewer than 30 valid price rows."
        )

    return clean_df


def slice_price_window(
    price_df: pd.DataFrame,
    window_config: dict,
) -> pd.DataFrame:
    """
    Slice a historical price DataFrame to the requested calibration window.
    """

    df = price_df.copy()

    if window_config["Use_Full_History"]:
        return df.reset_index(drop=True)

    window_days = int(window_config["Window_Trading_Days"])

    if len(df) <= window_days:
        return df.reset_index(drop=True)

    return df.tail(window_days + 1).reset_index(drop=True)


def estimate_ticker_statistics(price_df: pd.DataFrame) -> dict:
    """
    Estimate annual return and annual volatility from historical prices.

    Annual return is estimated using compound growth over the observed period.

    Annual volatility is estimated from daily simple returns.
    """

    df = price_df.copy()

    df["Daily_Return"] = df["Price"].pct_change()
    df = df.dropna(subset=["Daily_Return"])

    if df.empty:
        raise ValueError("No valid daily returns could be computed.")

    start_price = float(price_df["Price"].iloc[0])
    end_price = float(price_df["Price"].iloc[-1])

    start_date = price_df["Date"].iloc[0]
    end_date = price_df["Date"].iloc[-1]

    calendar_days = max((end_date - start_date).days, 1)
    years = calendar_days / 365.25

    cumulative_return = (end_price / start_price) - 1.0

    if start_price <= 0 or end_price <= 0 or years <= 0:
        annual_return = float("nan")
    else:
        annual_return = (end_price / start_price) ** (1.0 / years) - 1.0

    annual_volatility = (
        float(df["Daily_Return"].std())
        * (TRADING_DAYS_PER_YEAR ** 0.5)
    )

    return {
        "Start_Date": start_date,
        "End_Date": end_date,
        "Trading_Rows": int(len(price_df)),
        "Return_Rows": int(len(df)),
        "Start_Price": start_price,
        "End_Price": end_price,
        "Years": years,
        "Cumulative_Return": cumulative_return,
        "Annual_Return": annual_return,
        "Annual_Volatility": annual_volatility,
    }


# =============================================================================
# Simulation
# =============================================================================

def build_config(
    ticker_stats: dict,
    rule_label: str,
) -> SimulationConfig:
    """
    Build one simulation config from ticker statistics and rule label.
    """

    base_config = SimulationConfig()

    annual_return = float(ticker_stats["Annual_Return"])
    annual_volatility = float(ticker_stats["Annual_Volatility"])

    detected_regime = detect_regime(
        annual_return=annual_return,
        annual_volatility=annual_volatility,
    )

    rule_settings = RULE_CONFIGS[rule_label]

    config = clone_config(
        base_config,
        n_paths=N_PATHS,
        annual_return=annual_return,
        annual_volatility=annual_volatility,
        regime_name=detected_regime,
        **rule_settings,
    )

    return config


def run_single_experiment(
    ticker: str,
    window_label: str,
    ticker_stats: dict,
    rule_label: str,
) -> dict:
    """
    Run one ticker/window/rule experiment.
    """

    experiment_name = f"{ticker}__{window_label}__{rule_label}"

    print("=" * 100)
    print(f"Running experiment: {experiment_name}")
    print("=" * 100)

    config = build_config(
        ticker_stats=ticker_stats,
        rule_label=rule_label,
    )

    engine = SimulationEngine(config)
    path_results_df = engine.run()

    detected_regime = detect_regime(
        annual_return=float(ticker_stats["Annual_Return"]),
        annual_volatility=float(ticker_stats["Annual_Volatility"]),
    )

    summary = {
        "Ticker": ticker,
        "Window_Label": window_label,
        "Start_Date": ticker_stats["Start_Date"],
        "End_Date": ticker_stats["End_Date"],
        "Trading_Rows": ticker_stats["Trading_Rows"],
        "Return_Rows": ticker_stats["Return_Rows"],
        "Start_Price": ticker_stats["Start_Price"],
        "End_Price": ticker_stats["End_Price"],
        "Years": ticker_stats["Years"],
        "Cumulative_Return": ticker_stats["Cumulative_Return"],
        "Annual_Return": ticker_stats["Annual_Return"],
        "Annual_Volatility": ticker_stats["Annual_Volatility"],
        "Detected_Regime": detected_regime,
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


def run_historical_window_calibration() -> pd.DataFrame:
    """
    Run historical window calibration for all available tickers/windows.
    """

    rows = []
    available_tickers = []

    for ticker in TICKERS:
        csv_path = DATA_DIR / f"{ticker}.csv"

        if csv_path.exists():
            available_tickers.append(ticker)
        else:
            print(f"Skipping {ticker}: missing {csv_path}")

    if not available_tickers:
        raise FileNotFoundError(
            "No historical ticker CSV files were found. "
            f"Expected files in: {DATA_DIR}"
        )

    total_experiments = (
        len(available_tickers)
        * len(WINDOW_CONFIGS)
        * len(RULE_ORDER)
    )

    print("")
    print("=" * 100)
    print("COVERED CALL SIMULATOR - HISTORICAL WINDOW CALIBRATION")
    print("=" * 100)
    print(f"Paths per experiment: {N_PATHS}")
    print(f"Data folder:          {DATA_DIR}")
    print(f"Tickers found:        {available_tickers}")
    print(f"Windows tested:       {[w['Window_Label'] for w in WINDOW_CONFIGS]}")
    print(f"Rules tested:         {RULE_ORDER}")
    print(f"Total experiments:    {total_experiments}")
    print("=" * 100)
    print("")

    experiment_count = 0

    for ticker in available_tickers:
        full_price_df = read_price_file(ticker)

        for window_config in WINDOW_CONFIGS:
            window_label = str(window_config["Window_Label"])
            window_price_df = slice_price_window(
                price_df=full_price_df,
                window_config=window_config,
            )

            ticker_stats = estimate_ticker_statistics(window_price_df)

            for rule_label in RULE_ORDER:
                experiment_count += 1
                print(f"Progress: {experiment_count} of {total_experiments}")

                summary = run_single_experiment(
                    ticker=ticker,
                    window_label=window_label,
                    ticker_stats=ticker_stats,
                    rule_label=rule_label,
                )

                rows.append(summary)

    summary_df = pd.DataFrame(rows)

    summary_df["Rule_Label"] = pd.Categorical(
        summary_df["Rule_Label"],
        categories=RULE_ORDER,
        ordered=True,
    )

    window_order = [
        window_config["Window_Label"]
        for window_config in WINDOW_CONFIGS
    ]

    summary_df["Window_Label"] = pd.Categorical(
        summary_df["Window_Label"],
        categories=window_order,
        ordered=True,
    )

    summary_df = summary_df.sort_values(
        ["Ticker", "Window_Label", "Rule_Label"]
    ).reset_index(drop=True)

    return summary_df


# =============================================================================
# Analysis and report
# =============================================================================

def find_best_rule(group_df: pd.DataFrame) -> pd.Series | None:
    """
    Find best rule in one ticker/window group.
    """

    df = group_df.copy()
    df["Mean_Outperformance"] = pd.to_numeric(
        df["Mean_Outperformance"],
        errors="coerce",
    )
    df = df.dropna(subset=["Mean_Outperformance"])

    if df.empty:
        return None

    idx = df["Mean_Outperformance"].idxmax()
    return df.loc[idx]


def build_winners_table(summary_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build one row per ticker/window showing best rule and adaptive comparison.
    """

    rows = []

    group_columns = [
        "Ticker",
        "Window_Label",
    ]

    for (ticker, window_label), group_df in summary_df.groupby(
        group_columns,
        observed=False,
    ):
        best = find_best_rule(group_df)

        if best is None:
            continue

        adaptive_row = group_df[
            group_df["Rule_Label"].astype(str)
            == "AdaptiveRegimeDTECost"
        ]

        adaptive_outperformance = float("nan")

        if not adaptive_row.empty:
            adaptive_outperformance = float(
                pd.to_numeric(
                    adaptive_row.iloc[0]["Mean_Outperformance"],
                    errors="coerce",
                )
            )

        best_outperformance = float(best["Mean_Outperformance"])
        adaptive_minus_best = adaptive_outperformance - best_outperformance

        adaptive_materially_worse = (
            adaptive_minus_best < 0
            and abs(adaptive_minus_best) >= MATERIALITY_THRESHOLD
        )

        rows.append(
            {
                "Ticker": ticker,
                "Window_Label": window_label,
                "Start_Date": best["Start_Date"],
                "End_Date": best["End_Date"],
                "Trading_Rows": best["Trading_Rows"],
                "Years": best["Years"],
                "Cumulative_Return": best["Cumulative_Return"],
                "Annual_Return": best["Annual_Return"],
                "Annual_Volatility": best["Annual_Volatility"],
                "Detected_Regime": best["Detected_Regime"],
                "Best_Rule": best["Rule_Label"],
                "Best_Outperformance": best_outperformance,
                "Adaptive_Outperformance": adaptive_outperformance,
                "Adaptive_Minus_Best": adaptive_minus_best,
                "Adaptive_Materially_Worse": adaptive_materially_worse,
            }
        )

    winners_df = pd.DataFrame(rows)

    if not winners_df.empty:
        winners_df = winners_df.sort_values(
            ["Ticker", "Window_Label"]
        ).reset_index(drop=True)

    return winners_df


def build_stability_table(winners_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a compact table showing best-rule stability by ticker.
    """

    if winners_df.empty:
        return pd.DataFrame()

    rows = []

    for ticker in sorted(winners_df["Ticker"].astype(str).unique()):
        ticker_df = winners_df[
            winners_df["Ticker"].astype(str) == ticker
        ].copy()

        best_rules = sorted(ticker_df["Best_Rule"].astype(str).unique())
        regimes = sorted(ticker_df["Detected_Regime"].astype(str).unique())

        adaptive_worse_count = int(
            ticker_df["Adaptive_Materially_Worse"].fillna(False).sum()
        )

        rows.append(
            {
                "Ticker": ticker,
                "Windows_Tested": len(ticker_df),
                "Unique_Best_Rules": ", ".join(best_rules),
                "Best_Rule_Count": len(best_rules),
                "Detected_Regimes": ", ".join(regimes),
                "Regime_Count": len(regimes),
                "Adaptive_Materially_Worse_Count": adaptive_worse_count,
                "Stable_Best_Rule": len(best_rules) == 1,
                "Stable_Regime": len(regimes) == 1,
            }
        )

    return pd.DataFrame(rows)


def build_report(
    summary_df: pd.DataFrame,
    winners_df: pd.DataFrame,
    stability_df: pd.DataFrame,
) -> str:
    """
    Build a plain-text historical window calibration report.
    """

    lines = []

    lines.append("COVERED CALL SIMULATOR - HISTORICAL WINDOW CALIBRATION REPORT")
    lines.append("=" * 100)
    lines.append("")
    lines.append(f"Paths per experiment:       {N_PATHS}")
    lines.append(f"Materiality threshold:      {MATERIALITY_THRESHOLD:.4f}")
    lines.append(f"Data folder:                {DATA_DIR}")
    lines.append(f"Summary file:               {SUMMARY_PATH}")
    lines.append(f"Winners file:               {WINNERS_PATH}")
    lines.append("")
    lines.append(
        "This report tests whether the preferred covered-call management rule "
        "changes when the historical calibration window changes."
    )
    lines.append("")
    lines.append(
        "Each ticker/window estimate is passed into the rule-based regime "
        "detector. The simulator then compares the key covered-call "
        "management rules under that detected regime."
    )
    lines.append("")
    lines.append(
        "This is a standalone diagnostic. It should not be wired into "
        "app/main.py unless the calibration-window policy is finalized."
    )
    lines.append("")

    if summary_df.empty:
        lines.append("No simulations were completed.")
        return "\n".join(lines)

    lines.append("-" * 100)
    lines.append("Best-rule stability by ticker")
    lines.append("-" * 100)
    lines.append("")

    for _, row in stability_df.iterrows():
        lines.append(f"Ticker: {row['Ticker']}")
        lines.append(f"    Windows tested:                    {row['Windows_Tested']}")
        lines.append(f"    Unique best rules:                 {row['Unique_Best_Rules']}")
        lines.append(f"    Best rule count:                   {row['Best_Rule_Count']}")
        lines.append(f"    Stable best rule:                  {row['Stable_Best_Rule']}")
        lines.append(f"    Detected regimes:                  {row['Detected_Regimes']}")
        lines.append(f"    Regime count:                      {row['Regime_Count']}")
        lines.append(f"    Stable regime:                     {row['Stable_Regime']}")
        lines.append(
            f"    Adaptive materially worse count:   "
            f"{row['Adaptive_Materially_Worse_Count']}"
        )
        lines.append("")

    lines.append("-" * 100)
    lines.append("Ticker/window conclusions")
    lines.append("-" * 100)
    lines.append("")

    for _, row in winners_df.iterrows():
        lines.append(f"Ticker: {row['Ticker']} | Window: {row['Window_Label']}")
        lines.append(f"    Start date:                  {row['Start_Date']}")
        lines.append(f"    End date:                    {row['End_Date']}")
        lines.append(f"    Years:                       {format_decimal(row['Years'], 2)}")
        lines.append(
            f"    Cumulative return:           "
            f"{format_percent(row['Cumulative_Return'])}"
        )
        lines.append(f"    Annual return:               {format_percent(row['Annual_Return'])}")
        lines.append(
            f"    Annual volatility:           "
            f"{format_percent(row['Annual_Volatility'])}"
        )
        lines.append(f"    Detected regime:             {row['Detected_Regime']}")
        lines.append(f"    Best rule:                   {row['Best_Rule']}")
        lines.append(
            f"    Best outperformance:         "
            f"{format_decimal(row['Best_Outperformance'])}"
        )
        lines.append(
            f"    Adaptive outperformance:     "
            f"{format_decimal(row['Adaptive_Outperformance'])}"
        )
        lines.append(
            f"    Adaptive minus best:         "
            f"{format_decimal(row['Adaptive_Minus_Best'])}"
        )
        lines.append(
            f"    Adaptive materially worse:   "
            f"{row['Adaptive_Materially_Worse']}"
        )
        lines.append("")

    lines.append("-" * 100)
    lines.append("Detailed rule results")
    lines.append("-" * 100)
    lines.append("")

    for ticker in sorted(summary_df["Ticker"].astype(str).unique()):
        ticker_df = summary_df[
            summary_df["Ticker"].astype(str) == ticker
        ].copy()

        lines.append(f"Ticker: {ticker}")

        for window_label in [
            window_config["Window_Label"]
            for window_config in WINDOW_CONFIGS
        ]:
            window_df = ticker_df[
                ticker_df["Window_Label"].astype(str) == str(window_label)
            ].copy()

            if window_df.empty:
                continue

            first_row = window_df.iloc[0]

            lines.append(f"    Window: {window_label}")
            lines.append(
                f"        Annual return:       "
                f"{format_percent(first_row['Annual_Return'])}"
            )
            lines.append(
                f"        Annual volatility:   "
                f"{format_percent(first_row['Annual_Volatility'])}"
            )
            lines.append(f"        Detected regime:     {first_row['Detected_Regime']}")
            lines.append("")

            for _, row in window_df.iterrows():
                lines.append(
                    f"            {str(row['Rule_Label']):<32} | "
                    f"Outperf={format_decimal(row['Mean_Outperformance'])} | "
                    f"Net option={format_currency(row['Mean_Net_Option_Effect'])} | "
                    f"Cost={format_currency(row['Mean_Total_Transaction_Cost'])} | "
                    f"Cycles={format_decimal(row['Mean_Option_Cycles'], 2)}"
                )

            lines.append("")

    adaptive_worse_count = 0

    if not winners_df.empty:
        adaptive_worse_count = int(
            winners_df["Adaptive_Materially_Worse"].fillna(False).sum()
        )

    unstable_best_rule_count = 0

    if not stability_df.empty:
        unstable_best_rule_count = int(
            (~stability_df["Stable_Best_Rule"].fillna(False)).sum()
        )

    lines.append("=" * 100)
    lines.append("Overall conclusion")
    lines.append("=" * 100)
    lines.append("")
    lines.append(f"Ticker/window cases completed:   {len(winners_df)}")
    lines.append(f"Adaptive materially worse cases: {adaptive_worse_count}")
    lines.append(f"Tickers with unstable best rule: {unstable_best_rule_count}")
    lines.append("")

    if adaptive_worse_count == 0:
        lines.append(
            "The adaptive DTE/cost rule was not materially worse than the best "
            "rule in any completed ticker/window case."
        )
    else:
        lines.append(
            "At least one ticker/window case showed material adaptive-rule "
            "underperformance. Review those cases before using historical "
            "window calibration to drive recommendations."
        )

    lines.append("")

    if unstable_best_rule_count == 0:
        lines.append(
            "The best rule was stable across all tested historical windows for "
            "every completed ticker."
        )
    else:
        lines.append(
            "At least one ticker had a different best rule across calibration "
            "windows. This means the selected calibration window matters."
        )

    lines.append("")
    lines.append(
        "Recommendation: keep this script as a standalone diagnostic. Do not "
        "wire historical window calibration into app/main.py unless the "
        "calibration-window policy is finalized."
    )

    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)

    summary_df = run_historical_window_calibration()
    winners_df = build_winners_table(summary_df)
    stability_df = build_stability_table(winners_df)

    summary_df.to_csv(SUMMARY_PATH, index=False)
    winners_df.to_csv(WINNERS_PATH, index=False)

    report_text = build_report(
        summary_df=summary_df,
        winners_df=winners_df,
        stability_df=stability_df,
    )

    REPORT_PATH.write_text(report_text, encoding="utf-8")

    print("")
    print("=" * 100)
    print("Historical window calibration complete.")
    print("=" * 100)
    print("")
    print("Saved files:")
    print(f"  {SUMMARY_PATH}")
    print(f"  {WINNERS_PATH}")
    print(f"  {REPORT_PATH}")
    print("")
    print("Done.")
    print("")


if __name__ == "__main__":
    main()