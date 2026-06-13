"""
strategy_dashboard_report.py

Compact strategy dashboard report for the Covered Call Simulator.

This script combines the most important diagnostic outputs into one concise
dashboard report.

It does not run new simulations.

It reads existing output files created by:

    app/current_regime_snapshot.py
    app/historical_window_calibration.py
    app/rolling_strategy_calibration.py
    app/position_sizing_report.py
    app/account_size_sensitivity.py
    app/position_size_tiers.py

Primary inputs:

    outputs/tables/comparison/current_regime_snapshot.csv
    outputs/tables/comparison/historical_window_calibration_winners.csv
    outputs/tables/comparison/rolling_strategy_calibration_stability.csv
    outputs/tables/comparison/position_sizing_summary.csv
    outputs/tables/comparison/account_size_sensitivity_summary.csv
    outputs/tables/comparison/position_size_tiers_summary.csv

Output:

    outputs/tables/comparison/strategy_dashboard_report.txt

Purpose:

    Provide one compact summary of the current strategy state.

    This dashboard now combines:

        strategy validity
        current regime and rule
        historical-window validation
        rolling-window strategy validation
        fixed-account position sizing
        minimum account-size requirements
        conservative / balanced / aggressive tradability tiers

Important:

    This is a standalone reporting script.

    It does not modify app/main.py.
    It does not change strategy rules.
    It does not run Monte Carlo simulations.
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

HISTORICAL_WINDOW_WINNERS_PATH = (
    OUTPUT_TABLE_DIR / "historical_window_calibration_winners.csv"
)

ROLLING_STRATEGY_STABILITY_PATH = (
    OUTPUT_TABLE_DIR / "rolling_strategy_calibration_stability.csv"
)

POSITION_SIZING_SUMMARY_PATH = (
    OUTPUT_TABLE_DIR / "position_sizing_summary.csv"
)

ACCOUNT_SIZE_SENSITIVITY_PATH = (
    OUTPUT_TABLE_DIR / "account_size_sensitivity_summary.csv"
)

POSITION_SIZE_TIERS_PATH = (
    OUTPUT_TABLE_DIR / "position_size_tiers_summary.csv"
)

DASHBOARD_REPORT_PATH = OUTPUT_TABLE_DIR / "strategy_dashboard_report.txt"


# =============================================================================
# Settings
# =============================================================================

MATERIALITY_THRESHOLD = 0.0050

PREFERRED_ROLLING_WINDOW_DAYS = 252

CURRENT_RECOMMENDED_ADAPTIVE_RULE = "AdaptiveRegimeDTECost"

DO_NOT_WIRE_MESSAGE = (
    "Keep diagnostics standalone for now. Do not wire regime detection, "
    "historical calibration, rolling calibration, dashboard logic, or "
    "position-sizing diagnostics into app/main.py yet."
)


# =============================================================================
# Formatting helpers
# =============================================================================

def format_percent(value: object, digits: int = 2) -> str:
    """
    Format a decimal value as a percentage.
    """

    value = pd.to_numeric(value, errors="coerce")

    if pd.isna(value):
        return "NA"

    return f"{100.0 * float(value):,.{digits}f}%"


def format_decimal(value: object, digits: int = 4) -> str:
    """
    Format a decimal value.
    """

    value = pd.to_numeric(value, errors="coerce")

    if pd.isna(value):
        return "NA"

    return f"{float(value):,.{digits}f}"


def format_currency(value: object) -> str:
    """
    Format a decimal value as currency.
    """

    value = pd.to_numeric(value, errors="coerce")

    if pd.isna(value):
        return "NA"

    return f"${float(value):,.2f}"


def bool_from_value(value: object) -> bool:
    """
    Convert common CSV boolean representations to bool.
    """

    return str(value).strip().lower() in ["true", "1", "yes", "y"]


def read_csv_if_exists(
    path: Path,
    required_columns: list[str],
    allow_missing: bool = False,
) -> pd.DataFrame:
    """
    Read a CSV file and validate required columns.
    """

    if not path.exists():
        if allow_missing:
            return pd.DataFrame()

        raise FileNotFoundError(
            f"Missing required input file:\n{path}\n\n"
            "Run the required diagnostic scripts first."
        )

    df = pd.read_csv(path)

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"File is missing required columns:\n{path}\n\n"
            f"Missing columns: {missing_columns}"
        )

    return df


# =============================================================================
# Loaders
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
        "Latest_Rolling_Cumulative_Return",
        "Latest_Rolling_Annual_Return",
        "Latest_Rolling_Annual_Volatility",
        "Latest_Detected_Regime",
        "Practical_Rule",
    ]

    df = read_csv_if_exists(
        path=CURRENT_REGIME_PATH,
        required_columns=required_columns,
    )

    df["Rolling_Window_Days"] = pd.to_numeric(
        df["Rolling_Window_Days"],
        errors="coerce",
    )

    df = df[
        df["Rolling_Window_Days"] == PREFERRED_ROLLING_WINDOW_DAYS
    ].copy()

    df = df.sort_values("Ticker").reset_index(drop=True)

    return df


def load_historical_window_winners() -> pd.DataFrame:
    """
    Load historical-window calibration winners.
    """

    required_columns = [
        "Ticker",
        "Window_Label",
        "Detected_Regime",
        "Best_Rule",
        "Adaptive_Outperformance",
        "Best_Outperformance",
        "Adaptive_Minus_Best",
        "Adaptive_Materially_Worse",
    ]

    df = read_csv_if_exists(
        path=HISTORICAL_WINDOW_WINNERS_PATH,
        required_columns=required_columns,
    )

    df = df.sort_values(["Ticker", "Window_Label"]).reset_index(drop=True)

    return df


def load_rolling_strategy_stability() -> pd.DataFrame:
    """
    Load rolling strategy calibration stability table.
    """

    required_columns = [
        "Ticker",
        "Rolling_Windows",
        "Dominant_Best_Rule",
        "Dominant_Best_Rule_Count",
        "Dominant_Best_Rule_Fraction",
        "Unique_Best_Rules",
        "Best_Rule_Count",
        "Dominant_Regime",
        "Dominant_Regime_Fraction",
        "Unique_Regimes",
        "Regime_Count",
        "Adaptive_Materially_Worse_Count",
        "Stable_Best_Rule",
        "Stable_Regime",
    ]

    df = read_csv_if_exists(
        path=ROLLING_STRATEGY_STABILITY_PATH,
        required_columns=required_columns,
    )

    df = df.sort_values("Ticker").reset_index(drop=True)

    return df


def load_position_sizing_summary() -> pd.DataFrame:
    """
    Load fixed-account position-sizing summary.
    """

    required_columns = [
        "Ticker",
        "Latest_Date",
        "Latest_Price",
        "Detected_Regime",
        "Practical_Rule",
        "Rolling_Annual_Return",
        "Rolling_Annual_Volatility",
        "Risk_Label",
        "Ticker_Cap_Fraction",
        "Max_Dollar_Allocation",
        "Dollars_Per_Contract",
        "Max_Contracts",
        "Required_Shares",
        "Actual_Dollar_Allocation",
        "Actual_Account_Fraction",
        "Sizing_Status",
        "Total_Actual_Covered_Call_Allocation",
        "Max_Total_Covered_Call_Allocation",
        "Total_Covered_Call_Allocation_Fraction",
        "Total_Allocation_OK",
    ]

    df = read_csv_if_exists(
        path=POSITION_SIZING_SUMMARY_PATH,
        required_columns=required_columns,
        allow_missing=True,
    )

    if not df.empty:
        df = df.sort_values("Ticker").reset_index(drop=True)

    return df


def load_account_size_sensitivity() -> pd.DataFrame:
    """
    Load account-size sensitivity summary.
    """

    required_columns = [
        "Ticker",
        "Latest_Date",
        "Latest_Price",
        "Detected_Regime",
        "Practical_Rule",
        "Rolling_Annual_Return",
        "Rolling_Annual_Volatility",
        "Risk_Label",
        "Ticker_Allocation_Cap",
        "Target_Contracts",
        "Shares_Required",
        "Dollars_Per_Contract",
        "Position_Value",
        "Required_Account_Equity",
    ]

    df = read_csv_if_exists(
        path=ACCOUNT_SIZE_SENSITIVITY_PATH,
        required_columns=required_columns,
        allow_missing=True,
    )

    if not df.empty:
        df = df.sort_values(
            ["Ticker", "Target_Contracts"]
        ).reset_index(drop=True)

    return df


def load_position_size_tiers() -> pd.DataFrame:
    """
    Load position-size tier summary.
    """

    required_columns = [
        "Tier",
        "Ticker",
        "Latest_Date",
        "Latest_Price",
        "Detected_Regime",
        "Practical_Rule",
        "Rolling_Annual_Return",
        "Rolling_Annual_Volatility",
        "Risk_Label",
        "Ticker_Cap",
        "Total_Covered_Call_Cap",
        "Max_Dollar_Allocation",
        "Dollars_Per_Contract",
        "Minimum_Equity_For_One_Contract",
        "Max_Contracts",
        "Required_Shares",
        "Actual_Dollar_Allocation",
        "Actual_Account_Fraction",
        "Tradable_Status",
        "Tier_Total_Actual_Allocation",
        "Tier_Total_Allocation_Fraction",
        "Tier_Total_Allocation_OK",
    ]

    df = read_csv_if_exists(
        path=POSITION_SIZE_TIERS_PATH,
        required_columns=required_columns,
        allow_missing=True,
    )

    if not df.empty:
        tier_order = ["Conservative", "Balanced", "Aggressive"]

        df["Tier"] = pd.Categorical(
            df["Tier"],
            categories=tier_order,
            ordered=True,
        )

        df = df.sort_values(["Tier", "Ticker"]).reset_index(drop=True)

    return df


# =============================================================================
# Analysis helpers
# =============================================================================

def summarize_current_snapshot(current_df: pd.DataFrame) -> dict:
    """
    Summarize current regime snapshot.
    """

    if current_df.empty:
        return {
            "ticker_count": 0,
            "unique_regimes": [],
            "unique_rules": [],
            "all_same_rule": False,
        }

    unique_regimes = sorted(
        current_df["Latest_Detected_Regime"].astype(str).unique()
    )

    unique_rules = sorted(
        current_df["Practical_Rule"].astype(str).unique()
    )

    return {
        "ticker_count": len(current_df),
        "unique_regimes": unique_regimes,
        "unique_rules": unique_rules,
        "all_same_rule": len(unique_rules) == 1,
    }


def summarize_historical_windows(winners_df: pd.DataFrame) -> dict:
    """
    Summarize historical-window calibration results.
    """

    if winners_df.empty:
        return {
            "case_count": 0,
            "adaptive_worse_count": 0,
            "unstable_tickers": [],
            "unique_best_rules_by_ticker": {},
        }

    df = winners_df.copy()

    df["Adaptive_Materially_Worse"] = (
        df["Adaptive_Materially_Worse"]
        .astype(str)
        .str.lower()
        .isin(["true", "1", "yes"])
    )

    adaptive_worse_count = int(df["Adaptive_Materially_Worse"].sum())

    unique_best_rules_by_ticker = {}
    unstable_tickers = []

    for ticker in sorted(df["Ticker"].astype(str).unique()):
        ticker_df = df[df["Ticker"].astype(str) == ticker].copy()

        unique_rules = sorted(ticker_df["Best_Rule"].astype(str).unique())

        unique_best_rules_by_ticker[ticker] = unique_rules

        if len(unique_rules) > 1:
            unstable_tickers.append(ticker)

    return {
        "case_count": len(df),
        "adaptive_worse_count": adaptive_worse_count,
        "unstable_tickers": unstable_tickers,
        "unique_best_rules_by_ticker": unique_best_rules_by_ticker,
    }


def summarize_rolling_strategy(stability_df: pd.DataFrame) -> dict:
    """
    Summarize rolling strategy calibration stability.
    """

    if stability_df.empty:
        return {
            "ticker_count": 0,
            "total_rolling_windows": 0,
            "adaptive_worse_count": 0,
            "unstable_best_rule_tickers": [],
        }

    df = stability_df.copy()

    df["Adaptive_Materially_Worse_Count"] = pd.to_numeric(
        df["Adaptive_Materially_Worse_Count"],
        errors="coerce",
    ).fillna(0)

    total_adaptive_worse_count = int(
        df["Adaptive_Materially_Worse_Count"].sum()
    )

    df["Stable_Best_Rule_Bool"] = (
        df["Stable_Best_Rule"]
        .astype(str)
        .str.lower()
        .isin(["true", "1", "yes"])
    )

    unstable_best_rule_tickers = sorted(
        df.loc[
            ~df["Stable_Best_Rule_Bool"],
            "Ticker",
        ].astype(str).tolist()
    )

    total_rolling_windows = int(
        pd.to_numeric(
            df["Rolling_Windows"],
            errors="coerce",
        ).fillna(0).sum()
    )

    return {
        "ticker_count": len(df),
        "total_rolling_windows": total_rolling_windows,
        "adaptive_worse_count": total_adaptive_worse_count,
        "unstable_best_rule_tickers": unstable_best_rule_tickers,
    }


def summarize_position_sizing(position_df: pd.DataFrame) -> dict:
    """
    Summarize fixed-account position sizing.
    """

    if position_df.empty:
        return {
            "available": False,
            "tradable_count": 0,
            "total_actual_allocation": float("nan"),
            "total_allocation_fraction": float("nan"),
            "total_allocation_ok": False,
        }

    df = position_df.copy()

    df["Max_Contracts"] = pd.to_numeric(
        df["Max_Contracts"],
        errors="coerce",
    ).fillna(0)

    tradable_count = int((df["Max_Contracts"] >= 1).sum())

    first_row = df.iloc[0]

    return {
        "available": True,
        "tradable_count": tradable_count,
        "total_actual_allocation": first_row[
            "Total_Actual_Covered_Call_Allocation"
        ],
        "total_allocation_fraction": first_row[
            "Total_Covered_Call_Allocation_Fraction"
        ],
        "total_allocation_ok": bool_from_value(
            first_row["Total_Allocation_OK"]
        ),
    }


def summarize_account_size(account_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build one-contract minimum equity summary.
    """

    if account_df.empty:
        return pd.DataFrame()

    df = account_df.copy()

    df["Target_Contracts"] = pd.to_numeric(
        df["Target_Contracts"],
        errors="coerce",
    )

    df["Required_Account_Equity"] = pd.to_numeric(
        df["Required_Account_Equity"],
        errors="coerce",
    )

    one_contract_df = df[df["Target_Contracts"] == 1].copy()

    one_contract_df = one_contract_df.sort_values(
        "Required_Account_Equity"
    ).reset_index(drop=True)

    return one_contract_df


def summarize_position_tiers(tiers_df: pd.DataFrame) -> dict:
    """
    Summarize position-size tiers.
    """

    if tiers_df.empty:
        return {
            "available": False,
            "tier_summaries": pd.DataFrame(),
        }

    df = tiers_df.copy()

    df["Max_Contracts"] = pd.to_numeric(
        df["Max_Contracts"],
        errors="coerce",
    ).fillna(0)

    rows = []

    for tier in df["Tier"].astype(str).dropna().unique():
        tier_df = df[df["Tier"].astype(str) == tier].copy()

        if tier_df.empty:
            continue

        tradable_count = int((tier_df["Max_Contracts"] >= 1).sum())

        first_row = tier_df.iloc[0]

        rows.append(
            {
                "Tier": tier,
                "Tradable_Count": tradable_count,
                "Tier_Total_Actual_Allocation": first_row[
                    "Tier_Total_Actual_Allocation"
                ],
                "Tier_Total_Allocation_Fraction": first_row[
                    "Tier_Total_Allocation_Fraction"
                ],
                "Tier_Total_Allocation_OK": bool_from_value(
                    first_row["Tier_Total_Allocation_OK"]
                ),
            }
        )

    tier_summary_df = pd.DataFrame(rows)

    return {
        "available": True,
        "tier_summaries": tier_summary_df,
    }


# =============================================================================
# Report builder
# =============================================================================

def build_dashboard_report(
    current_df: pd.DataFrame,
    historical_winners_df: pd.DataFrame,
    rolling_stability_df: pd.DataFrame,
    position_sizing_df: pd.DataFrame,
    account_size_df: pd.DataFrame,
    position_tiers_df: pd.DataFrame,
) -> str:
    """
    Build the compact dashboard report.
    """

    current_summary = summarize_current_snapshot(current_df)
    historical_summary = summarize_historical_windows(historical_winners_df)
    rolling_summary = summarize_rolling_strategy(rolling_stability_df)
    position_summary = summarize_position_sizing(position_sizing_df)
    one_contract_df = summarize_account_size(account_size_df)
    tier_summary = summarize_position_tiers(position_tiers_df)

    lines = []

    lines.append("COVERED CALL SIMULATOR - STRATEGY DASHBOARD REPORT")
    lines.append("=" * 100)
    lines.append("")
    lines.append(f"Project folder:                  {PROJECT_ROOT}")
    lines.append(f"Preferred rolling window:         {PREFERRED_ROLLING_WINDOW_DAYS} trading days")
    lines.append(f"Materiality threshold:            {MATERIALITY_THRESHOLD:.4f}")
    lines.append(f"Current adaptive rule candidate:  {CURRENT_RECOMMENDED_ADAPTIVE_RULE}")
    lines.append("")
    lines.append("Input files:")
    lines.append(f"    {CURRENT_REGIME_PATH}")
    lines.append(f"    {HISTORICAL_WINDOW_WINNERS_PATH}")
    lines.append(f"    {ROLLING_STRATEGY_STABILITY_PATH}")
    lines.append(f"    {POSITION_SIZING_SUMMARY_PATH}")
    lines.append(f"    {ACCOUNT_SIZE_SENSITIVITY_PATH}")
    lines.append(f"    {POSITION_SIZE_TIERS_PATH}")
    lines.append("")

    lines.append("-" * 100)
    lines.append("1. Current 252-day regime snapshot")
    lines.append("-" * 100)
    lines.append("")

    if current_df.empty:
        lines.append("No current regime snapshot rows found.")
    else:
        for _, row in current_df.iterrows():
            lines.append(f"Ticker: {row['Ticker']}")
            lines.append(f"    Latest date:                  {row['Latest_Date']}")
            lines.append(f"    Latest price:                 {format_decimal(row['Latest_Price'], 2)}")
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

    lines.append("Current snapshot summary:")
    lines.append(f"    Tickers:                      {current_summary['ticker_count']}")
    lines.append(
        f"    Current regimes:              "
        f"{', '.join(current_summary['unique_regimes'])}"
    )
    lines.append(
        f"    Current practical rules:      "
        f"{', '.join(current_summary['unique_rules'])}"
    )
    lines.append(
        f"    All same practical rule:      "
        f"{current_summary['all_same_rule']}"
    )
    lines.append("")

    lines.append("-" * 100)
    lines.append("2. Strategy validation")
    lines.append("-" * 100)
    lines.append("")

    lines.append("Historical-window validation:")
    lines.append(
        f"    Ticker/window cases:          "
        f"{historical_summary['case_count']}"
    )
    lines.append(
        f"    Adaptive worse cases:         "
        f"{historical_summary['adaptive_worse_count']}"
    )
    lines.append(
        f"    Tickers with unstable best:   "
        f"{len(historical_summary['unstable_tickers'])}"
    )
    lines.append("")

    for ticker, rules in historical_summary[
        "unique_best_rules_by_ticker"
    ].items():
        lines.append(f"    {ticker}: {', '.join(rules)}")

    lines.append("")
    lines.append("Rolling strategy validation:")
    lines.append(
        f"    Tickers tested:               "
        f"{rolling_summary['ticker_count']}"
    )
    lines.append(
        f"    Rolling windows tested:       "
        f"{rolling_summary['total_rolling_windows']}"
    )
    lines.append(
        f"    Adaptive worse cases:         "
        f"{rolling_summary['adaptive_worse_count']}"
    )
    lines.append(
        f"    Tickers with unstable best:   "
        f"{len(rolling_summary['unstable_best_rule_tickers'])}"
    )
    lines.append("")

    for _, row in rolling_stability_df.iterrows():
        lines.append(f"Ticker: {row['Ticker']}")
        lines.append(f"    Dominant best rule:           {row['Dominant_Best_Rule']}")
        lines.append(
            f"    Dominant best-rule fraction:  "
            f"{format_percent(row['Dominant_Best_Rule_Fraction'])}"
        )
        lines.append(f"    Unique best rules:            {row['Unique_Best_Rules']}")
        lines.append(f"    Dominant regime:              {row['Dominant_Regime']}")
        lines.append(
            f"    Adaptive worse count:         "
            f"{row['Adaptive_Materially_Worse_Count']}"
        )
        lines.append("")

    lines.append("-" * 100)
    lines.append("3. Fixed-account position sizing")
    lines.append("-" * 100)
    lines.append("")

    if not position_summary["available"]:
        lines.append(
            "Position-sizing summary is not available. "
            "Run app\\position_sizing_report.py."
        )
        lines.append("")
    else:
        lines.append(
            f"Tradable tickers under fixed-account sizing: "
            f"{position_summary['tradable_count']}"
        )
        lines.append(
            f"Total actual covered-call allocation:        "
            f"{format_currency(position_summary['total_actual_allocation'])}"
        )
        lines.append(
            f"Total covered-call allocation fraction:      "
            f"{format_percent(position_summary['total_allocation_fraction'])}"
        )
        lines.append(
            f"Total allocation OK:                         "
            f"{position_summary['total_allocation_ok']}"
        )
        lines.append("")

        for _, row in position_sizing_df.iterrows():
            lines.append(f"Ticker: {row['Ticker']}")
            lines.append(f"    Risk label:                   {row['Risk_Label']}")
            lines.append(
                f"    Ticker cap:                   "
                f"{format_percent(row['Ticker_Cap_Fraction'])}"
            )
            lines.append(
                f"    Dollars per contract:         "
                f"{format_currency(row['Dollars_Per_Contract'])}"
            )
            lines.append(f"    Max contracts:                {int(row['Max_Contracts'])}")
            lines.append(
                f"    Actual allocation:            "
                f"{format_currency(row['Actual_Dollar_Allocation'])}"
            )
            lines.append(f"    Sizing status:                {row['Sizing_Status']}")
            lines.append("")

    lines.append("-" * 100)
    lines.append("4. Minimum account equity for 1 contract")
    lines.append("-" * 100)
    lines.append("")

    if one_contract_df.empty:
        lines.append(
            "Account-size sensitivity is not available. "
            "Run app\\account_size_sensitivity.py."
        )
        lines.append("")
    else:
        for _, row in one_contract_df.iterrows():
            lines.append(
                f"{row['Ticker']}: "
                f"{format_currency(row['Required_Account_Equity'])} "
                f"at {format_percent(row['Ticker_Allocation_Cap'])} cap"
            )

        lines.append("")

    lines.append("-" * 100)
    lines.append("5. Position-size tier tradability")
    lines.append("-" * 100)
    lines.append("")

    if not tier_summary["available"]:
        lines.append(
            "Position-size tier summary is not available. "
            "Run app\\position_size_tiers.py."
        )
        lines.append("")
    else:
        tier_summary_df = tier_summary["tier_summaries"]

        lines.append("Tier summary:")
        lines.append("")

        for _, row in tier_summary_df.iterrows():
            lines.append(f"Tier: {row['Tier']}")
            lines.append(f"    Tradable tickers:             {row['Tradable_Count']}")
            lines.append(
                f"    Total actual allocation:      "
                f"{format_currency(row['Tier_Total_Actual_Allocation'])}"
            )
            lines.append(
                f"    Total allocation fraction:    "
                f"{format_percent(row['Tier_Total_Allocation_Fraction'])}"
            )
            lines.append(f"    Total allocation OK:          {row['Tier_Total_Allocation_OK']}")
            lines.append("")

        lines.append("Cross-tier tradability map:")
        lines.append("")

        for ticker in sorted(position_tiers_df["Ticker"].astype(str).unique()):
            ticker_df = position_tiers_df[
                position_tiers_df["Ticker"].astype(str) == ticker
            ].copy()

            lines.append(f"Ticker: {ticker}")

            for tier in ["Conservative", "Balanced", "Aggressive"]:
                row_df = ticker_df[
                    ticker_df["Tier"].astype(str) == tier
                ]

                if row_df.empty:
                    continue

                row = row_df.iloc[0]

                lines.append(
                    f"    {tier}: "
                    f"{int(row['Max_Contracts'])} contract(s), "
                    f"{row['Tradable_Status']}"
                )

            lines.append("")

    lines.append("-" * 100)
    lines.append("6. Interpretation")
    lines.append("-" * 100)
    lines.append("")

    lines.append(
        "The strategy layer and the tradability layer answer different questions."
    )
    lines.append("")
    lines.append(
        "The strategy layer identifies which covered-call rule appears most "
        "appropriate under the detected regime."
    )
    lines.append("")
    lines.append(
        "The tradability layer checks whether the account can actually hold "
        "100-share covered-call positions under the selected allocation caps."
    )
    lines.append("")
    lines.append(
        "The current strategy evidence supports AdaptiveRegimeDTECost as the "
        "strongest current candidate rule."
    )
    lines.append("")
    lines.append(
        "The current practical tradability evidence shows that high-priced ETFs "
        "can be impossible to trade as fully covered-call positions in smaller "
        "accounts unless the user accepts aggressive concentration or uses "
        "alternative structures."
    )
    lines.append("")

    lines.append("-" * 100)
    lines.append("7. Development recommendation")
    lines.append("-" * 100)
    lines.append("")

    lines.append(DO_NOT_WIRE_MESSAGE)
    lines.append("")
    lines.append(
        "The research layer and first-pass tradability layer are now mature "
        "enough to support a compact user-facing dashboard or website design."
    )
    lines.append("")
    lines.append("Recommended next development options:")
    lines.append("")
    lines.append("    1. Create a user-facing explanation of the adaptive rule.")
    lines.append("    2. Add taxable-account versus IRA assumptions.")
    lines.append("    3. Add poor man's covered-call or smaller-account alternatives.")
    lines.append("    4. Begin designing the compact website/dashboard interface.")
    lines.append("")

    lines.append("=" * 100)
    lines.append("Overall dashboard conclusion")
    lines.append("=" * 100)
    lines.append("")

    strategy_pass = (
        historical_summary["adaptive_worse_count"] == 0
        and rolling_summary["adaptive_worse_count"] == 0
    )

    if strategy_pass:
        lines.append(
            "STRATEGY STATUS: PASS. AdaptiveRegimeDTECost remains the strongest "
            "current candidate rule. It was not materially worse than the best "
            "fixed rule in the historical-window or rolling-window validation "
            "tests."
        )
    else:
        lines.append(
            "STRATEGY STATUS: REVIEW REQUIRED. At least one validation test "
            "showed material adaptive-rule underperformance."
        )

    lines.append("")

    if position_summary["available"]:
        lines.append(
            "TRADABILITY STATUS: The position-sizing layer is available. Use the "
            "fixed-account sizing, minimum account-size, and tier tradability "
            "sections to decide whether a ticker is practical for the account."
        )
    else:
        lines.append(
            "TRADABILITY STATUS: Incomplete. Run the position-sizing diagnostics."
        )

    lines.append("")
    lines.append(
        "Use this report as the compact strategy-and-tradability dashboard."
    )

    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)

    current_df = load_current_regime_snapshot()
    historical_winners_df = load_historical_window_winners()
    rolling_stability_df = load_rolling_strategy_stability()
    position_sizing_df = load_position_sizing_summary()
    account_size_df = load_account_size_sensitivity()
    position_tiers_df = load_position_size_tiers()

    report_text = build_dashboard_report(
        current_df=current_df,
        historical_winners_df=historical_winners_df,
        rolling_stability_df=rolling_stability_df,
        position_sizing_df=position_sizing_df,
        account_size_df=account_size_df,
        position_tiers_df=position_tiers_df,
    )

    DASHBOARD_REPORT_PATH.write_text(report_text, encoding="utf-8")

    print("")
    print("=" * 100)
    print("Strategy dashboard report complete.")
    print("=" * 100)
    print("")
    print(f"Saved report:")
    print(f"  {DASHBOARD_REPORT_PATH}")
    print("")
    print("Done.")
    print("")


if __name__ == "__main__":
    main()