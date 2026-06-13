"""
rolling_regime_detection.py

Rolling historical regime detection for the Covered Call Simulator.

This script reads historical ticker price CSV files from:

    data/historical_prices

It computes rolling annualized return and rolling annualized volatility, then
passes those rolling estimates into the rule-based regime detector:

    app/regime_detection.py

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

    outputs/tables/comparison/rolling_regime_detection_summary.csv
    outputs/tables/comparison/rolling_regime_detection_latest.csv
    outputs/tables/comparison/rolling_regime_detection_transitions.csv
    outputs/tables/comparison/rolling_regime_detection_report.txt

Purpose:

    This script checks how each ticker's detected regime changes over time
    using rolling historical return and volatility estimates.

    It is the next diagnostic step after historical_ticker_calibration.py.
"""

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

from app.regime_detection import detect_regime


# =============================================================================
# User settings
# =============================================================================

TICKERS = [
    "SPY",
    "QQQ",
    "IWM",
    "TQQQ",
    "SOXL",
]

TRADING_DAYS_PER_YEAR = 252

# Rolling windows in trading days.
# 63  = about 3 months
# 126 = about 6 months
# 252 = about 1 year
# 504 = about 2 years
ROLLING_WINDOWS = [
    63,
    126,
    252,
    504,
]

REGIME_ORDER = [
    "bearish_market",
    "sideways_market",
    "baseline",
    "bullish_market",
    "high_volatility",
    "low_volatility",
]


# =============================================================================
# Paths
# =============================================================================

DATA_DIR = PROJECT_ROOT / "data" / "historical_prices"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "comparison"

SUMMARY_PATH = OUTPUT_TABLE_DIR / "rolling_regime_detection_summary.csv"
LATEST_PATH = OUTPUT_TABLE_DIR / "rolling_regime_detection_latest.csv"
TRANSITIONS_PATH = OUTPUT_TABLE_DIR / "rolling_regime_detection_transitions.csv"
REPORT_PATH = OUTPUT_TABLE_DIR / "rolling_regime_detection_report.txt"


# =============================================================================
# Helpers
# =============================================================================

def format_decimal(value: object, digits: int = 4) -> str:
    """
    Format a decimal value.
    """

    value = pd.to_numeric(value, errors="coerce")

    if pd.isna(value):
        return "NA"

    return f"{float(value):,.{digits}f}"


def format_percent(value: object, digits: int = 2) -> str:
    """
    Format a decimal value as a percentage.
    """

    value = pd.to_numeric(value, errors="coerce")

    if pd.isna(value):
        return "NA"

    return f"{100.0 * float(value):,.{digits}f}%"


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

    if len(clean_df) < 30:
        raise ValueError(
            f"{csv_path} has fewer than 30 valid price rows."
        )

    return clean_df


def detect_regime_safe(
    annual_return: float,
    annual_volatility: float,
) -> str:
    """
    Detect regime while handling missing values.
    """

    if pd.isna(annual_return) or pd.isna(annual_volatility):
        return "unknown"

    return detect_regime(
        annual_return=float(annual_return),
        annual_volatility=float(annual_volatility),
    )


def compute_rolling_regimes(
    ticker: str,
    price_df: pd.DataFrame,
    window: int,
) -> pd.DataFrame:
    """
    Compute rolling return, volatility, and detected regime for one ticker/window.
    """

    df = price_df.copy()

    df["Daily_Return"] = df["Price"].pct_change()

    df["Rolling_Start_Price"] = df["Price"].shift(window)
    df["Rolling_End_Price"] = df["Price"]

    df["Rolling_Cumulative_Return"] = (
        df["Rolling_End_Price"] / df["Rolling_Start_Price"]
    ) - 1.0

    df["Rolling_Annual_Return"] = (
        df["Rolling_End_Price"] / df["Rolling_Start_Price"]
    ) ** (TRADING_DAYS_PER_YEAR / window) - 1.0

    df["Rolling_Annual_Volatility"] = (
        df["Daily_Return"].rolling(window=window).std()
        * (TRADING_DAYS_PER_YEAR ** 0.5)
    )

    df["Detected_Regime"] = df.apply(
        lambda row: detect_regime_safe(
            annual_return=row["Rolling_Annual_Return"],
            annual_volatility=row["Rolling_Annual_Volatility"],
        ),
        axis=1,
    )

    df["Ticker"] = ticker
    df["Rolling_Window_Days"] = window

    output_columns = [
        "Ticker",
        "Date",
        "Rolling_Window_Days",
        "Price",
        "Rolling_Start_Price",
        "Rolling_End_Price",
        "Rolling_Cumulative_Return",
        "Rolling_Annual_Return",
        "Rolling_Annual_Volatility",
        "Detected_Regime",
    ]

    df = df[output_columns].copy()

    df = df[df["Detected_Regime"] != "unknown"].reset_index(drop=True)

    return df


def build_summary_table(rolling_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build regime-count summary by ticker and rolling window.
    """

    if rolling_df.empty:
        return pd.DataFrame()

    rows = []

    grouped = rolling_df.groupby(
        ["Ticker", "Rolling_Window_Days", "Detected_Regime"],
        dropna=False,
    )

    counts_df = grouped.size().reset_index(name="Observation_Count")

    total_counts = (
        rolling_df.groupby(["Ticker", "Rolling_Window_Days"])
        .size()
        .reset_index(name="Total_Observations")
    )

    counts_df = counts_df.merge(
        total_counts,
        on=["Ticker", "Rolling_Window_Days"],
        how="left",
    )

    counts_df["Regime_Fraction"] = (
        counts_df["Observation_Count"] / counts_df["Total_Observations"]
    )

    for _, row in counts_df.iterrows():
        rows.append(
            {
                "Ticker": row["Ticker"],
                "Rolling_Window_Days": row["Rolling_Window_Days"],
                "Detected_Regime": row["Detected_Regime"],
                "Observation_Count": int(row["Observation_Count"]),
                "Total_Observations": int(row["Total_Observations"]),
                "Regime_Fraction": float(row["Regime_Fraction"]),
            }
        )

    summary_df = pd.DataFrame(rows)

    summary_df = summary_df.sort_values(
        ["Ticker", "Rolling_Window_Days", "Detected_Regime"]
    ).reset_index(drop=True)

    return summary_df


def build_latest_table(rolling_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build table showing latest detected regime for each ticker/window.
    """

    if rolling_df.empty:
        return pd.DataFrame()

    rows = []

    grouped = rolling_df.groupby(["Ticker", "Rolling_Window_Days"])

    for (ticker, window), group_df in grouped:
        group_df = group_df.sort_values("Date").reset_index(drop=True)

        latest = group_df.iloc[-1]

        rows.append(
            {
                "Ticker": ticker,
                "Rolling_Window_Days": window,
                "Latest_Date": latest["Date"],
                "Latest_Price": latest["Price"],
                "Latest_Rolling_Cumulative_Return": latest[
                    "Rolling_Cumulative_Return"
                ],
                "Latest_Rolling_Annual_Return": latest[
                    "Rolling_Annual_Return"
                ],
                "Latest_Rolling_Annual_Volatility": latest[
                    "Rolling_Annual_Volatility"
                ],
                "Latest_Detected_Regime": latest["Detected_Regime"],
            }
        )

    latest_df = pd.DataFrame(rows)

    latest_df = latest_df.sort_values(
        ["Ticker", "Rolling_Window_Days"]
    ).reset_index(drop=True)

    return latest_df


def build_transition_table(rolling_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build table of regime transitions by ticker/window.
    """

    if rolling_df.empty:
        return pd.DataFrame()

    rows = []

    grouped = rolling_df.groupby(["Ticker", "Rolling_Window_Days"])

    for (ticker, window), group_df in grouped:
        group_df = group_df.sort_values("Date").reset_index(drop=True)

        previous_regime = None
        previous_date = None

        for _, row in group_df.iterrows():
            current_regime = row["Detected_Regime"]
            current_date = row["Date"]

            if previous_regime is None:
                previous_regime = current_regime
                previous_date = current_date
                continue

            if current_regime != previous_regime:
                rows.append(
                    {
                        "Ticker": ticker,
                        "Rolling_Window_Days": window,
                        "Transition_Date": current_date,
                        "Previous_Date": previous_date,
                        "From_Regime": previous_regime,
                        "To_Regime": current_regime,
                        "Rolling_Annual_Return": row["Rolling_Annual_Return"],
                        "Rolling_Annual_Volatility": row[
                            "Rolling_Annual_Volatility"
                        ],
                    }
                )

            previous_regime = current_regime
            previous_date = current_date

    transitions_df = pd.DataFrame(rows)

    if not transitions_df.empty:
        transitions_df = transitions_df.sort_values(
            ["Ticker", "Rolling_Window_Days", "Transition_Date"]
        ).reset_index(drop=True)

    return transitions_df


def get_dominant_regime(
    summary_df: pd.DataFrame,
    ticker: str,
    window: int,
) -> str:
    """
    Find the most common regime for one ticker/window.
    """

    subset = summary_df[
        (summary_df["Ticker"].astype(str) == str(ticker))
        & (summary_df["Rolling_Window_Days"].astype(int) == int(window))
    ].copy()

    if subset.empty:
        return "NA"

    subset = subset.sort_values(
        ["Regime_Fraction", "Observation_Count"],
        ascending=False,
    ).reset_index(drop=True)

    return str(subset.iloc[0]["Detected_Regime"])


def get_dominant_fraction(
    summary_df: pd.DataFrame,
    ticker: str,
    window: int,
) -> float:
    """
    Find the fraction of time spent in the dominant regime.
    """

    subset = summary_df[
        (summary_df["Ticker"].astype(str) == str(ticker))
        & (summary_df["Rolling_Window_Days"].astype(int) == int(window))
    ].copy()

    if subset.empty:
        return float("nan")

    subset = subset.sort_values(
        ["Regime_Fraction", "Observation_Count"],
        ascending=False,
    ).reset_index(drop=True)

    return float(subset.iloc[0]["Regime_Fraction"])


def build_report(
    rolling_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    latest_df: pd.DataFrame,
    transitions_df: pd.DataFrame,
) -> str:
    """
    Build plain-text rolling regime detection report.
    """

    lines = []

    lines.append("COVERED CALL SIMULATOR - ROLLING REGIME DETECTION REPORT")
    lines.append("=" * 100)
    lines.append("")
    lines.append(f"Data folder:          {DATA_DIR}")
    lines.append(f"Rolling windows:      {ROLLING_WINDOWS}")
    lines.append(f"Summary file:         {SUMMARY_PATH}")
    lines.append(f"Latest file:          {LATEST_PATH}")
    lines.append(f"Transitions file:     {TRANSITIONS_PATH}")
    lines.append("")
    lines.append(
        "This report estimates rolling annual return and rolling annual "
        "volatility from historical prices."
    )
    lines.append("")
    lines.append(
        "Each rolling estimate is passed into the same rule-based regime "
        "detector used elsewhere in the Covered Call Simulator."
    )
    lines.append("")
    lines.append(
        "This is a diagnostic only. It should not be wired into app/main.py "
        "until the rolling window and regime rules have been reviewed."
    )
    lines.append("")

    if rolling_df.empty:
        lines.append("No rolling regime rows were created.")
        return "\n".join(lines)

    lines.append("-" * 100)
    lines.append("Latest detected regime by ticker and window")
    lines.append("-" * 100)
    lines.append("")

    for _, row in latest_df.iterrows():
        lines.append(f"Ticker: {row['Ticker']}")
        lines.append(f"    Rolling window:              {row['Rolling_Window_Days']} trading days")
        lines.append(f"    Latest date:                 {row['Latest_Date']}")
        lines.append(f"    Latest price:                {format_decimal(row['Latest_Price'], 2)}")
        lines.append(
            f"    Rolling cumulative return:   "
            f"{format_percent(row['Latest_Rolling_Cumulative_Return'])}"
        )
        lines.append(
            f"    Rolling annual return:       "
            f"{format_percent(row['Latest_Rolling_Annual_Return'])}"
        )
        lines.append(
            f"    Rolling annual volatility:   "
            f"{format_percent(row['Latest_Rolling_Annual_Volatility'])}"
        )
        lines.append(f"    Latest detected regime:      {row['Latest_Detected_Regime']}")
        lines.append("")

    lines.append("-" * 100)
    lines.append("Dominant regime by ticker and window")
    lines.append("-" * 100)
    lines.append("")

    for ticker in sorted(rolling_df["Ticker"].astype(str).unique()):
        lines.append(f"Ticker: {ticker}")

        for window in ROLLING_WINDOWS:
            dominant_regime = get_dominant_regime(
                summary_df=summary_df,
                ticker=ticker,
                window=window,
            )

            dominant_fraction = get_dominant_fraction(
                summary_df=summary_df,
                ticker=ticker,
                window=window,
            )

            lines.append(
                f"    {window:>3} days: "
                f"{dominant_regime:<18} "
                f"({format_percent(dominant_fraction)} of observations)"
            )

        lines.append("")

    lines.append("-" * 100)
    lines.append("Regime fraction detail")
    lines.append("-" * 100)
    lines.append("")

    for ticker in sorted(rolling_df["Ticker"].astype(str).unique()):
        lines.append(f"Ticker: {ticker}")

        for window in ROLLING_WINDOWS:
            subset = summary_df[
                (summary_df["Ticker"].astype(str) == str(ticker))
                & (summary_df["Rolling_Window_Days"].astype(int) == int(window))
            ].copy()

            if subset.empty:
                continue

            lines.append(f"    Rolling window: {window} trading days")

            subset = subset.sort_values(
                "Regime_Fraction",
                ascending=False,
            ).reset_index(drop=True)

            for _, row in subset.iterrows():
                lines.append(
                    f"        {str(row['Detected_Regime']):<18} "
                    f"Count={int(row['Observation_Count']):>5} "
                    f"Fraction={format_percent(row['Regime_Fraction'])}"
                )

        lines.append("")

    transition_count = 0

    if not transitions_df.empty:
        transition_count = len(transitions_df)

    lines.append("=" * 100)
    lines.append("Overall conclusion")
    lines.append("=" * 100)
    lines.append("")
    lines.append(f"Tickers analyzed:          {rolling_df['Ticker'].nunique()}")
    lines.append(f"Rolling windows tested:    {len(ROLLING_WINDOWS)}")
    lines.append(f"Rolling observations:      {len(rolling_df)}")
    lines.append(f"Regime transitions found:  {transition_count}")
    lines.append("")
    lines.append(
        "Recommendation: use this report to decide which rolling window "
        "produces the most stable and intuitive regime classifications."
    )
    lines.append("")
    lines.append(
        "Do not connect rolling regime detection to the main simulator until "
        "the preferred rolling window has been selected."
    )

    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)

    all_rolling_rows = []

    print("")
    print("=" * 100)
    print("COVERED CALL SIMULATOR - ROLLING REGIME DETECTION")
    print("=" * 100)
    print(f"Data folder:      {DATA_DIR}")
    print(f"Tickers:          {TICKERS}")
    print(f"Rolling windows:  {ROLLING_WINDOWS}")
    print("=" * 100)
    print("")

    for ticker in TICKERS:
        try:
            print("")
            print("=" * 80)
            print(f"Processing ticker: {ticker}")
            print("=" * 80)

            price_df = read_price_file(ticker)

            print(f"Rows loaded: {len(price_df)}")
            print(f"Date range:  {price_df['Date'].iloc[0]} to {price_df['Date'].iloc[-1]}")

            for window in ROLLING_WINDOWS:
                if len(price_df) <= window:
                    print(
                        f"Skipping {ticker}, window {window}: "
                        f"not enough rows."
                    )
                    continue

                rolling_df = compute_rolling_regimes(
                    ticker=ticker,
                    price_df=price_df,
                    window=window,
                )

                all_rolling_rows.append(rolling_df)

                print(
                    f"Window {window}: "
                    f"{len(rolling_df)} rolling observations"
                )

        except Exception as exc:
            print(f"FAILED: {ticker}")
            print(str(exc))

    if all_rolling_rows:
        full_rolling_df = pd.concat(
            all_rolling_rows,
            ignore_index=True,
        )
    else:
        full_rolling_df = pd.DataFrame()

    summary_df = build_summary_table(full_rolling_df)
    latest_df = build_latest_table(full_rolling_df)
    transitions_df = build_transition_table(full_rolling_df)

    summary_df.to_csv(SUMMARY_PATH, index=False)
    latest_df.to_csv(LATEST_PATH, index=False)
    transitions_df.to_csv(TRANSITIONS_PATH, index=False)

    report_text = build_report(
        rolling_df=full_rolling_df,
        summary_df=summary_df,
        latest_df=latest_df,
        transitions_df=transitions_df,
    )

    REPORT_PATH.write_text(report_text, encoding="utf-8")

    print("")
    print("=" * 100)
    print("Rolling regime detection complete.")
    print("=" * 100)
    print("")
    print("Saved files:")
    print(f"  {SUMMARY_PATH}")
    print(f"  {LATEST_PATH}")
    print(f"  {TRANSITIONS_PATH}")
    print(f"  {REPORT_PATH}")
    print("")
    print("Done.")
    print("")


if __name__ == "__main__":
    main()