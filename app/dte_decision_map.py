"""
dte_decision_map.py

Builds a clean DTE decision map from the DTE sensitivity results.

This script reads:

    outputs/tables/comparison/dte_sensitivity_winners.csv

and creates:

    outputs/tables/comparison/dte_decision_map.csv
    outputs/tables/comparison/dte_decision_map_report.txt

Purpose
-------
The DTE sensitivity test showed that the preferred covered-call management
rule can change with DTE. This script converts the winner table into a simple
decision map:

    Regime x DTE -> Winning Rule

This script does not run simulations.
Run app/dte_sensitivity.py first.
"""

from pathlib import Path

import pandas as pd


# =============================================================================
# Paths
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "comparison"
    / "dte_sensitivity_winners.csv"
)

OUTPUT_TABLE_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "comparison"
)

DECISION_MAP_PATH = OUTPUT_TABLE_DIR / "dte_decision_map.csv"
REPORT_PATH = OUTPUT_TABLE_DIR / "dte_decision_map_report.txt"


# =============================================================================
# Settings
# =============================================================================

REGIME_ORDER = [
    "baseline",
    "sideways_market",
    "bullish_market",
    "bearish_market",
    "high_volatility",
    "low_volatility",
]

DTE_ORDER = [
    7,
    14,
    21,
    30,
    45,
]

RULE_SHORT_LABELS = {
    "HoldToExpiration": "Hold",
    "Close50": "Close50",
    "Wait10d": "Wait10d",
    "AdaptiveClose50Wait10": "Adaptive",
    "AdaptiveClose50Wait10CostAware": "AdaptiveCostAware",
}


# =============================================================================
# Helpers
# =============================================================================

def load_winners() -> pd.DataFrame:
    """
    Load dte_sensitivity_winners.csv.
    """

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            "Could not find dte_sensitivity_winners.csv at:\n"
            f"{INPUT_PATH}\n\n"
            "Run app/dte_sensitivity.py first."
        )

    df = pd.read_csv(INPUT_PATH)

    required_columns = [
        "DTE",
        "Regime",
        "Winning_Rule",
        "Winning_Mean_Outperformance",
        "Winning_Mean_Net_Option_Effect",
        "Winning_Mean_Total_Transaction_Cost",
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise KeyError(
            "dte_sensitivity_winners.csv is missing required columns:\n"
            f"{missing}\n\n"
            f"Available columns are:\n{list(df.columns)}"
        )

    df["DTE"] = pd.to_numeric(df["DTE"], errors="coerce").astype("Int64")
    df["Winning_Mean_Outperformance"] = pd.to_numeric(
        df["Winning_Mean_Outperformance"],
        errors="coerce",
    )
    df["Winning_Mean_Net_Option_Effect"] = pd.to_numeric(
        df["Winning_Mean_Net_Option_Effect"],
        errors="coerce",
    )
    df["Winning_Mean_Total_Transaction_Cost"] = pd.to_numeric(
        df["Winning_Mean_Total_Transaction_Cost"],
        errors="coerce",
    )

    return df


def short_rule_label(rule: str) -> str:
    """
    Return a shorter display label for a rule.
    """

    rule = str(rule)

    return RULE_SHORT_LABELS.get(rule, rule)


def format_decimal(value, digits: int = 4) -> str:
    """
    Format numeric value as decimal text.
    """

    numeric = pd.to_numeric(value, errors="coerce")

    if pd.isna(numeric):
        return "NA"

    return f"{float(numeric):,.{digits}f}"


def format_currency(value) -> str:
    """
    Format numeric value as currency text.
    """

    numeric = pd.to_numeric(value, errors="coerce")

    if pd.isna(numeric):
        return "NA"

    return f"${float(numeric):,.2f}"


# =============================================================================
# Decision map
# =============================================================================

def build_decision_map(winners_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build wide decision map:

        Regime | 7_DTE | 14_DTE | 21_DTE | 30_DTE | 45_DTE

    Each cell contains the short winning rule label.
    """

    rows = []

    for regime in REGIME_ORDER:
        row = {
            "Regime": regime,
        }

        for dte in DTE_ORDER:
            match = winners_df[
                (winners_df["Regime"] == regime)
                & (winners_df["DTE"] == dte)
            ]

            column_name = f"{dte}_DTE"

            if match.empty:
                row[column_name] = "NA"
            else:
                winner = match.iloc[0]["Winning_Rule"]
                row[column_name] = short_rule_label(winner)

        rows.append(row)

    return pd.DataFrame(rows)


def build_detailed_decision_map(winners_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a detailed long-format decision table with metrics.
    """

    rows = []

    for regime in REGIME_ORDER:
        for dte in DTE_ORDER:
            match = winners_df[
                (winners_df["Regime"] == regime)
                & (winners_df["DTE"] == dte)
            ]

            if match.empty:
                rows.append(
                    {
                        "Regime": regime,
                        "DTE": dte,
                        "Winning_Rule": "NA",
                        "Winning_Label": "NA",
                        "Winning_Mean_Outperformance": None,
                        "Winning_Mean_Net_Option_Effect": None,
                        "Winning_Mean_Total_Transaction_Cost": None,
                    }
                )
                continue

            row = match.iloc[0]

            rows.append(
                {
                    "Regime": regime,
                    "DTE": dte,
                    "Winning_Rule": row["Winning_Rule"],
                    "Winning_Label": short_rule_label(row["Winning_Rule"]),
                    "Winning_Mean_Outperformance": row[
                        "Winning_Mean_Outperformance"
                    ],
                    "Winning_Mean_Net_Option_Effect": row[
                        "Winning_Mean_Net_Option_Effect"
                    ],
                    "Winning_Mean_Total_Transaction_Cost": row[
                        "Winning_Mean_Total_Transaction_Cost"
                    ],
                }
            )

    return pd.DataFrame(rows)


# =============================================================================
# Report
# =============================================================================

def build_report(
    decision_map_df: pd.DataFrame,
    detailed_df: pd.DataFrame,
) -> str:
    """
    Build a plain-text DTE decision map report.
    """

    lines = []

    lines.append("Covered Call Simulator — DTE Decision Map")
    lines.append("=" * 78)
    lines.append("")
    lines.append(f"Input file:  {INPUT_PATH}")
    lines.append(f"Output file: {DECISION_MAP_PATH}")
    lines.append("")
    lines.append("Decision map:")
    lines.append("")

    header = (
        f"{'Regime':<18} "
        f"{'7DTE':<10} "
        f"{'14DTE':<10} "
        f"{'21DTE':<10} "
        f"{'30DTE':<10} "
        f"{'45DTE':<10}"
    )

    lines.append(header)
    lines.append("-" * len(header))

    for _, row in decision_map_df.iterrows():
        lines.append(
            f"{row['Regime']:<18} "
            f"{row['7_DTE']:<10} "
            f"{row['14_DTE']:<10} "
            f"{row['21_DTE']:<10} "
            f"{row['30_DTE']:<10} "
            f"{row['45_DTE']:<10}"
        )

    lines.append("")
    lines.append("=" * 78)
    lines.append("Regime-by-Regime Interpretation")
    lines.append("=" * 78)
    lines.append("")

    for regime in REGIME_ORDER:
        regime_df = detailed_df[detailed_df["Regime"] == regime].copy()

        if regime_df.empty:
            lines.append(f"{regime}: no data")
            lines.append("")
            continue

        winner_sequence = [
            f"{int(row['DTE'])}DTE={row['Winning_Label']}"
            for _, row in regime_df.iterrows()
        ]

        unique_winners = list(regime_df["Winning_Label"].dropna().unique())

        lines.append(f"{regime}:")
        lines.append(f"    Winner sequence: {', '.join(winner_sequence)}")
        lines.append(f"    Unique winners:  {', '.join(unique_winners)}")

        if len(unique_winners) == 1:
            lines.append("    Interpretation: Stable across tested DTE values.")
        else:
            lines.append("    Interpretation: DTE-sensitive regime.")

        lines.append("")

    lines.append("=" * 78)
    lines.append("Detailed Winning Metrics")
    lines.append("=" * 78)
    lines.append("")

    for regime in REGIME_ORDER:
        lines.append("-" * 78)
        lines.append(f"Regime: {regime}")
        lines.append("-" * 78)

        regime_df = detailed_df[detailed_df["Regime"] == regime].copy()

        for _, row in regime_df.iterrows():
            lines.append(
                f"{int(row['DTE']):>2} DTE | "
                f"{row['Winning_Label']:<10} | "
                f"outperf: {format_decimal(row['Winning_Mean_Outperformance']):>10} | "
                f"net option: {format_currency(row['Winning_Mean_Net_Option_Effect']):>12} | "
                f"cost: {format_currency(row['Winning_Mean_Total_Transaction_Cost']):>10}"
            )

        lines.append("")

    lines.append("=" * 78)
    lines.append("Practical Rule Suggested by DTE Decision Map")
    lines.append("=" * 78)
    lines.append("")
    lines.append("A first DTE-aware rule would be:")
    lines.append("")
    lines.append("    If bearish_market:")
    lines.append("        Use Close50 at all tested DTE values.")
    lines.append("")
    lines.append("    If sideways_market:")
    lines.append("        If DTE <= 14:")
    lines.append("            Hold to expiration.")
    lines.append("        If DTE >= 21:")
    lines.append("            Use Close50, unless transaction costs are high.")
    lines.append("")
    lines.append("    If bullish_market or high_volatility:")
    lines.append("        If DTE <= 30:")
    lines.append("            Use Wait10d.")
    lines.append("        If DTE >= 45:")
    lines.append("            Hold to expiration.")
    lines.append("")
    lines.append("    If baseline or low_volatility:")
    lines.append("        Use Wait10d at 7, 21, and 30 DTE.")
    lines.append("        Use HoldToExpiration at 14 and 45 DTE.")
    lines.append("")
    lines.append("Caution:")
    lines.append(
        "    The baseline and low-volatility 14-DTE HoldToExpiration result "
        "is less smooth than the broader pattern. It may be real, but it "
        "should be treated cautiously before hard-coding a rule."
    )
    lines.append("")
    lines.append("Recommended next step:")
    lines.append(
        "    Use this decision map as a report first. Do not modify portfolio.py "
        "until the DTE-aware rule design is clear."
    )

    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)

    winners_df = load_winners()

    decision_map_df = build_decision_map(winners_df)
    detailed_df = build_detailed_decision_map(winners_df)

    # Save one compact map and one detailed map.
    decision_map_df.to_csv(DECISION_MAP_PATH, index=False)

    detailed_path = OUTPUT_TABLE_DIR / "dte_decision_map_detailed.csv"
    detailed_df.to_csv(detailed_path, index=False)

    report_text = build_report(
        decision_map_df=decision_map_df,
        detailed_df=detailed_df,
    )

    REPORT_PATH.write_text(report_text, encoding="utf-8")

    print("")
    print("Covered Call Simulator — DTE Decision Map")
    print("=" * 78)
    print("")
    print("Saved files:")
    print(f"  {DECISION_MAP_PATH}")
    print(f"  {detailed_path}")
    print(f"  {REPORT_PATH}")
    print("")
    print("Decision map:")
    print("")
    print(decision_map_df.to_string(index=False))
    print("")


if __name__ == "__main__":
    main()