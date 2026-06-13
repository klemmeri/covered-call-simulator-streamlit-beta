"""
position_size_tiers.py

Position-size tier diagnostic for the Covered Call Simulator.

This script compares conservative, balanced, and aggressive position-sizing
tiers for fully covered-call positions.

It does not run simulations.

It does not modify app/main.py.

It does not change any strategy rule.

Input:

    outputs/tables/comparison/current_regime_snapshot.csv

Outputs:

    outputs/tables/comparison/position_size_tiers_summary.csv
    outputs/tables/comparison/position_size_tiers_report.txt

Purpose:

    The position-sizing report answered:

        With one account size and one set of caps, how many contracts fit?

    The account-size sensitivity report answered:

        How much account equity is needed for 1, 2, 3, 5, or 10 contracts?

    This script answers:

        Which tickers become tradable under conservative, balanced,
        and aggressive allocation tiers?

Important:

    This is a first-pass diagnostic.

    It assumes fully covered calls, so one option contract requires 100 shares.

    It does not model margin, taxes, assignment liquidity, bid-ask spread,
    dividends, tax lots, or correlation across tickers.
"""

from pathlib import Path
import math

import pandas as pd


# =============================================================================
# Paths
# =============================================================================

CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "comparison"

CURRENT_REGIME_PATH = OUTPUT_TABLE_DIR / "current_regime_snapshot.csv"

POSITION_SIZE_TIERS_SUMMARY_PATH = (
    OUTPUT_TABLE_DIR / "position_size_tiers_summary.csv"
)

POSITION_SIZE_TIERS_REPORT_PATH = (
    OUTPUT_TABLE_DIR / "position_size_tiers_report.txt"
)


# =============================================================================
# User settings
# =============================================================================

ACCOUNT_EQUITY = 100_000.00

SHARES_PER_CONTRACT = 100

PREFERRED_ROLLING_WINDOW_DAYS = 252

LEVERAGED_TICKERS = {
    "TQQQ",
    "SOXL",
}

POSITION_SIZE_TIERS = {
    "Conservative": {
        "normal_ticker_cap": 0.10,
        "leveraged_ticker_cap": 0.05,
        "total_covered_call_cap": 0.50,
    },
    "Balanced": {
        "normal_ticker_cap": 0.20,
        "leveraged_ticker_cap": 0.10,
        "total_covered_call_cap": 0.80,
    },
    "Aggressive": {
        "normal_ticker_cap": 0.35,
        "leveraged_ticker_cap": 0.20,
        "total_covered_call_cap": 1.00,
    },
}


# =============================================================================
# Formatting helpers
# =============================================================================

def format_currency(value: object) -> str:
    """
    Format a numeric value as dollars.
    """

    value = pd.to_numeric(value, errors="coerce")

    if pd.isna(value):
        return "NA"

    return f"${float(value):,.2f}"


def format_percent(value: object, digits: int = 2) -> str:
    """
    Format a decimal value as a percentage.
    """

    value = pd.to_numeric(value, errors="coerce")

    if pd.isna(value):
        return "NA"

    return f"{100.0 * float(value):,.{digits}f}%"


def format_decimal(value: object, digits: int = 2) -> str:
    """
    Format a decimal value.
    """

    value = pd.to_numeric(value, errors="coerce")

    if pd.isna(value):
        return "NA"

    return f"{float(value):,.{digits}f}"


# =============================================================================
# Data loading
# =============================================================================

def load_current_regime_snapshot() -> pd.DataFrame:
    """
    Load current 252-day regime snapshot.
    """

    required_columns = [
        "Ticker",
        "Rolling_Window_Days",
        "Latest_Date",
        "Latest_Price",
        "Latest_Rolling_Annual_Return",
        "Latest_Rolling_Annual_Volatility",
        "Latest_Detected_Regime",
        "Practical_Rule",
    ]

    if not CURRENT_REGIME_PATH.exists():
        raise FileNotFoundError(
            f"Missing required input file:\n{CURRENT_REGIME_PATH}\n\n"
            "Run app\\current_regime_snapshot.py first."
        )

    df = pd.read_csv(CURRENT_REGIME_PATH)

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns in {CURRENT_REGIME_PATH}:\n"
            f"{missing_columns}"
        )

    df["Rolling_Window_Days"] = pd.to_numeric(
        df["Rolling_Window_Days"],
        errors="coerce",
    )

    df["Latest_Price"] = pd.to_numeric(
        df["Latest_Price"],
        errors="coerce",
    )

    df["Latest_Rolling_Annual_Return"] = pd.to_numeric(
        df["Latest_Rolling_Annual_Return"],
        errors="coerce",
    )

    df["Latest_Rolling_Annual_Volatility"] = pd.to_numeric(
        df["Latest_Rolling_Annual_Volatility"],
        errors="coerce",
    )

    df = df[
        df["Rolling_Window_Days"] == PREFERRED_ROLLING_WINDOW_DAYS
    ].copy()

    df = df.dropna(subset=["Ticker", "Latest_Price"])
    df = df.sort_values("Ticker").reset_index(drop=True)

    return df


# =============================================================================
# Tier calculations
# =============================================================================

def is_leveraged_ticker(ticker: str) -> bool:
    """
    Return True if ticker is treated as leveraged/high risk.
    """

    return ticker.upper() in LEVERAGED_TICKERS


def get_ticker_cap(ticker: str, tier_settings: dict) -> float:
    """
    Return ticker allocation cap for a tier.
    """

    if is_leveraged_ticker(ticker):
        return float(tier_settings["leveraged_ticker_cap"])

    return float(tier_settings["normal_ticker_cap"])


def classify_ticker_risk(ticker: str, annual_volatility: float) -> str:
    """
    Assign a simple qualitative risk label.
    """

    if is_leveraged_ticker(ticker):
        return "Leveraged / high risk"

    if annual_volatility >= 0.40:
        return "High volatility"

    if annual_volatility >= 0.25:
        return "Moderate-high volatility"

    if annual_volatility >= 0.15:
        return "Moderate volatility"

    return "Lower volatility"


def build_position_size_tiers_summary(snapshot_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build one row per ticker per position-size tier.
    """

    rows = []

    for tier_name, tier_settings in POSITION_SIZE_TIERS.items():
        total_cap = float(tier_settings["total_covered_call_cap"])

        for _, row in snapshot_df.iterrows():
            ticker = str(row["Ticker"])
            price = float(row["Latest_Price"])
            annual_volatility = float(row["Latest_Rolling_Annual_Volatility"])

            ticker_cap = get_ticker_cap(
                ticker=ticker,
                tier_settings=tier_settings,
            )

            max_dollar_allocation = ACCOUNT_EQUITY * ticker_cap
            dollars_per_contract = price * SHARES_PER_CONTRACT

            if dollars_per_contract > 0:
                max_contracts = math.floor(
                    max_dollar_allocation / dollars_per_contract
                )
            else:
                max_contracts = 0

            required_shares = max_contracts * SHARES_PER_CONTRACT
            actual_dollar_allocation = required_shares * price

            actual_account_fraction = (
                actual_dollar_allocation / ACCOUNT_EQUITY
                if ACCOUNT_EQUITY > 0
                else 0.0
            )

            minimum_equity_for_one_contract = (
                dollars_per_contract / ticker_cap
                if ticker_cap > 0
                else float("nan")
            )

            if max_contracts >= 1:
                tradable_status = "Tradable"
            else:
                tradable_status = "Not tradable under cap"

            rows.append(
                {
                    "Tier": tier_name,
                    "Ticker": ticker,
                    "Latest_Date": row["Latest_Date"],
                    "Latest_Price": price,
                    "Detected_Regime": row["Latest_Detected_Regime"],
                    "Practical_Rule": row["Practical_Rule"],
                    "Rolling_Annual_Return": row[
                        "Latest_Rolling_Annual_Return"
                    ],
                    "Rolling_Annual_Volatility": annual_volatility,
                    "Risk_Label": classify_ticker_risk(
                        ticker=ticker,
                        annual_volatility=annual_volatility,
                    ),
                    "Ticker_Cap": ticker_cap,
                    "Total_Covered_Call_Cap": total_cap,
                    "Max_Dollar_Allocation": max_dollar_allocation,
                    "Dollars_Per_Contract": dollars_per_contract,
                    "Minimum_Equity_For_One_Contract": (
                        minimum_equity_for_one_contract
                    ),
                    "Max_Contracts": max_contracts,
                    "Required_Shares": required_shares,
                    "Actual_Dollar_Allocation": actual_dollar_allocation,
                    "Actual_Account_Fraction": actual_account_fraction,
                    "Tradable_Status": tradable_status,
                }
            )

    summary_df = pd.DataFrame(rows)

    summary_df["Tier"] = pd.Categorical(
        summary_df["Tier"],
        categories=list(POSITION_SIZE_TIERS.keys()),
        ordered=True,
    )

    summary_df = summary_df.sort_values(
        ["Tier", "Ticker"]
    ).reset_index(drop=True)

    return summary_df


def add_tier_portfolio_totals(summary_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add tier-level portfolio allocation totals.
    """

    df = summary_df.copy()

    tier_totals = (
        df.groupby("Tier", observed=False)["Actual_Dollar_Allocation"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "Actual_Dollar_Allocation": "Tier_Total_Actual_Allocation"
            }
        )
    )

    df = df.merge(
        tier_totals,
        on="Tier",
        how="left",
    )

    df["Tier_Total_Allocation_Fraction"] = (
        df["Tier_Total_Actual_Allocation"] / ACCOUNT_EQUITY
        if ACCOUNT_EQUITY > 0
        else 0.0
    )

    df["Tier_Total_Allocation_OK"] = (
        df["Tier_Total_Allocation_Fraction"]
        <= df["Total_Covered_Call_Cap"]
    )

    return df


# =============================================================================
# Report
# =============================================================================

def build_report(summary_df: pd.DataFrame) -> str:
    """
    Build plain-text position-size tier report.
    """

    lines = []

    lines.append("COVERED CALL SIMULATOR - POSITION SIZE TIERS REPORT")
    lines.append("=" * 100)
    lines.append("")
    lines.append(f"Project folder:                  {PROJECT_ROOT}")
    lines.append(f"Input file:                      {CURRENT_REGIME_PATH}")
    lines.append(f"Output summary file:             {POSITION_SIZE_TIERS_SUMMARY_PATH}")
    lines.append("")
    lines.append(f"Account equity tested:           {format_currency(ACCOUNT_EQUITY)}")
    lines.append(f"Shares per option contract:      {SHARES_PER_CONTRACT}")
    lines.append(f"Preferred rolling window:        {PREFERRED_ROLLING_WINDOW_DAYS} days")
    lines.append("")
    lines.append("Position-size tiers:")
    lines.append("")

    for tier_name, tier_settings in POSITION_SIZE_TIERS.items():
        lines.append(f"    {tier_name}:")
        lines.append(
            f"        normal ticker cap:        "
            f"{format_percent(tier_settings['normal_ticker_cap'])}"
        )
        lines.append(
            f"        leveraged ticker cap:     "
            f"{format_percent(tier_settings['leveraged_ticker_cap'])}"
        )
        lines.append(
            f"        total covered-call cap:   "
            f"{format_percent(tier_settings['total_covered_call_cap'])}"
        )
        lines.append("")

    lines.append("-" * 100)
    lines.append("Tier summaries")
    lines.append("-" * 100)
    lines.append("")

    if summary_df.empty:
        lines.append("No tier rows were created.")
    else:
        for tier_name in POSITION_SIZE_TIERS.keys():
            tier_df = summary_df[
                summary_df["Tier"].astype(str) == tier_name
            ].copy()

            if tier_df.empty:
                continue

            tier_total_allocation = float(
                tier_df["Tier_Total_Actual_Allocation"].iloc[0]
            )
            tier_total_fraction = float(
                tier_df["Tier_Total_Allocation_Fraction"].iloc[0]
            )
            tier_total_cap = float(
                tier_df["Total_Covered_Call_Cap"].iloc[0]
            )
            tier_total_ok = bool(
                tier_df["Tier_Total_Allocation_OK"].iloc[0]
            )

            tradable_count = int(
                (tier_df["Max_Contracts"] >= 1).sum()
            )

            lines.append(f"Tier: {tier_name}")
            lines.append(f"    Tradable tickers:             {tradable_count}")
            lines.append(
                f"    Total actual allocation:      "
                f"{format_currency(tier_total_allocation)}"
            )
            lines.append(
                f"    Total allocation fraction:    "
                f"{format_percent(tier_total_fraction)}"
            )
            lines.append(
                f"    Total allocation cap:         "
                f"{format_percent(tier_total_cap)}"
            )
            lines.append(f"    Total allocation OK:          {tier_total_ok}")
            lines.append("")

            for _, row in tier_df.iterrows():
                lines.append(f"    Ticker: {row['Ticker']}")
                lines.append(f"        Latest price:             {format_currency(row['Latest_Price'])}")
                lines.append(f"        Regime:                   {row['Detected_Regime']}")
                lines.append(f"        Practical rule:           {row['Practical_Rule']}")
                lines.append(f"        Risk label:               {row['Risk_Label']}")
                lines.append(
                    f"        Ticker cap:               "
                    f"{format_percent(row['Ticker_Cap'])}"
                )
                lines.append(
                    f"        Dollars per contract:     "
                    f"{format_currency(row['Dollars_Per_Contract'])}"
                )
                lines.append(
                    f"        Min equity for 1 contract:"
                    f" {format_currency(row['Minimum_Equity_For_One_Contract'])}"
                )
                lines.append(f"        Max contracts:            {int(row['Max_Contracts'])}")
                lines.append(
                    f"        Actual allocation:        "
                    f"{format_currency(row['Actual_Dollar_Allocation'])}"
                )
                lines.append(
                    f"        Account fraction:         "
                    f"{format_percent(row['Actual_Account_Fraction'])}"
                )
                lines.append(f"        Status:                   {row['Tradable_Status']}")
                lines.append("")

    lines.append("-" * 100)
    lines.append("Cross-tier tradability map")
    lines.append("-" * 100)
    lines.append("")

    if summary_df.empty:
        lines.append("No tradability map available.")
    else:
        tickers = sorted(summary_df["Ticker"].astype(str).unique())

        for ticker in tickers:
            ticker_df = summary_df[
                summary_df["Ticker"].astype(str) == ticker
            ].copy()

            lines.append(f"Ticker: {ticker}")

            for tier_name in POSITION_SIZE_TIERS.keys():
                row_df = ticker_df[
                    ticker_df["Tier"].astype(str) == tier_name
                ]

                if row_df.empty:
                    continue

                row = row_df.iloc[0]

                lines.append(
                    f"    {tier_name}: "
                    f"{int(row['Max_Contracts'])} contract(s), "
                    f"{row['Tradable_Status']}"
                )

            lines.append("")

    lines.append("-" * 100)
    lines.append("Interpretation")
    lines.append("-" * 100)
    lines.append("")
    lines.append(
        "This report shows how tradability changes as the allocation caps become "
        "more conservative or more aggressive."
    )
    lines.append("")
    lines.append(
        "A ticker may have a valid covered-call management rule but still be too "
        "large for the account under conservative or balanced caps."
    )
    lines.append("")
    lines.append(
        "For a user-facing dashboard, this tier view is useful because users can "
        "select their risk posture before seeing which tickers are practical."
    )
    lines.append("")
    lines.append(
        "The tier labels are not recommendations. They are allocation scenarios."
    )
    lines.append("")

    lines.append("-" * 100)
    lines.append("Limitations")
    lines.append("-" * 100)
    lines.append("")
    lines.append("This first-pass tier diagnostic does not model:")
    lines.append("")
    lines.append("    taxes")
    lines.append("    margin")
    lines.append("    option liquidity")
    lines.append("    dividend timing")
    lines.append("    correlation across tickers")
    lines.append("    drawdown-based exposure cuts")
    lines.append("    user-specific risk tolerance")
    lines.append("    IRA versus taxable-account constraints")
    lines.append("")

    lines.append("=" * 100)
    lines.append("Overall conclusion")
    lines.append("=" * 100)
    lines.append("")

    lines.append(
        "Use this report with the position-sizing and account-size sensitivity "
        "reports. Together, they define the first-pass practical tradability "
        "layer for the simulator."
    )
    lines.append("")
    lines.append(
        "Recommended next step: update the dashboard report to include "
        "position-sizing, account-size sensitivity, and tier tradability."
    )

    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)

    snapshot_df = load_current_regime_snapshot()

    summary_df = build_position_size_tiers_summary(snapshot_df)
    summary_df = add_tier_portfolio_totals(summary_df)

    summary_df.to_csv(POSITION_SIZE_TIERS_SUMMARY_PATH, index=False)

    report_text = build_report(summary_df)
    POSITION_SIZE_TIERS_REPORT_PATH.write_text(
        report_text,
        encoding="utf-8",
    )

    print("")
    print("=" * 100)
    print("Position size tiers report complete.")
    print("=" * 100)
    print("")
    print("Saved files:")
    print(f"  {POSITION_SIZE_TIERS_SUMMARY_PATH}")
    print(f"  {POSITION_SIZE_TIERS_REPORT_PATH}")
    print("")
    print("Done.")
    print("")


if __name__ == "__main__":
    main()