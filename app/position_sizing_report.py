"""
position_sizing_report.py

Position-sizing diagnostic for the Covered Call Simulator.

This script reads the current regime snapshot and estimates how many covered-call
contracts could be traded per ticker under simple account-size and allocation
limits.

It does not run new simulations.

It does not modify app/main.py.

It does not change any strategy rule.

Input:

    outputs/tables/comparison/current_regime_snapshot.csv

Output:

    outputs/tables/comparison/position_sizing_summary.csv
    outputs/tables/comparison/position_sizing_report.txt

Purpose:

    Add a basic risk-management layer before moving toward a user-facing
    dashboard or website.

    Covered-call rules answer:

        What should I do with the short call?

    Position sizing answers:

        How large should the position be?

Important:

    This is a first-pass diagnostic.

    It assumes fully covered calls, so one option contract requires 100 shares.

    It does not yet model margin, taxes, assignment liquidity, option bid-ask
    width, dividend risk, or tax-lot management.
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

POSITION_SIZING_SUMMARY_PATH = (
    OUTPUT_TABLE_DIR / "position_sizing_summary.csv"
)

POSITION_SIZING_REPORT_PATH = (
    OUTPUT_TABLE_DIR / "position_sizing_report.txt"
)


# =============================================================================
# User settings
# =============================================================================

# Change this to the account size you want to test.
ACCOUNT_EQUITY = 100_000.00

# Maximum fraction of total account equity allowed in one ticker.
MAX_SINGLE_TICKER_ALLOCATION_FRACTION = 0.20

# Maximum fraction of total account equity allowed in all covered-call
# positions combined.
MAX_TOTAL_COVERED_CALL_ALLOCATION_FRACTION = 0.80

# Covered-call contract size.
SHARES_PER_CONTRACT = 100

# Optional ticker-level caps.
#
# If a ticker is not listed here, the default MAX_SINGLE_TICKER_ALLOCATION_FRACTION
# is used.
#
# Leveraged ETFs are capped more conservatively by default.
TICKER_ALLOCATION_CAPS = {
    "SPY": 0.20,
    "QQQ": 0.20,
    "IWM": 0.20,
    "TQQQ": 0.10,
    "SOXL": 0.10,
}

# Risk labels are qualitative only.
LEVERAGED_TICKERS = {
    "TQQQ",
    "SOXL",
}

# Preferred rolling window used elsewhere in the project.
PREFERRED_ROLLING_WINDOW_DAYS = 252


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
# Load data
# =============================================================================

def load_current_regime_snapshot() -> pd.DataFrame:
    """
    Load current regime snapshot.
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
# Position sizing
# =============================================================================

def get_ticker_allocation_cap(ticker: str) -> float:
    """
    Return ticker-specific allocation cap.
    """

    return float(
        TICKER_ALLOCATION_CAPS.get(
            ticker,
            MAX_SINGLE_TICKER_ALLOCATION_FRACTION,
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


def build_position_sizing_summary(snapshot_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build the position-sizing summary table.
    """

    rows = []

    for _, row in snapshot_df.iterrows():
        ticker = str(row["Ticker"])
        price = float(row["Latest_Price"])
        annual_volatility = float(row["Latest_Rolling_Annual_Volatility"])

        ticker_cap_fraction = get_ticker_allocation_cap(ticker)
        max_dollar_allocation = ACCOUNT_EQUITY * ticker_cap_fraction

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

        unused_allocation = max_dollar_allocation - actual_dollar_allocation

        if max_contracts <= 0:
            sizing_status = "Too expensive for current cap"
        elif ticker in LEVERAGED_TICKERS:
            sizing_status = "Use reduced cap"
        else:
            sizing_status = "Tradable under cap"

        rows.append(
            {
                "Ticker": ticker,
                "Latest_Date": row["Latest_Date"],
                "Latest_Price": price,
                "Detected_Regime": row["Latest_Detected_Regime"],
                "Practical_Rule": row["Practical_Rule"],
                "Rolling_Annual_Return": row["Latest_Rolling_Annual_Return"],
                "Rolling_Annual_Volatility": annual_volatility,
                "Risk_Label": classify_ticker_risk(
                    ticker=ticker,
                    annual_volatility=annual_volatility,
                ),
                "Ticker_Cap_Fraction": ticker_cap_fraction,
                "Max_Dollar_Allocation": max_dollar_allocation,
                "Dollars_Per_Contract": dollars_per_contract,
                "Max_Contracts": max_contracts,
                "Required_Shares": required_shares,
                "Actual_Dollar_Allocation": actual_dollar_allocation,
                "Actual_Account_Fraction": actual_account_fraction,
                "Unused_Allocation": unused_allocation,
                "Sizing_Status": sizing_status,
            }
        )

    summary_df = pd.DataFrame(rows)

    return summary_df


def apply_total_allocation_check(summary_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add total allocation status.

    The first-pass table sizes each ticker independently. This function adds a
    portfolio-level check showing whether the sum of all suggested positions
    would exceed the total covered-call allocation limit.
    """

    df = summary_df.copy()

    total_actual_allocation = float(
        pd.to_numeric(
            df["Actual_Dollar_Allocation"],
            errors="coerce",
        ).fillna(0).sum()
    )

    max_total_allocation = (
        ACCOUNT_EQUITY * MAX_TOTAL_COVERED_CALL_ALLOCATION_FRACTION
    )

    total_allocation_fraction = (
        total_actual_allocation / ACCOUNT_EQUITY
        if ACCOUNT_EQUITY > 0
        else 0.0
    )

    total_allocation_ok = total_actual_allocation <= max_total_allocation

    df["Total_Actual_Covered_Call_Allocation"] = total_actual_allocation
    df["Max_Total_Covered_Call_Allocation"] = max_total_allocation
    df["Total_Covered_Call_Allocation_Fraction"] = total_allocation_fraction
    df["Total_Allocation_OK"] = total_allocation_ok

    return df


# =============================================================================
# Report
# =============================================================================

def build_report(summary_df: pd.DataFrame) -> str:
    """
    Build the plain-text position-sizing report.
    """

    total_actual_allocation = 0.0
    max_total_allocation = (
        ACCOUNT_EQUITY * MAX_TOTAL_COVERED_CALL_ALLOCATION_FRACTION
    )
    total_allocation_fraction = 0.0
    total_allocation_ok = True

    if not summary_df.empty:
        total_actual_allocation = float(
            summary_df["Total_Actual_Covered_Call_Allocation"].iloc[0]
        )
        total_allocation_fraction = float(
            summary_df["Total_Covered_Call_Allocation_Fraction"].iloc[0]
        )
        total_allocation_ok = bool(
            summary_df["Total_Allocation_OK"].iloc[0]
        )

    lines = []

    lines.append("COVERED CALL SIMULATOR - POSITION SIZING REPORT")
    lines.append("=" * 100)
    lines.append("")
    lines.append(f"Project folder:                         {PROJECT_ROOT}")
    lines.append(f"Input file:                             {CURRENT_REGIME_PATH}")
    lines.append(f"Output summary file:                    {POSITION_SIZING_SUMMARY_PATH}")
    lines.append("")
    lines.append(f"Account equity tested:                  {format_currency(ACCOUNT_EQUITY)}")
    lines.append(
        f"Default max single-ticker allocation:   "
        f"{format_percent(MAX_SINGLE_TICKER_ALLOCATION_FRACTION)}"
    )
    lines.append(
        f"Max total covered-call allocation:      "
        f"{format_percent(MAX_TOTAL_COVERED_CALL_ALLOCATION_FRACTION)}"
    )
    lines.append(f"Shares per option contract:             {SHARES_PER_CONTRACT}")
    lines.append(f"Preferred rolling window:               {PREFERRED_ROLLING_WINDOW_DAYS} days")
    lines.append("")
    lines.append("-" * 100)
    lines.append("Ticker-level sizing")
    lines.append("-" * 100)
    lines.append("")

    if summary_df.empty:
        lines.append("No position-sizing rows were created.")
    else:
        for _, row in summary_df.iterrows():
            lines.append(f"Ticker: {row['Ticker']}")
            lines.append(f"    Latest date:                  {row['Latest_Date']}")
            lines.append(f"    Latest price:                 {format_currency(row['Latest_Price'])}")
            lines.append(f"    Detected regime:              {row['Detected_Regime']}")
            lines.append(f"    Practical rule:               {row['Practical_Rule']}")
            lines.append(
                f"    Rolling annual return:        "
                f"{format_percent(row['Rolling_Annual_Return'])}"
            )
            lines.append(
                f"    Rolling annual volatility:    "
                f"{format_percent(row['Rolling_Annual_Volatility'])}"
            )
            lines.append(f"    Risk label:                   {row['Risk_Label']}")
            lines.append(
                f"    Ticker allocation cap:        "
                f"{format_percent(row['Ticker_Cap_Fraction'])}"
            )
            lines.append(
                f"    Max dollar allocation:        "
                f"{format_currency(row['Max_Dollar_Allocation'])}"
            )
            lines.append(
                f"    Dollars per 1 contract:       "
                f"{format_currency(row['Dollars_Per_Contract'])}"
            )
            lines.append(f"    Max contracts:                {int(row['Max_Contracts'])}")
            lines.append(f"    Required shares:              {int(row['Required_Shares'])}")
            lines.append(
                f"    Actual dollar allocation:     "
                f"{format_currency(row['Actual_Dollar_Allocation'])}"
            )
            lines.append(
                f"    Actual account fraction:      "
                f"{format_percent(row['Actual_Account_Fraction'])}"
            )
            lines.append(
                f"    Unused allocation:            "
                f"{format_currency(row['Unused_Allocation'])}"
            )
            lines.append(f"    Sizing status:                {row['Sizing_Status']}")
            lines.append("")

    lines.append("-" * 100)
    lines.append("Portfolio-level allocation check")
    lines.append("-" * 100)
    lines.append("")
    lines.append(
        f"Total covered-call allocation:          "
        f"{format_currency(total_actual_allocation)}"
    )
    lines.append(
        f"Total covered-call allocation fraction: "
        f"{format_percent(total_allocation_fraction)}"
    )
    lines.append(
        f"Maximum allowed total allocation:       "
        f"{format_currency(max_total_allocation)}"
    )
    lines.append(f"Total allocation OK:                    {total_allocation_ok}")
    lines.append("")

    lines.append("-" * 100)
    lines.append("Interpretation")
    lines.append("-" * 100)
    lines.append("")
    lines.append(
        "This report adds a first-pass position-sizing layer to the covered-call "
        "strategy research."
    )
    lines.append("")
    lines.append(
        "The trading-rule diagnostics answer which management rule appears most "
        "appropriate under each regime."
    )
    lines.append("")
    lines.append(
        "This report answers how many fully covered option contracts could be "
        "traded without exceeding simple allocation caps."
    )
    lines.append("")
    lines.append(
        "A ticker can have a valid strategy rule but still be too expensive for "
        "a small account under the chosen allocation cap."
    )
    lines.append("")
    lines.append(
        "Leveraged tickers such as TQQQ and SOXL are capped more conservatively "
        "by default because their realized volatility is much higher."
    )
    lines.append("")

    lines.append("-" * 100)
    lines.append("Limitations")
    lines.append("-" * 100)
    lines.append("")
    lines.append("This first-pass sizing report does not yet model:")
    lines.append("")
    lines.append("    taxes")
    lines.append("    margin")
    lines.append("    assignment liquidity")
    lines.append("    option bid-ask width")
    lines.append("    dividend timing")
    lines.append("    tax-lot selection")
    lines.append("    correlation across tickers")
    lines.append("    drawdown-based exposure cuts")
    lines.append("")

    lines.append("=" * 100)
    lines.append("Overall conclusion")
    lines.append("=" * 100)
    lines.append("")

    if total_allocation_ok:
        lines.append(
            "PASS: The independently sized ticker positions fit within the "
            "portfolio-level covered-call allocation cap."
        )
    else:
        lines.append(
            "REVIEW REQUIRED: The independently sized ticker positions exceed "
            "the portfolio-level covered-call allocation cap. Reduce one or "
            "more ticker allocations."
        )

    lines.append("")
    lines.append(
        "Recommended next step after this report: review the allocation caps, "
        "then decide whether to add taxable-account versus IRA assumptions or "
        "move toward a user-facing dashboard."
    )

    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)

    snapshot_df = load_current_regime_snapshot()

    summary_df = build_position_sizing_summary(snapshot_df)
    summary_df = apply_total_allocation_check(summary_df)

    summary_df.to_csv(POSITION_SIZING_SUMMARY_PATH, index=False)

    report_text = build_report(summary_df)
    POSITION_SIZING_REPORT_PATH.write_text(report_text, encoding="utf-8")

    print("")
    print("=" * 100)
    print("Position sizing report complete.")
    print("=" * 100)
    print("")
    print("Saved files:")
    print(f"  {POSITION_SIZING_SUMMARY_PATH}")
    print(f"  {POSITION_SIZING_REPORT_PATH}")
    print("")
    print("Done.")
    print("")


if __name__ == "__main__":
    main()