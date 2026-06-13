"""
phase4_historical_price_path_adapter.py

Phase 4-4 historical price path input adapter for the Covered Call Simulator.

This module is a conservative bridge between the market-data CSV scaffold and the
existing simulation engine. It reads an imported underlying-price CSV, validates
and normalizes the price records, then converts them into a simple historical
price-path table that later phases can connect to the simulator.

No dashboard changes are made in this phase.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json

import pandas as pd


READY_MARKER = "PHASE4_4_HISTORICAL_PRICE_PATH_ADAPTER_READY"
RELEASE_DECISION = "PHASE4_4_HISTORICAL_PRICE_PATH_ADAPTER_CREATED_NO_DASHBOARD_CHANGE"
DASHBOARD_CHANGE_REQUIRED = False

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = PROJECT_ROOT / "inputs" / "market_data"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"

DEFAULT_UNDERLYING_PRICE_FILE = INPUT_DIR / "sample_underlying_prices.csv"

REQUIRED_UNDERLYING_COLUMNS = [
    "date",
    "ticker",
    "open",
    "high",
    "low",
    "close",
    "volume",
]

ADAPTED_PATH_COLUMNS = [
    "path_id",
    "source_mode",
    "ticker",
    "step",
    "date",
    "price",
    "open",
    "high",
    "low",
    "close",
    "daily_return",
    "cumulative_return",
]




def _ensure_output_dirs() -> None:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)


def _create_fallback_underlying_sample(path: Path) -> None:
    """
    Create a small deterministic price file only when the expected sample is absent.

    Phase 4-2 normally creates this file. The fallback keeps the adapter check
    robust if someone runs Phase 4-4 before regenerating the Phase 4-2 templates.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {"date": "2024-01-02", "ticker": "SPY", "open": 545.25, "high": 547.10, "low": 543.80, "close": 546.20, "volume": 72500000},
        {"date": "2024-01-03", "ticker": "SPY", "open": 546.20, "high": 548.00, "low": 544.90, "close": 547.35, "volume": 70100000},
        {"date": "2024-01-04", "ticker": "SPY", "open": 547.35, "high": 549.50, "low": 546.10, "close": 548.90, "volume": 68800000},
        {"date": "2024-01-05", "ticker": "SPY", "open": 548.90, "high": 550.10, "low": 547.40, "close": 549.45, "volume": 69500000},
        {"date": "2024-01-08", "ticker": "SPY", "open": 549.45, "high": 552.25, "low": 548.80, "close": 551.80, "volume": 74600000},
    ]
    pd.DataFrame(rows).to_csv(path, index=False)


def _read_underlying_prices(path: Path) -> pd.DataFrame:
    if not path.exists():
        _create_fallback_underlying_sample(path)
    return pd.read_csv(path)


def _validate_required_columns(df: pd.DataFrame) -> list[str]:
    return [column for column in REQUIRED_UNDERLYING_COLUMNS if column not in df.columns]


def normalize_underlying_prices(df: pd.DataFrame, ticker: str | None = None) -> tuple[pd.DataFrame, list[str]]:
    """
    Return a clean, sorted underlying-price table and a list of issues.

    The adapter is intentionally strict enough to prevent bad data from moving
    into the simulator, but not yet a full production-grade market-data parser.
    """
    issues: list[str] = []
    working = df.copy()

    missing = _validate_required_columns(working)
    if missing:
        issues.append("Missing required underlying-price columns: " + ", ".join(missing))
        return pd.DataFrame(columns=REQUIRED_UNDERLYING_COLUMNS), issues

    working["date"] = pd.to_datetime(working["date"], errors="coerce")
    bad_dates = int(working["date"].isna().sum())
    if bad_dates:
        issues.append(f"Dropped {bad_dates} row(s) with unparseable dates.")
    working = working.dropna(subset=["date"])

    for column in ["open", "high", "low", "close", "volume"]:
        working[column] = pd.to_numeric(working[column], errors="coerce")
        bad_values = int(working[column].isna().sum())
        if bad_values:
            issues.append(f"Dropped {bad_values} row(s) with non-numeric {column} values.")
    working = working.dropna(subset=["open", "high", "low", "close", "volume"])

    if ticker:
        before = len(working)
        working = working[working["ticker"].astype(str).str.upper() == ticker.upper()]
        removed = before - len(working)
        if removed:
            issues.append(f"Filtered out {removed} row(s) not matching ticker {ticker.upper()}.")

    for column in ["open", "high", "low", "close"]:
        non_positive = int((working[column] <= 0).sum())
        if non_positive:
            issues.append(f"Dropped {non_positive} row(s) with non-positive {column} prices.")
            working = working[working[column] > 0]

    negative_volume = int((working["volume"] < 0).sum())
    if negative_volume:
        issues.append(f"Dropped {negative_volume} row(s) with negative volume.")
        working = working[working["volume"] >= 0]

    high_too_low = int(((working["high"] < working["open"]) | (working["high"] < working["close"]) | (working["high"] < working["low"])).sum())
    low_too_high = int(((working["low"] > working["open"]) | (working["low"] > working["close"]) | (working["low"] > working["high"])).sum())
    if high_too_low:
        issues.append(f"Found {high_too_low} row(s) where high is inconsistent with OHLC prices.")
    if low_too_high:
        issues.append(f"Found {low_too_high} row(s) where low is inconsistent with OHLC prices.")

    working = working.sort_values(["ticker", "date"]).drop_duplicates(subset=["ticker", "date"], keep="last")
    working = working.reset_index(drop=True)
    return working, issues


def build_historical_price_path(normalized_df: pd.DataFrame, ticker: str | None = None) -> tuple[pd.DataFrame, list[str]]:
    """
    Convert normalized OHLC data into the path shape needed by later simulator work.

    For Phase 4-4, one path is produced per selected ticker. Later phases can
    extend this adapter to create rolling windows, multiple historical paths, or
    bootstrapped paths.
    """
    issues: list[str] = []
    if normalized_df.empty:
        issues.append("No normalized underlying-price rows are available for path construction.")
        return pd.DataFrame(columns=ADAPTED_PATH_COLUMNS), issues

    working = normalized_df.copy()
    if ticker is None:
        ticker = str(working["ticker"].iloc[0])
    working = working[working["ticker"].astype(str).str.upper() == ticker.upper()].copy()

    if working.empty:
        issues.append(f"No rows are available for ticker {ticker}.")
        return pd.DataFrame(columns=ADAPTED_PATH_COLUMNS), issues

    working = working.sort_values("date").reset_index(drop=True)
    first_price = float(working["close"].iloc[0])
    if first_price <= 0:
        issues.append("First close price must be positive.")
        return pd.DataFrame(columns=ADAPTED_PATH_COLUMNS), issues

    path = pd.DataFrame()
    path["path_id"] = ["historical_path_001"] * len(working)
    path["source_mode"] = "historical_import"
    path["ticker"] = working["ticker"].astype(str).str.upper()
    path["step"] = range(len(working))
    path["date"] = working["date"].dt.strftime("%Y-%m-%d")
    path["price"] = working["close"].astype(float)
    path["open"] = working["open"].astype(float)
    path["high"] = working["high"].astype(float)
    path["low"] = working["low"].astype(float)
    path["close"] = working["close"].astype(float)
    path["daily_return"] = path["price"].pct_change().fillna(0.0)
    path["cumulative_return"] = (path["price"] / first_price) - 1.0
    return path[ADAPTED_PATH_COLUMNS], issues


def _write_outputs(result: dict[str, Any], path_df: pd.DataFrame, normalized_df: pd.DataFrame) -> None:
    _ensure_output_dirs()

    path_output = TABLE_DIR / "phase4_4_historical_price_path.csv"
    normalized_output = TABLE_DIR / "phase4_4_normalized_underlying_prices.csv"
    summary_output = TABLE_DIR / "phase4_4_historical_price_path_summary.csv"
    json_output = REPORT_DIR / "phase4_4_historical_price_path_adapter.json"
    report_output = REPORT_DIR / "phase4_4_historical_price_path_adapter_report.txt"

    path_df.to_csv(path_output, index=False)
    normalized_df.to_csv(normalized_output, index=False)
    pd.DataFrame([result]).drop(columns=["issues", "output_files"]).to_csv(summary_output, index=False)

    json_output.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "Phase 4-4 historical price path adapter report",
        "=" * 70,
        "",
        f"Ready marker:       {result['ready_marker']}",
        f"Release decision:   {result['release_decision']}",
        f"Dashboard change:   {result['dashboard_change_required']}",
        f"Overall status:     {result['overall_status']}",
        f"Source file:        {result['source_file']}",
        f"Source mode:        {result['source_mode']}",
        f"Ticker:             {result['ticker']}",
        f"Input rows:         {result['row_count']}",
        f"Path rows:          {result['path_row_count']}",
        f"First date:         {result['first_date']}",
        f"Last date:          {result['last_date']}",
        f"First price:        {result['first_price']:.2f}",
        f"Last price:         {result['last_price']:.2f}",
        f"Cumulative return:  {result['cumulative_return']:.6f}",
        "",
        "Issues:",
    ]
    if result["issues"]:
        lines.extend(f"- {issue}" for issue in result["issues"])
    else:
        lines.append("- None")
    lines.extend(["", "Outputs:"])
    lines.extend(f"- {name}: {path}" for name, path in result["output_files"].items())
    report_output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_phase4_4_summary(
    underlying_price_file: str | Path | None = None,
    ticker: str | None = None,
    write_outputs: bool = True,
) -> dict[str, Any]:
    """
    Build the Phase 4-4 historical-path adapter summary.

    Returns a plain dictionary so checkpoint scripts and future dashboard code can
    consume it without depending on dataclass internals.
    """
    _ensure_output_dirs()

    source_path = Path(underlying_price_file) if underlying_price_file else DEFAULT_UNDERLYING_PRICE_FILE
    source_existed_before_read = source_path.exists()
    raw_df = _read_underlying_prices(source_path)

    normalized_df, normalization_issues = normalize_underlying_prices(raw_df, ticker=ticker)
    selected_ticker = ticker or (str(normalized_df["ticker"].iloc[0]).upper() if not normalized_df.empty else "UNKNOWN")
    path_df, path_issues = build_historical_price_path(normalized_df, ticker=selected_ticker)

    issues = normalization_issues + path_issues
    output_files = {
        "path_csv": str(TABLE_DIR / "phase4_4_historical_price_path.csv"),
        "normalized_prices_csv": str(TABLE_DIR / "phase4_4_normalized_underlying_prices.csv"),
        "summary_csv": str(TABLE_DIR / "phase4_4_historical_price_path_summary.csv"),
        "json": str(REPORT_DIR / "phase4_4_historical_price_path_adapter.json"),
        "report": str(REPORT_DIR / "phase4_4_historical_price_path_adapter_report.txt"),
    }

    if path_df.empty:
        first_date = ""
        last_date = ""
        first_price = 0.0
        last_price = 0.0
        cumulative_return = 0.0
        path_id = ""
        status = "FAIL"
    else:
        first_date = str(path_df["date"].iloc[0])
        last_date = str(path_df["date"].iloc[-1])
        first_price = float(path_df["price"].iloc[0])
        last_price = float(path_df["price"].iloc[-1])
        cumulative_return = float(path_df["cumulative_return"].iloc[-1])
        path_id = str(path_df["path_id"].iloc[0])
        status = "PASS"

    result = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "dashboard_change_required": DASHBOARD_CHANGE_REQUIRED,
        "overall_status": status,
        "source_file": str(source_path),
        "source_file_exists": source_existed_before_read or source_path.exists(),
        "source_mode": "historical_import",
        "ticker": selected_ticker,
        "row_count": int(len(raw_df)),
        "path_row_count": int(len(path_df)),
        "path_id": path_id,
        "first_date": first_date,
        "last_date": last_date,
        "first_price": first_price,
        "last_price": last_price,
        "cumulative_return": cumulative_return,
        "issue_count": int(len(issues)),
        "issues": issues,
        "output_files": output_files,
    }

    if write_outputs:
        _write_outputs(result, path_df=path_df, normalized_df=normalized_df)

    return result


if __name__ == "__main__":
    summary = build_phase4_4_summary()
    print(json.dumps(summary, indent=2))
