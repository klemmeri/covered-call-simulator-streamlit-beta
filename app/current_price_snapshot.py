"""
current_price_snapshot.py

Builds a current or near-current price snapshot for the Covered Call Simulator.

Purpose
-------
This script creates a separate live/current-price layer for the dashboard.

The existing regime logic should continue to use completed daily bars.
This script is for dashboard tradability and position-size estimates.

Output
------
outputs/tables/comparison/current_price_snapshot.csv

Important
---------
Quotes from yfinance may be delayed. This script should be treated as a
near-current quote helper, not an exchange-grade real-time feed.

Time Convention
---------------
This script uses U.S. Eastern Time because the covered-call dashboard is a
market-facing tool. The output columns are:

    Quote_Time_ET
    Quote_Date_ET

Using ET avoids confusion between standard time and daylight time. Internally,
the timezone is America/New_York.
"""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


try:
    import yfinance as yf
except ImportError as exc:
    raise ImportError(
        "The yfinance package is required for current_price_snapshot.py. "
        "Install it in the PyCharm interpreter with: pip install yfinance"
    ) from exc


# =============================================================================
# Configuration
# =============================================================================

TICKERS = [
    "IWM",
    "QQQ",
    "SOXL",
    "SPY",
    "TQQQ",
]

OUTPUT_FILENAME = "current_price_snapshot.csv"

MARKET_TIMEZONE = ZoneInfo("America/New_York")


# =============================================================================
# Path helpers
# =============================================================================

def get_project_root() -> Path:
    """
    Return the Covered Call Simulator project root.

    This file is expected to live in:

        Coveredcallsimulator/app/current_price_snapshot.py
    """
    current_file = Path(__file__).resolve()
    app_dir = current_file.parent
    project_root = app_dir.parent

    return project_root


def get_output_dir(project_root: Path) -> Path:
    """
    Return the comparison output directory.
    """
    return project_root / "outputs" / "tables" / "comparison"


def get_output_path(project_root: Path) -> Path:
    """
    Return the full output path for the current price snapshot.
    """
    return get_output_dir(project_root) / OUTPUT_FILENAME


# =============================================================================
# Time helpers
# =============================================================================

def get_market_now() -> datetime:
    """
    Return current timestamp in U.S. Eastern Time.
    """
    return datetime.now(MARKET_TIMEZONE)


def format_et_timestamp(timestamp: datetime) -> str:
    """
    Format an Eastern Time timestamp.
    """
    return timestamp.strftime("%Y-%m-%d %I:%M:%S %p ET")


# =============================================================================
# Quote helpers
# =============================================================================

def safe_float(value) -> float | None:
    """
    Safely convert a value to float.
    """
    try:
        if value is None:
            return None

        numeric_value = float(value)

        if pd.isna(numeric_value):
            return None

        return numeric_value

    except Exception:
        return None


def get_from_fast_info(fast_info, key: str):
    """
    Safely read a value from yfinance fast_info.

    yfinance fast_info may act like a dictionary or expose attributes,
    depending on the installed yfinance version.
    """
    try:
        if hasattr(fast_info, "get"):
            return fast_info.get(key)
    except Exception:
        pass

    try:
        return getattr(fast_info, key)
    except Exception:
        return None


def get_last_daily_close(ticker: str) -> dict[str, object]:
    """
    Fallback method: download recent daily bars and return the last close.

    Despite the name "fallback", this can still be today's latest available
    daily value if the data provider has already updated the daily bar.
    """
    try:
        history_df = yf.download(
            tickers=ticker,
            period="5d",
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False,
        )

        if history_df.empty:
            return {
                "fallback_price": None,
                "fallback_date": None,
            }

        # yfinance can return a MultiIndex column DataFrame in some cases.
        if isinstance(history_df.columns, pd.MultiIndex):
            if ("Close", ticker) in history_df.columns:
                close_series = history_df[("Close", ticker)]
            elif ("Adj Close", ticker) in history_df.columns:
                close_series = history_df[("Adj Close", ticker)]
            else:
                close_series = history_df.iloc[:, 0]
        else:
            if "Close" in history_df.columns:
                close_series = history_df["Close"]
            elif "Adj Close" in history_df.columns:
                close_series = history_df["Adj Close"]
            else:
                close_series = history_df.iloc[:, 0]

        close_series = close_series.dropna()

        if close_series.empty:
            return {
                "fallback_price": None,
                "fallback_date": None,
            }

        last_date = close_series.index[-1]
        last_price = safe_float(close_series.iloc[-1])

        if hasattr(last_date, "date"):
            fallback_date = str(last_date.date())
        else:
            fallback_date = str(last_date)

        return {
            "fallback_price": last_price,
            "fallback_date": fallback_date,
        }

    except Exception:
        return {
            "fallback_price": None,
            "fallback_date": None,
        }


def get_current_quote(ticker: str) -> dict[str, object]:
    """
    Get a current or near-current quote for one ticker.

    Uses yfinance fast_info first, then falls back to recent daily close.

    Quote_Status values are user-facing:

        Live/near-live:
            A price was obtained from yfinance fast_info.

        Daily price:
            A price was obtained from the latest available daily bar.

        Missing:
            No usable price was found.
    """
    quote_time_et = get_market_now()

    row = {
        "Ticker": ticker,
        "Quote_Time_ET": format_et_timestamp(quote_time_et),
        "Quote_Date_ET": quote_time_et.strftime("%Y-%m-%d"),
        "Current_Price": None,
        "Previous_Close": None,
        "Open": None,
        "Day_High": None,
        "Day_Low": None,
        "Last_Daily_Close": None,
        "Last_Daily_Close_Date": None,
        "Source": "Unavailable",
        "Quote_Status": "Missing",
        "Notes": "",
    }

    try:
        yf_ticker = yf.Ticker(ticker)
        fast_info = yf_ticker.fast_info

        last_price = safe_float(
            get_from_fast_info(fast_info, "last_price")
        )

        regular_market_price = safe_float(
            get_from_fast_info(fast_info, "regular_market_price")
        )

        previous_close = safe_float(
            get_from_fast_info(fast_info, "previous_close")
        )

        open_price = safe_float(
            get_from_fast_info(fast_info, "open")
        )

        day_high = safe_float(
            get_from_fast_info(fast_info, "day_high")
        )

        day_low = safe_float(
            get_from_fast_info(fast_info, "day_low")
        )

        current_price = last_price

        if current_price is None:
            current_price = regular_market_price

        if current_price is None:
            current_price = previous_close

        row["Current_Price"] = current_price
        row["Previous_Close"] = previous_close
        row["Open"] = open_price
        row["Day_High"] = day_high
        row["Day_Low"] = day_low

        if current_price is not None:
            row["Source"] = "yfinance fast_info"
            row["Quote_Status"] = "Live/near-live"

    except Exception as exc:
        row["Notes"] = f"fast_info error: {exc}"

    fallback = get_last_daily_close(ticker)

    row["Last_Daily_Close"] = fallback["fallback_price"]
    row["Last_Daily_Close_Date"] = fallback["fallback_date"]

    if row["Current_Price"] is None and fallback["fallback_price"] is not None:
        row["Current_Price"] = fallback["fallback_price"]
        row["Source"] = "yfinance daily bar"
        row["Quote_Status"] = "Daily price"

    if row["Current_Price"] is None:
        row["Quote_Status"] = "Missing"

    return row


# =============================================================================
# Main
# =============================================================================

def build_current_price_snapshot() -> pd.DataFrame:
    """
    Build the current price snapshot DataFrame.
    """
    rows = []

    for ticker in TICKERS:
        print(f"Fetching current price for {ticker}...")
        rows.append(get_current_quote(ticker))

    snapshot_df = pd.DataFrame(rows)

    column_order = [
        "Ticker",
        "Quote_Time_ET",
        "Quote_Date_ET",
        "Current_Price",
        "Previous_Close",
        "Open",
        "Day_High",
        "Day_Low",
        "Last_Daily_Close",
        "Last_Daily_Close_Date",
        "Source",
        "Quote_Status",
        "Notes",
    ]

    available_columns = [
        column for column in column_order if column in snapshot_df.columns
    ]

    snapshot_df = snapshot_df[available_columns].copy()

    return snapshot_df


def save_current_price_snapshot(snapshot_df: pd.DataFrame) -> Path:
    """
    Save the current price snapshot.
    """
    project_root = get_project_root()
    output_dir = get_output_dir(project_root)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = get_output_path(project_root)

    snapshot_df.to_csv(output_path, index=False)

    return output_path


def main() -> None:
    """
    Build and save the current price snapshot.
    """
    print()
    print("=" * 79)
    print("Current Price Snapshot")
    print("=" * 79)

    snapshot_df = build_current_price_snapshot()
    output_path = save_current_price_snapshot(snapshot_df)

    print()
    print("Current price snapshot:")
    print(snapshot_df.to_string(index=False))

    print()
    print("Saved current price snapshot to:")
    print(output_path)

    print()
    print("Note: yfinance quotes may be delayed.")
    print("Time convention: U.S. Eastern Time, displayed as ET.")
    print("=" * 79)
    print()


if __name__ == "__main__":
    main()