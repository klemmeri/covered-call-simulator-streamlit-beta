"""
account_size_sensitivity.py

Account-size sensitivity diagnostic for the Covered Call Simulator.

This script estimates the minimum account equity needed to trade 1, 2, 3,
or more fully covered-call contracts for each ticker under the current
ticker-level allocation caps.

It does not run new simulations.

It does not modify app/main.py.

It does not change any strategy rule.

Input:

    outputs/tables/comparison/current_regime_snapshot.csv

Outputs:

    outputs/tables/comparison/account_size_sensitivity_summary.csv
    outputs/tables/comparison/account_size_sensitivity_report.txt

Purpose:

    The position-sizing report answered:

        Given a fixed account size, how many covered-call contracts fit?

    This script answers the reverse question:

        Given a desired number of covered-call contracts, how large must
        the account be?

Important:

    This is a first-pass diagnostic.

    It assumes fully covered calls, so one option contract requires 100 shares.

    It does not model margin, taxes, assignment liquidity, option bid-ask width,
    dividends, tax lots, or correlation across tickers.
"""

from pathlib import Path

import pandas as pd


# =============================================================================
# Paths
# =============================================================================

CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "comparison"

CURRENT_REGIME_PATH = OUTPUT_TABLE_DIR / "current_regime_snapshot.csv"

ACCOUNT_SIZE_SUMMARY_PATH = (
    OUTPUT_TABLE_DIR / "account_size_sensitivity_summary.csv"
)

ACCOUNT_SIZE_REPORT_PATH = (
    OUTPUT_TABLE_DIR / "account_size_sensitivity_report.txt"
)


# =============================================================================
# User settings
# =============================================================================

SHARES_PER_CONTRACT = 100

PREFERRED_ROLLING_WINDOW_DAYS = 252

TARGET_CONTRACT_COUNTS = [
    1,
    2,
    3,
    5,
    10,
]

DEFAULT_SINGLE_TICKER_ALLOCATION_CAP = 0.20

TICKER_ALLOCATION_CAPS = {
    "SPY": 0.20,
    "QQQ": 0.20,
    "IWM": 0.20,
    "TQQQ": 0.10,
    "SOXL": 0.10,
}

LEVERAGED_TICKERS = {
    "TQQQ",
    "SOXL",
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
    Load the current 252-day regime snapshot.
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
# Account-size calculations
# =============================================================================

def get_ticker_allocation_cap(ticker: str) -> float:
    """
    Return ticker-specific allocation cap.
    """

    return float(
        TICKER_ALLOCATION_CAPS.get(
            ticker,
            DEFAULT_SINGLE_TICKER_ALLOCATION_CAP,
        )
    )


def classify_ticker_risk(ticker: str, annual_volatility: float) -> str:
    """
    Assign a simple qualitative risk label.
    """

    if ticker in LEVERAGED_TICKERS:
        return "Leveraged / high risk"

    if annual_volatility >= 0.40:
        return "High volatility"

    if annual_volatility >= 0.25:
        return "Moderate-high volatility"

    if annual_volatility >= 0.15:
        return "Moderate volatility"

    return "Lower volatility"


def calculate_required_account_equity(
    price: float,
    contract_count: int,
    allocation_cap: float,
) -> float:
    """
    Calculate account equity required to hold a target number of covered-call
    contracts without exceeding the ticker allocation cap.

    Formula:

        required account equity =
            shares required x share price / allocation cap
    """

    if allocation_cap <= 0:
        return float("nan")

    shares_required = contract_count * SHARES_PER_CONTRACT
    position_value = shares_required * price

    return position_value / allocation_cap


def build_account_size_summary(snapshot_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build account-size sensitivity table.
    """

    rows = []

    for _, row in snapshot_df.iterrows():
        ticker = str(row["Ticker"])
        price = float(row["Latest_Price"])
        annual_volatility = float(row["Latest_Rolling_Annual_Volatility"])

        allocation_cap = get_ticker_allocation_cap(ticker)
        dollars_per_contract = price * SHARES_PER_CONTRACT

        risk_label = classify_ticker_risk(
            ticker=ticker,
            annual_volatility=annual_volatility,
        )

        for contract_count in TARGET_CONTRACT_COUNTS:
            shares_required = contract_count * SHARES_PER_CONTRACT
            position_value = shares_required * price

            required_account_equity = calculate_required_account_equity(
                price=price,
                contract_count=contract_count,
                allocation_cap=allocation_cap,
            )

            rows.append(
                {
                    "Ticker": ticker,
                    "Latest_Date": row["Latest_Date"],
                    "Latest_Price": price,
                    "Detected_Regime": row["Latest_Detected_Regime"],
                    "Practical_Rule": row["Practical_Rule"],
                    "Rolling_Annual_Return": row[
                        "Latest_Rolling_Annual_Return"
                    ],
                    "Rolling_Annual_Volatility": annual_volatility,
                    "Risk_Label": risk_label,
                    "Ticker_Allocation_Cap": allocation_cap,
                    "Target_Contracts": contract_count,
                    "Shares_Required": shares_required,
                    "Dollars_Per_Contract": dollars_per_contract,
                    "Position_Value": position_value,
                    "Required_Account_Equity": required_account_equity,
                }
            )

    summary_df = pd.DataFrame(rows)

    summary_df = summary_df.sort_values(
        [
            "Ticker",
            "Target_Contracts",
        ]
    ).reset_index(drop=True)

    return summary_df


# =============================================================================
# Report
# =============================================================================

def build_report(summary_df: pd.DataFrame) -> str:
    """
    Build plain-text account-size sensitivity report.
    """

    lines = []

    lines.append("COVERED CALL SIMULATOR - ACCOUNT SIZE SENSITIVITY REPORT")
    lines.append("=" * 100)
    lines.append("")
    lines.append(f"Project folder:                  {PROJECT_ROOT}")
    lines.append(f"Input file:                      {CURRENT_REGIME_PATH}")
    lines.append(f"Output summary file:             {ACCOUNT_SIZE_SUMMARY_PATH}")
    lines.append("")
    lines.append(f"Preferred rolling window:         {PREFERRED_ROLLING_WINDOW_DAYS} days")
    lines.append(f"Shares per option contract:       {SHARES_PER_CONTRACT}")
    lines.append(
        f"Default ticker allocation cap:    "
        f"{format_percent(DEFAULT_SINGLE_TICKER_ALLOCATION_CAP)}"
    )
    lines.append("")
    lines.append("Target contract counts tested:")
    lines.append(f"    {TARGET_CONTRACT_COUNTS}")
    lines.append("")

    lines.append("-" * 100)
    lines.append("Ticker-level account-size requirements")
    lines.append("-" * 100)
    lines.append("")

    if summary_df.empty:
        lines.append("No account-size sensitivity rows were created.")
    else:
        for ticker in sorted(summary_df["Ticker"].astype(str).unique()):
            ticker_df = summary_df[
                summary_df["Ticker"].astype(str) == ticker
            ].copy()

            first_row = ticker_df.iloc[0]

            lines.append(f"Ticker: {ticker}")
            lines.append(f"    Latest date:                  {first_row['Latest_Date']}")
            lines.append(f"    Latest price:                 {format_currency(first_row['Latest_Price'])}")
            lines.append(f"    Detected regime:              {first_row['Detected_Regime']}")
            lines.append(f"    Practical rule:               {first_row['Practical_Rule']}")
            lines.append(
                f"    Rolling annual return:        "
                f"{format_percent(first_row['Rolling_Annual_Return'])}"
            )
            lines.append(
                f"    Rolling annual volatility:    "
                f"{format_percent(first_row['Rolling_Annual_Volatility'])}"
            )
            lines.append(f"    Risk label:                   {first_row['Risk_Label']}")
            lines.append(
                f"    Allocation cap:               "
                f"{format_percent(first_row['Ticker_Allocation_Cap'])}"
            )
            lines.append(
                f"    Dollars per 1 contract:       "
                f"{format_currency(first_row['Dollars_Per_Contract'])}"
            )
            lines.append("")
            lines.append("    Required account equity:")
            lines.append("")

            for _, row in ticker_df.iterrows():
                lines.append(
                    f"        {int(row['Target_Contracts'])} contract(s): "
                    f"{format_currency(row['Required_Account_Equity'])}"
                )

            lines.append("")

    lines.append("-" * 100)
    lines.append("Minimum account equity for 1 contract")
    lines.append("-" * 100)
    lines.append("")

    one_contract_df = summary_df[
        pd.to_numeric(
            summary_df["Target_Contracts"],
            errors="coerce",
        ) == 1
    ].copy()

    if one_contract_df.empty:
        lines.append("No one-contract rows were available.")
    else:
        one_contract_df = one_contract_df.sort_values(
            "Required_Account_Equity"
        )

        for _, row in one_contract_df.iterrows():
            lines.append(
                f"{row['Ticker']}: "
                f"{format_currency(row['Required_Account_Equity'])} "
                f"at {format_percent(row['Ticker_Allocation_Cap'])} cap"
            )

    lines.append("")
    lines.append("-" * 100)
    lines.append("Interpretation")
    lines.append("-" * 100)
    lines.append("")
    lines.append(
        "This report shows why fully covered-call trading is capital intensive."
    )
    lines.append("")
    lines.append(
        "One covered-call contract requires 100 shares. For high-priced ETFs "
        "such as SPY and QQQ, that can require a large account if the position "
        "is constrained to 20% of equity."
    )
    lines.append("")
    lines.append(
        "Leveraged ETFs such as TQQQ and SOXL use a smaller allocation cap in "
        "this diagnostic because their realized volatility is much higher."
    )
    lines.append("")
    lines.append(
        "A ticker can have a valid strategy rule but still be impractical for "
        "a small account under the chosen allocation cap."
    )
    lines.append("")

    lines.append("-" * 100)
    lines.append("Limitations")
    lines.append("-" * 100)
    lines.append("")
    lines.append("This first-pass account-size diagnostic does not model:")
    lines.append("")
    lines.append("    margin")
    lines.append("    taxes")
    lines.append("    assignment liquidity")
    lines.append("    option bid-ask width")
    lines.append("    dividend timing")
    lines.append("    tax-lot selection")
    lines.append("    portfolio correlation")
    lines.append("    drawdown-based exposure cuts")
    lines.append("    partial-share alternatives")
    lines.append("    poor man's covered-call alternatives")
    lines.append("")

    lines.append("=" * 100)
    lines.append("Overall conclusion")
    lines.append("=" * 100)
    lines.append("")
    lines.append(
        "This report should be used with the position-sizing report. Together, "
        "they show which tickers fit a given account and how much account "
        "equity is required for each target contract count."
    )
    lines.append("")
    lines.append(
        "Recommended next step: decide whether to add position-size tiers "
        "such as conservative, balanced, and aggressive."
    )

    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)

    snapshot_df = load_current_regime_snapshot()
    summary_df = build_account_size_summary(snapshot_df)

    summary_df.to_csv(ACCOUNT_SIZE_SUMMARY_PATH, index=False)

    report_text = build_report(summary_df)
    ACCOUNT_SIZE_REPORT_PATH.write_text(report_text, encoding="utf-8")

    print("")
    print("=" * 100)
    print("Account size sensitivity report complete.")
    print("=" * 100)
    print("")
    print("Saved files:")
    print(f"  {ACCOUNT_SIZE_SUMMARY_PATH}")
    print(f"  {ACCOUNT_SIZE_REPORT_PATH}")
    print("")
    print("Done.")
    print("")


if __name__ == "__main__":
    main()