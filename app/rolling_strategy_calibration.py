"""
rolling_strategy_calibration.py

Rolling-window strategy calibration for the Covered Call Simulator.

This script reads historical ticker price CSV files from:

    data/historical_prices

It creates rolling historical windows, estimates annual return and annual
volatility for each window, detects the market regime, and then runs the key
covered-call management rules for each rolling window.

This is different from rolling_regime_detection.py.

rolling_regime_detection.py:
    Detects the regime over rolling windows.

rolling_strategy_calibration.py:
    Detects the regime AND tests which covered-call management rule would
    have been preferred over each rolling window.

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

Outputs:

    outputs/tables/comparison/rolling_strategy_calibration_summary.csv
    outputs/tables/comparison/rolling_strategy_calibration_winners.csv
    outputs/tables/comparison/rolling_strategy_calibration_stability.csv
    outputs/tables/comparison/rolling_strategy_calibration_report.txt

Purpose:

    This script tests whether the preferred covered-call rule is stable across
    rolling historical calibration windows.

    If Wait10d remains dominant across rolling windows, that strengthens the
    evidence that immediate reselling after a 50% profit creates too much
    upside drag in upward-drifting markets.

Important:

    This script may take longer than prior diagnostics because it runs many
    Monte Carlo experiments.

    To keep runtime reasonable, it uses a rolling step size rather than testing
    every possible day.

Default settings:

    Rolling window:       252 trading days
    Rolling step:         63 trading days
    Paths per experiment: 250
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

# Rolling strategy calibration settings.
#
# 252 trading days = roughly 1 year.
# 63 trading days  = roughly 1 quarter.
#
# This gives a reasonable number of overlapping windows without making the
# script too slow.
ROLLING_WINDOW_DAYS = 252
ROLLING_STEP_DAYS = 63

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

SUMMARY_PATH = OUTPUT_TABLE_DIR / "rolling_strategy_calibration_summary.csv"
WINNERS_PATH = OUTPUT_TABLE_DIR / "rolling_strategy_calibration_winners.csv"
STABILITY_PATH = OUTPUT_TABLE_DIR / "rolling_strategy_calibration_stability.csv"
REPORT_PATH = OUTPUT_TABLE_DIR / "rolling_strategy_calibration_report.txt"


# =============================================================================
# Formatting helpers
# =============================================================================

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


# =============================================================================
# Data helpers
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


def find_price_column(df: pd.DataFrame) -> str:
    """
    Find the best available historical price column.
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

    if len(clean_df) < ROLLING_WINDOW_DAYS + 1:
        raise ValueError(
            f"{csv_path} has fewer rows than needed for a "
            f"{ROLLING_WINDOW_DAYS}-day rolling window."
        )

    return clean_df


def build_rolling_windows(
    ticker: str,
    price_df: pd.DataFrame,
) -> list[dict]:
    """
    Build rolling window slices for one ticker.

    Each rolling window has ROLLING_WINDOW_DAYS + 1 price rows so that
    pct_change can produce ROLLING_WINDOW_DAYS daily returns.
    """

    windows = []

    window_row_count = ROLLING_WINDOW_DAYS + 1

    start_indices = list(
        range(
            0,
            len(price_df) - window_row_count + 1,
            ROLLING_STEP_DAYS,
        )
    )

    # Ensure the most recent window is included.
    latest_start_index = len(price_df) - window_row_count

    if latest_start_index not in start_indices:
        start_indices.append(latest_start_index)

    start_indices = sorted(set(start_indices))

    for window_number, start_index in enumerate(start_indices, start=1):
        end_index = start_index + window_row_count

        window_df = price_df.iloc[start_index:end_index].copy()
        window_df = window_df.reset_index(drop=True)

        windows.append(
            {
                "Ticker": ticker,
                "Window_Number": window_number,
                "Start_Index": start_index,
                "End_Index": end_index - 1,
                "Window_Data": window_df,
            }
        )

    return windows


def estimate_window_statistics(price_df: pd.DataFrame) -> dict:
    """
    Estimate annual return and annual volatility from one rolling window.

    Annual return is estimated using compound growth over the observed
    calendar period.

    Annual volatility is estimated from daily simple returns.
    """

    df = price_df.copy()

    df["Daily_Return"] = df["Price"].pct_change()
    return_df = df.dropna(subset=["Daily_Return"]).copy()

    if return_df.empty:
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
        float(return_df["Daily_Return"].std())
        * (TRADING_DAYS_PER_YEAR ** 0.5)
    )

    return {
        "Start_Date": start_date,
        "End_Date": end_date,
        "Trading_Rows": int(len(price_df)),
        "Return_Rows": int(len(return_df)),
        "Start_Price": start_price,
        "End_Price": end_price,
        "Years": years,
        "Cumulative_Return": cumulative_return,
        "Annual_Return": annual_return,
        "Annual_Volatility": annual_volatility,
    }


# =============================================================================
# Simulation helpers
# =============================================================================

def build_config(
    window_stats: dict,
    rule_label: str,
) -> SimulationConfig:
    """
    Build one simulation config from window statistics and rule label.
    """

    base_config = SimulationConfig()

    annual_return = float(window_stats["Annual_Return"])
    annual_volatility = float(window_stats["Annual_Volatility"])

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
    window_number: int,
    window_stats: dict,
    rule_label: str,
) -> dict:
    """
    Run one ticker/window/rule experiment.
    """

    experiment_name = f"{ticker}__Window{window_number:03d}__{rule_label}"

    print("=" * 100)
    print(f"Running experiment: {experiment_name}")
    print("=" * 100)

    config = build_config(
        window_stats=window_stats,
        rule_label=rule_label,
    )

    engine = SimulationEngine(config)
    path_results_df = engine.run()

    detected_regime = detect_regime(
        annual_return=float(window_stats["Annual_Return"]),
        annual_volatility=float(window_stats["Annual_Volatility"]),
    )

    summary = {
        "Ticker": ticker,
        "Window_Number": window_number,
        "Start_Date": window_stats["Start_Date"],
        "End_Date": window_stats["End_Date"],
        "Trading_Rows": window_stats["Trading_Rows"],
        "Return_Rows": window_stats["Return_Rows"],
        "Start_Price": window_stats["Start_Price"],
        "End_Price": window_stats["End_Price"],
        "Years": window_stats["Years"],
        "Cumulative_Return": window_stats["Cumulative_Return"],
        "Annual_Return": window_stats["Annual_Return"],
        "Annual_Volatility": window_stats["Annual_Volatility"],
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


def run_rolling_strategy_calibration() -> pd.DataFrame:
    """
    Run rolling strategy calibration for all available tickers/windows/rules.
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

    rolling_windows_by_ticker = {}

    total_rolling_windows = 0

    for ticker in available_tickers:
        price_df = read_price_file(ticker)
        rolling_windows = build_rolling_windows(
            ticker=ticker,
            price_df=price_df,
        )
        rolling_windows_by_ticker[ticker] = rolling_windows
        total_rolling_windows += len(rolling_windows)

    total_experiments = total_rolling_windows * len(RULE_ORDER)

    print("")
    print("=" * 100)
    print("COVERED CALL SIMULATOR - ROLLING STRATEGY CALIBRATION")
    print("=" * 100)
    print(f"Paths per experiment:      {N_PATHS}")
    print(f"Data folder:               {DATA_DIR}")
    print(f"Tickers found:             {available_tickers}")
    print(f"Rolling window days:       {ROLLING_WINDOW_DAYS}")
    print(f"Rolling step days:         {ROLLING_STEP_DAYS}")
    print(f"Rolling windows created:   {total_rolling_windows}")
    print(f"Rules tested:              {RULE_ORDER}")
    print(f"Total experiments:         {total_experiments}")
    print("=" * 100)
    print("")

    experiment_count = 0

    for ticker in available_tickers:
        rolling_windows = rolling_windows_by_ticker[ticker]

        for window_info in rolling_windows:
            window_number = int(window_info["Window_Number"])
            window_df = window_info["Window_Data"]

            window_stats = estimate_window_statistics(window_df)

            for rule_label in RULE_ORDER:
                experiment_count += 1

                print(
                    f"Progress: {experiment_count} of {total_experiments}"
                )

                summary = run_single_experiment(
                    ticker=ticker,
                    window_number=window_number,
                    window_stats=window_stats,
                    rule_label=rule_label,
                )

                rows.append(summary)

    summary_df = pd.DataFrame(rows)

    summary_df["Rule_Label"] = pd.Categorical(
        summary_df["Rule_Label"],
        categories=RULE_ORDER,
        ordered=True,
    )

    summary_df = summary_df.sort_values(
        ["Ticker", "Window_Number", "Rule_Label"]
    ).reset_index(drop=True)

    return summary_df


# =============================================================================
# Analysis
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
        "Window_Number",
    ]

    for (ticker, window_number), group_df in summary_df.groupby(
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
                "Window_Number": window_number,
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
            ["Ticker", "Window_Number"]
        ).reset_index(drop=True)

    return winners_df


def build_stability_table(winners_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build stability summary by ticker.
    """

    if winners_df.empty:
        return pd.DataFrame()

    rows = []

    for ticker in sorted(winners_df["Ticker"].astype(str).unique()):
        ticker_df = winners_df[
            winners_df["Ticker"].astype(str) == ticker
        ].copy()

        best_rule_counts = (
            ticker_df["Best_Rule"]
            .astype(str)
            .value_counts()
            .sort_index()
        )

        regime_counts = (
            ticker_df["Detected_Regime"]
            .astype(str)
            .value_counts()
            .sort_index()
        )

        total_windows = len(ticker_df)

        dominant_rule = str(best_rule_counts.idxmax())
        dominant_rule_count = int(best_rule_counts.max())
        dominant_rule_fraction = dominant_rule_count / total_windows

        dominant_regime = str(regime_counts.idxmax())
        dominant_regime_count = int(regime_counts.max())
        dominant_regime_fraction = dominant_regime_count / total_windows

        adaptive_worse_count = int(
            ticker_df["Adaptive_Materially_Worse"].fillna(False).sum()
        )

        rows.append(
            {
                "Ticker": ticker,
                "Rolling_Windows": total_windows,
                "Dominant_Best_Rule": dominant_rule,
                "Dominant_Best_Rule_Count": dominant_rule_count,
                "Dominant_Best_Rule_Fraction": dominant_rule_fraction,
                "Unique_Best_Rules": ", ".join(
                    sorted(ticker_df["Best_Rule"].astype(str).unique())
                ),
                "Best_Rule_Count": int(
                    ticker_df["Best_Rule"].astype(str).nunique()
                ),
                "Dominant_Regime": dominant_regime,
                "Dominant_Regime_Count": dominant_regime_count,
                "Dominant_Regime_Fraction": dominant_regime_fraction,
                "Unique_Regimes": ", ".join(
                    sorted(ticker_df["Detected_Regime"].astype(str).unique())
                ),
                "Regime_Count": int(
                    ticker_df["Detected_Regime"].astype(str).nunique()
                ),
                "Adaptive_Materially_Worse_Count": adaptive_worse_count,
                "Stable_Best_Rule": int(
                    ticker_df["Best_Rule"].astype(str).nunique()
                ) == 1,
                "Stable_Regime": int(
                    ticker_df["Detected_Regime"].astype(str).nunique()
                ) == 1,
            }
        )

    stability_df = pd.DataFrame(rows)
    stability_df = stability_df.sort_values("Ticker").reset_index(drop=True)

    return stability_df


# =============================================================================
# Report
# =============================================================================

def build_report(
    summary_df: pd.DataFrame,
    winners_df: pd.DataFrame,
    stability_df: pd.DataFrame,
) -> str:
    """
    Build a plain-text rolling strategy calibration report.
    """

    lines = []

    lines.append("COVERED CALL SIMULATOR - ROLLING STRATEGY CALIBRATION REPORT")
    lines.append("=" * 100)
    lines.append("")
    lines.append(f"Paths per experiment:       {N_PATHS}")
    lines.append(f"Materiality threshold:      {MATERIALITY_THRESHOLD:.4f}")
    lines.append(f"Rolling window days:        {ROLLING_WINDOW_DAYS}")
    lines.append(f"Rolling step days:          {ROLLING_STEP_DAYS}")
    lines.append(f"Data folder:                {DATA_DIR}")
    lines.append(f"Summary file:               {SUMMARY_PATH}")
    lines.append(f"Winners file:               {WINNERS_PATH}")
    lines.append(f"Stability file:             {STABILITY_PATH}")
    lines.append("")
    lines.append(
        "This report tests whether the preferred covered-call management rule "
        "changes across rolling historical windows."
    )
    lines.append("")
    lines.append(
        "Each rolling window estimate is passed into the rule-based regime "
        "detector. The simulator then compares the key covered-call "
        "management rules under that detected regime."
    )
    lines.append("")
    lines.append(
        "This is a standalone diagnostic. It should not be wired into "
        "app/main.py unless the rolling strategy calibration policy is "
        "finalized."
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
        lines.append(f"    Rolling windows:                   {row['Rolling_Windows']}")
        lines.append(f"    Dominant best rule:                {row['Dominant_Best_Rule']}")
        lines.append(
            f"    Dominant best-rule count:          "
            f"{row['Dominant_Best_Rule_Count']}"
        )
        lines.append(
            f"    Dominant best-rule fraction:       "
            f"{format_percent(row['Dominant_Best_Rule_Fraction'])}"
        )
        lines.append(f"    Unique best rules:                 {row['Unique_Best_Rules']}")
        lines.append(f"    Stable best rule:                  {row['Stable_Best_Rule']}")
        lines.append(f"    Dominant regime:                   {row['Dominant_Regime']}")
        lines.append(
            f"    Dominant regime fraction:          "
            f"{format_percent(row['Dominant_Regime_Fraction'])}"
        )
        lines.append(f"    Unique regimes:                    {row['Unique_Regimes']}")
        lines.append(f"    Stable regime:                     {row['Stable_Regime']}")
        lines.append(
            f"    Adaptive materially worse count:   "
            f"{row['Adaptive_Materially_Worse_Count']}"
        )
        lines.append("")

    lines.append("-" * 100)
    lines.append("Rolling window winners")
    lines.append("-" * 100)
    lines.append("")

    for ticker in sorted(winners_df["Ticker"].astype(str).unique()):
        ticker_df = winners_df[
            winners_df["Ticker"].astype(str) == ticker
        ].copy()

        lines.append(f"Ticker: {ticker}")
        lines.append("")

        for _, row in ticker_df.iterrows():
            lines.append(f"    Window number:              {row['Window_Number']}")
            lines.append(f"        Start date:             {row['Start_Date']}")
            lines.append(f"        End date:               {row['End_Date']}")
            lines.append(
                f"        Cumulative return:      "
                f"{format_percent(row['Cumulative_Return'])}"
            )
            lines.append(
                f"        Annual return:          "
                f"{format_percent(row['Annual_Return'])}"
            )
            lines.append(
                f"        Annual volatility:      "
                f"{format_percent(row['Annual_Volatility'])}"
            )
            lines.append(f"        Detected regime:        {row['Detected_Regime']}")
            lines.append(f"        Best rule:              {row['Best_Rule']}")
            lines.append(
                f"        Best outperformance:    "
                f"{format_decimal(row['Best_Outperformance'])}"
            )
            lines.append(
                f"        Adaptive outperformance:"
                f" {format_decimal(row['Adaptive_Outperformance'])}"
            )
            lines.append(
                f"        Adaptive minus best:    "
                f"{format_decimal(row['Adaptive_Minus_Best'])}"
            )
            lines.append(
                f"        Adaptive worse:         "
                f"{row['Adaptive_Materially_Worse']}"
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
            "rule in any completed rolling-window case."
        )
    else:
        lines.append(
            "At least one rolling-window case showed material adaptive-rule "
            "underperformance. Review those cases before using rolling "
            "strategy calibration to drive recommendations."
        )

    lines.append("")

    if unstable_best_rule_count == 0:
        lines.append(
            "The best rule was stable across rolling windows for every "
            "completed ticker."
        )
    else:
        lines.append(
            "At least one ticker had a different best rule across rolling "
            "windows. This means the rolling strategy calibration result is "
            "not fully stable."
        )

    lines.append("")
    lines.append(
        "Recommendation: keep this script as a standalone diagnostic. Do not "
        "wire rolling strategy calibration into app/main.py unless the "
        "rolling-window policy is finalized."
    )

    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)

    summary_df = run_rolling_strategy_calibration()
    winners_df = build_winners_table(summary_df)
    stability_df = build_stability_table(winners_df)

    summary_df.to_csv(SUMMARY_PATH, index=False)
    winners_df.to_csv(WINNERS_PATH, index=False)
    stability_df.to_csv(STABILITY_PATH, index=False)

    report_text = build_report(
        summary_df=summary_df,
        winners_df=winners_df,
        stability_df=stability_df,
    )

    REPORT_PATH.write_text(report_text, encoding="utf-8")

    print("")
    print("=" * 100)
    print("Rolling strategy calibration complete.")
    print("=" * 100)
    print("")
    print("Saved files:")
    print(f"  {SUMMARY_PATH}")
    print(f"  {WINNERS_PATH}")
    print(f"  {STABILITY_PATH}")
    print(f"  {REPORT_PATH}")
    print("")
    print("Done.")
    print("")


if __name__ == "__main__":
    main()