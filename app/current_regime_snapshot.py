"""
current_regime_snapshot.py

Current regime snapshot for the Covered Call Simulator.

This script reads the rolling-regime output created by:

    app/rolling_regime_detection.py

It extracts the latest detected regime for the preferred rolling window.

Default preferred window:

    252 trading days

This creates a simple current-regime dashboard before connecting any regime
logic to the main simulator.

This is a standalone diagnostic script.

It does not modify app/main.py.

Input file:

    outputs/tables/comparison/rolling_regime_detection_latest.csv

Outputs:

    outputs/tables/comparison/current_regime_snapshot.csv
    outputs/tables/comparison/current_regime_snapshot_report.txt
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

INPUT_PATH = OUTPUT_TABLE_DIR / "rolling_regime_detection_latest.csv"

SNAPSHOT_PATH = OUTPUT_TABLE_DIR / "current_regime_snapshot.csv"
REPORT_PATH = OUTPUT_TABLE_DIR / "current_regime_snapshot_report.txt"


# =============================================================================
# User settings
# =============================================================================

PREFERRED_ROLLING_WINDOW_DAYS = 252

# These are the rules currently implied by the adaptive strategy map at
# default DTE and low transaction costs.
REGIME_TO_PRACTICAL_RULE = {
    "baseline": "Wait10d",
    "sideways_market": "Close50",
    "bullish_market": "Wait10d",
    "bearish_market": "Close50",
    "high_volatility": "Wait10d",
    "low_volatility": "Wait10d",
}


# =============================================================================
# Formatting helpers
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


# =============================================================================
# Core logic
# =============================================================================

def load_latest_regime_table() -> pd.DataFrame:
    """
    Load rolling_regime_detection_latest.csv.
    """

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Missing input file: {INPUT_PATH}\n"
            "Run app\\rolling_regime_detection.py first."
        )

    df = pd.read_csv(INPUT_PATH)

    required_columns = [
        "Ticker",
        "Rolling_Window_Days",
        "Latest_Date",
        "Latest_Price",
        "Latest_Rolling_Cumulative_Return",
        "Latest_Rolling_Annual_Return",
        "Latest_Rolling_Annual_Volatility",
        "Latest_Detected_Regime",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "The latest regime file is missing required columns:\n"
            f"{missing_columns}"
        )

    return df


def build_snapshot(latest_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract the preferred rolling-window current regime snapshot.
    """

    df = latest_df.copy()

    df["Rolling_Window_Days"] = pd.to_numeric(
        df["Rolling_Window_Days"],
        errors="coerce",
    )

    snapshot_df = df[
        df["Rolling_Window_Days"] == PREFERRED_ROLLING_WINDOW_DAYS
    ].copy()

    if snapshot_df.empty:
        raise ValueError(
            f"No rows found for preferred rolling window: "
            f"{PREFERRED_ROLLING_WINDOW_DAYS}"
        )

    snapshot_df["Practical_Rule"] = snapshot_df[
        "Latest_Detected_Regime"
    ].map(REGIME_TO_PRACTICAL_RULE)

    snapshot_df["Practical_Rule"] = snapshot_df[
        "Practical_Rule"
    ].fillna("Review manually")

    snapshot_df = snapshot_df.sort_values("Ticker").reset_index(drop=True)

    output_columns = [
        "Ticker",
        "Rolling_Window_Days",
        "Latest_Date",
        "Latest_Price",
        "Latest_Rolling_Cumulative_Return",
        "Latest_Rolling_Annual_Return",
        "Latest_Rolling_Annual_Volatility",
        "Latest_Detected_Regime",
        "Practical_Rule",
    ]

    return snapshot_df[output_columns].copy()


def build_report(snapshot_df: pd.DataFrame) -> str:
    """
    Build a plain-text current regime snapshot report.
    """

    lines = []

    lines.append("COVERED CALL SIMULATOR - CURRENT REGIME SNAPSHOT REPORT")
    lines.append("=" * 100)
    lines.append("")
    lines.append(f"Input file:                 {INPUT_PATH}")
    lines.append(f"Snapshot file:              {SNAPSHOT_PATH}")
    lines.append(f"Preferred rolling window:   {PREFERRED_ROLLING_WINDOW_DAYS} trading days")
    lines.append("")
    lines.append(
        "This report extracts the latest detected regime from the rolling "
        "historical regime detector."
    )
    lines.append("")
    lines.append(
        "It is a diagnostic dashboard only. It should not be wired into "
        "app/main.py yet."
    )
    lines.append("")
    lines.append("-" * 100)
    lines.append("Current regime snapshot")
    lines.append("-" * 100)
    lines.append("")

    for _, row in snapshot_df.iterrows():
        lines.append(f"Ticker: {row['Ticker']}")
        lines.append(f"    Latest date:                  {row['Latest_Date']}")
        lines.append(f"    Rolling window:               {int(row['Rolling_Window_Days'])} trading days")
        lines.append(f"    Latest price:                 {format_decimal(row['Latest_Price'], 2)}")
        lines.append(
            f"    Rolling cumulative return:    "
            f"{format_percent(row['Latest_Rolling_Cumulative_Return'])}"
        )
        lines.append(
            f"    Rolling annual return:        "
            f"{format_percent(row['Latest_Rolling_Annual_Return'])}"
        )
        lines.append(
            f"    Rolling annual volatility:    "
            f"{format_percent(row['Latest_Rolling_Annual_Volatility'])}"
        )
        lines.append(f"    Detected regime:              {row['Latest_Detected_Regime']}")
        lines.append(f"    Practical rule:               {row['Practical_Rule']}")
        lines.append("")

    regime_counts = (
        snapshot_df["Latest_Detected_Regime"]
        .value_counts()
        .sort_index()
    )

    practical_rule_counts = (
        snapshot_df["Practical_Rule"]
        .value_counts()
        .sort_index()
    )

    lines.append("-" * 100)
    lines.append("Regime counts")
    lines.append("-" * 100)
    lines.append("")

    for regime, count in regime_counts.items():
        lines.append(f"{regime:<20} {int(count)}")

    lines.append("")
    lines.append("-" * 100)
    lines.append("Practical-rule counts")
    lines.append("-" * 100)
    lines.append("")

    for rule, count in practical_rule_counts.items():
        lines.append(f"{rule:<20} {int(count)}")

    lines.append("")
    lines.append("=" * 100)
    lines.append("Overall conclusion")
    lines.append("=" * 100)
    lines.append("")
    lines.append(f"Tickers in snapshot:        {len(snapshot_df)}")
    lines.append(f"Rolling window used:        {PREFERRED_ROLLING_WINDOW_DAYS} trading days")
    lines.append("")

    unique_rules = sorted(snapshot_df["Practical_Rule"].dropna().unique())

    if len(unique_rules) == 1:
        lines.append(
            f"All tickers currently map to the same practical rule: {unique_rules[0]}."
        )
    else:
        lines.append(
            "The current snapshot contains more than one practical rule. "
            "Review ticker-level regimes before using this as a trading guide."
        )

    lines.append("")
    lines.append(
        "Recommendation: keep this as a standalone diagnostic for now. "
        "Use it to monitor whether the rolling 252-day regime classification "
        "stays stable and intuitive."
    )

    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)

    print("")
    print("=" * 100)
    print("COVERED CALL SIMULATOR - CURRENT REGIME SNAPSHOT")
    print("=" * 100)
    print(f"Input file:               {INPUT_PATH}")
    print(f"Preferred rolling window: {PREFERRED_ROLLING_WINDOW_DAYS}")
    print("=" * 100)
    print("")

    latest_df = load_latest_regime_table()
    snapshot_df = build_snapshot(latest_df)

    snapshot_df.to_csv(SNAPSHOT_PATH, index=False)

    report_text = build_report(snapshot_df)
    REPORT_PATH.write_text(report_text, encoding="utf-8")

    print("Current regime snapshot:")
    print(snapshot_df.to_string(index=False))
    print("")
    print("Saved files:")
    print(f"  {SNAPSHOT_PATH}")
    print(f"  {REPORT_PATH}")
    print("")
    print("Done.")
    print("")


if __name__ == "__main__":
    main()