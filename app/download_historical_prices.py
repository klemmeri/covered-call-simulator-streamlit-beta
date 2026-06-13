"""
download_historical_prices.py

Downloads historical daily price data for the Covered Call Simulator.

This script fills the CSV files needed by:

    app/historical_ticker_calibration.py

Output folder:

    data/historical_prices

Output files:

    data/historical_prices/SPY.csv
    data/historical_prices/QQQ.csv
    data/historical_prices/IWM.csv
    data/historical_prices/TQQQ.csv
    data/historical_prices/SOXL.csv

Each output file will contain daily historical price data with standardized columns:

    Date
    Open
    High
    Low
    Close
    Adj Close
    Volume

This script is standalone.
It does not modify app/main.py.
"""

from pathlib import Path

import pandas as pd
import yfinance as yf


# =============================================================================
# Paths
# =============================================================================

CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

DATA_DIR = PROJECT_ROOT / "data" / "historical_prices"


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

START_DATE = "2020-01-01"
END_DATE = None
# END_DATE = None means download through the most recent available date.


# =============================================================================
# Helpers
# =============================================================================

def flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flatten yfinance columns if they are returned as a MultiIndex.

    yfinance may return columns like:

        ('Close', 'SPY')

    This function converts them to:

        Close_SPY

    Later we strip the ticker suffix.
    """

    clean_df = df.copy()

    if isinstance(clean_df.columns, pd.MultiIndex):
        clean_df.columns = [
            "_".join(
                str(part).strip()
                for part in column_tuple
                if str(part).strip()
            )
            for column_tuple in clean_df.columns
        ]

    return clean_df


def standardize_column_name(column_name: str, ticker: str) -> str:
    """
    Convert yfinance column names into standard names.

    Handles examples such as:

        Close
        Close_SPY
        SPY_Close
        Adj Close
        Adj Close_SPY
        Adj_Close_SPY
    """

    name = str(column_name).strip()

    ticker_upper = ticker.upper()

    # Remove ticker suffix or prefix if yfinance added it.
    possible_suffixes = [
        f"_{ticker_upper}",
        f" {ticker_upper}",
    ]

    possible_prefixes = [
        f"{ticker_upper}_",
        f"{ticker_upper} ",
    ]

    for suffix in possible_suffixes:
        if name.upper().endswith(suffix.upper()):
            name = name[: -len(suffix)].strip()

    for prefix in possible_prefixes:
        if name.upper().startswith(prefix.upper()):
            name = name[len(prefix):].strip()

    normalized = (
        name.lower()
        .replace("_", " ")
        .replace("-", " ")
        .replace(".", " ")
    )

    normalized = " ".join(normalized.split())

    if normalized == "date":
        return "Date"

    if normalized == "open":
        return "Open"

    if normalized == "high":
        return "High"

    if normalized == "low":
        return "Low"

    if normalized == "close":
        return "Close"

    if normalized in ["adj close", "adjusted close"]:
        return "Adj Close"

    if normalized == "volume":
        return "Volume"

    return name


def clean_downloaded_data(raw_df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """
    Clean downloaded Yahoo Finance data.

    Returns a DataFrame with standardized columns:

        Date
        Open
        High
        Low
        Close
        Adj Close
        Volume
    """

    if raw_df.empty:
        return pd.DataFrame()

    df = raw_df.copy()

    df = flatten_columns(df)

    # yfinance usually returns Date as the index.
    df = df.reset_index()

    # Standardize column names.
    rename_map = {
        column: standardize_column_name(column, ticker)
        for column in df.columns
    }

    df = df.rename(columns=rename_map)

    # If duplicate columns were created, keep the first non-empty version.
    df = df.loc[:, ~df.columns.duplicated()].copy()

    if "Date" not in df.columns:
        raise ValueError(
            f"Downloaded data for {ticker} does not contain a Date column. "
            f"Columns found: {list(df.columns)}"
        )

    if "Close" not in df.columns and "Adj Close" not in df.columns:
        raise ValueError(
            f"Downloaded data for {ticker} does not contain Close or Adj Close. "
            f"Columns found: {list(df.columns)}"
        )

    # Convert Date.
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date

    # Keep useful columns only.
    preferred_columns = [
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Adj Close",
        "Volume",
    ]

    available_columns = [
        column for column in preferred_columns
        if column in df.columns
    ]

    df = df[available_columns].copy()

    # Convert numeric columns.
    for column in df.columns:
        if column != "Date":
            df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(subset=["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    return df


def download_one_ticker(ticker: str) -> pd.DataFrame:
    """
    Download historical daily data for one ticker.
    """

    print("")
    print("=" * 80)
    print(f"Downloading {ticker}")
    print("=" * 80)

    raw_df = yf.download(
        tickers=ticker,
        start=START_DATE,
        end=END_DATE,
        interval="1d",
        auto_adjust=False,
        progress=False,
        group_by="column",
        threads=False,
    )

    print("Raw columns:")
    print(list(raw_df.columns))

    clean_df = clean_downloaded_data(
        raw_df=raw_df,
        ticker=ticker,
    )

    if clean_df.empty:
        raise ValueError(f"No data downloaded for {ticker}.")

    print("Clean columns:")
    print(list(clean_df.columns))

    return clean_df


def save_ticker_csv(ticker: str, df: pd.DataFrame) -> Path:
    """
    Save one ticker DataFrame to CSV.
    """

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    output_path = DATA_DIR / f"{ticker}.csv"

    df.to_csv(output_path, index=False)

    return output_path


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("")
    print("=" * 100)
    print("COVERED CALL SIMULATOR - DOWNLOAD HISTORICAL PRICES")
    print("=" * 100)
    print(f"Output folder: {DATA_DIR}")
    print(f"Start date:    {START_DATE}")
    print(f"End date:      {END_DATE if END_DATE else 'most recent available'}")
    print(f"Tickers:       {TICKERS}")
    print("=" * 100)

    downloaded_rows = []

    for ticker in TICKERS:
        try:
            df = download_one_ticker(ticker)
            output_path = save_ticker_csv(ticker, df)

            first_date = df["Date"].iloc[0]
            last_date = df["Date"].iloc[-1]

            downloaded_rows.append(
                {
                    "Ticker": ticker,
                    "Rows": len(df),
                    "First_Date": first_date,
                    "Last_Date": last_date,
                    "Output_File": str(output_path),
                    "Status": "OK",
                    "Error": "",
                }
            )

            print(f"Saved {ticker}: {output_path}")
            print(f"Rows: {len(df)}")
            print(f"Date range: {first_date} to {last_date}")

        except Exception as exc:
            downloaded_rows.append(
                {
                    "Ticker": ticker,
                    "Rows": 0,
                    "First_Date": "",
                    "Last_Date": "",
                    "Output_File": "",
                    "Status": "FAILED",
                    "Error": str(exc),
                }
            )

            print(f"FAILED: {ticker}")
            print(str(exc))

    summary_df = pd.DataFrame(downloaded_rows)

    summary_path = DATA_DIR / "download_summary.csv"
    summary_df.to_csv(summary_path, index=False)

    print("")
    print("=" * 100)
    print("Download complete.")
    print("=" * 100)
    print("")
    print("Summary:")
    print(summary_df.to_string(index=False))
    print("")
    print(f"Saved summary: {summary_path}")
    print("")
    print("Next step:")
    print("    python app\\historical_ticker_calibration.py")
    print("")


if __name__ == "__main__":
    main()