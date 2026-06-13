"""
delta_decision_map.py

Creates a clean decision-map report from the delta sensitivity test.

This script reads:

    outputs/tables/comparison/delta_sensitivity_winners.csv

and creates:

    outputs/tables/comparison/delta_decision_map.csv
    outputs/tables/comparison/delta_decision_map_detailed.csv
    outputs/tables/comparison/delta_decision_map_report.txt

This script does not run simulations.
Run app/delta_sensitivity.py first.
"""

from pathlib import Path

import pandas as pd


# =============================================================================
# Paths
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_TABLE_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "comparison"
)

WINNERS_PATH = OUTPUT_TABLE_DIR / "delta_sensitivity_winners.csv"

DECISION_MAP_PATH = OUTPUT_TABLE_DIR / "delta_decision_map.csv"
DETAILED_MAP_PATH = OUTPUT_TABLE_DIR / "delta_decision_map_detailed.csv"
REPORT_PATH = OUTPUT_TABLE_DIR / "delta_decision_map_report.txt"


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

DELTA_VALUES = [
    0.20,
    0.25,
    0.30,
    0.35,
    0.40,
]

MATERIALITY_THRESHOLD = 0.0050


# =============================================================================
# Helpers
# =============================================================================

def load_winners() -> pd.DataFrame:
    """
    Load delta_sensitivity_winners.csv.
    """

    if not WINNERS_PATH.exists():
        raise FileNotFoundError(
            "Could not find delta_sensitivity_winners.csv at:\n"
            f"{WINNERS_PATH}\n\n"
            "Run app/delta_sensitivity.py first."
        )

    df = pd.read_csv(WINNERS_PATH)

    required_columns = [
        "Regime",
        "Target_Delta",
        "Best_Rule_Label",
        "Best_Mean_Outperformance",
        "Second_Best_Rule_Label",
        "Second_Best_Mean_Outperformance",
        "Outperformance_Edge",
        "Best_Mean_Net_Option_Effect",
        "Best_Mean_Total_Transaction_Cost",
    ]

    missing_columns = [
        column for column in required_columns if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "delta_sensitivity_winners.csv is missing required columns:\n"
            f"{missing_columns}"
        )

    df["Target_Delta"] = pd.to_numeric(
        df["Target_Delta"],
        errors="coerce",
    )

    df["Outperformance_Edge"] = pd.to_numeric(
        df["Outperformance_Edge"],
        errors="coerce",
    )

    return df


def format_decimal(value: object, digits: int = 4) -> str:
    """
    Format decimal values.
    """

    value = pd.to_numeric(value, errors="coerce")

    if pd.isna(value):
        return "NA"

    return f"{float(value):,.{digits}f}"


def format_currency(value: object) -> str:
    """
    Format dollar values.
    """

    value = pd.to_numeric(value, errors="coerce")

    if pd.isna(value):
        return "NA"

    return f"${float(value):,.2f}"


def simplify_rule_label(rule_label: object) -> str:
    """
    Convert detailed rule labels into practical labels.
    """

    text = str(rule_label)

    if text in [
        "AdaptiveClose50Wait10",
        "AdaptiveClose50Wait10CostAware",
        "AdaptiveRegimeDTECost",
        "Wait10d",
    ]:
        return "Wait10d"

    if text == "Close50":
        return "Close50"

    if text == "HoldToExpiration":
        return "Hold"

    return text


# =============================================================================
# Decision maps
# =============================================================================

def build_decision_map(winners_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a regime x delta table using the raw best rule label.
    """

    matrix = winners_df.pivot(
        index="Regime",
        columns="Target_Delta",
        values="Best_Rule_Label",
    )

    matrix = matrix.reindex(REGIME_ORDER)
    matrix = matrix.reindex(columns=DELTA_VALUES)

    return matrix


def build_practical_decision_map(winners_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a simplified regime x delta table using practical labels.
    """

    df = winners_df.copy()
    df["Practical_Rule"] = df["Best_Rule_Label"].apply(
        simplify_rule_label
    )

    matrix = df.pivot(
        index="Regime",
        columns="Target_Delta",
        values="Practical_Rule",
    )

    matrix = matrix.reindex(REGIME_ORDER)
    matrix = matrix.reindex(columns=DELTA_VALUES)

    return matrix


def build_detailed_map(winners_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a detailed table with materiality flags.
    """

    df = winners_df.copy()

    df["Practical_Rule"] = df["Best_Rule_Label"].apply(
        simplify_rule_label
    )

    df["Material_Edge"] = (
        df["Outperformance_Edge"].abs() >= MATERIALITY_THRESHOLD
    )

    df["Regime"] = pd.Categorical(
        df["Regime"],
        categories=REGIME_ORDER,
        ordered=True,
    )

    df = df.sort_values(
        ["Regime", "Target_Delta"]
    ).reset_index(drop=True)

    return df


def summarize_regime_stability(detailed_df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize whether each regime is stable across deltas.
    """

    rows = []

    for regime in REGIME_ORDER:
        regime_df = detailed_df[
            detailed_df["Regime"].astype(str) == regime
        ].copy()

        if regime_df.empty:
            continue

        practical_rules = sorted(
            regime_df["Practical_Rule"].dropna().astype(str).unique()
        )

        material_edges = regime_df["Material_Edge"].fillna(False).any()

        if len(practical_rules) == 1:
            stability = "Stable"
        else:
            stability = "Mixed"

        if not material_edges:
            conclusion = (
                "No material delta-based rule change detected."
            )
        elif stability == "Stable":
            conclusion = (
                "Rule is stable across deltas with at least one material edge."
            )
        else:
            conclusion = (
                "Potential delta sensitivity detected; review before changing adaptive logic."
            )

        rows.append(
            {
                "Regime": regime,
                "Practical_Rules_Observed": ", ".join(practical_rules),
                "Delta_Stability": stability,
                "Any_Material_Edge": material_edges,
                "Conclusion": conclusion,
            }
        )

    return pd.DataFrame(rows)


# =============================================================================
# Report
# =============================================================================

def build_report(
    raw_map: pd.DataFrame,
    practical_map: pd.DataFrame,
    detailed_df: pd.DataFrame,
    stability_df: pd.DataFrame,
) -> str:
    """
    Build a clean plain-text report.
    """

    lines = []

    lines.append("COVERED CALL SIMULATOR - DELTA DECISION MAP")
    lines.append("=" * 100)
    lines.append("")
    lines.append(f"Input file:                 {WINNERS_PATH}")
    lines.append(f"Raw decision map file:       {DECISION_MAP_PATH}")
    lines.append(f"Detailed decision map file:  {DETAILED_MAP_PATH}")
    lines.append(f"Materiality threshold:       {MATERIALITY_THRESHOLD:.4f}")
    lines.append("")

    lines.append("-" * 100)
    lines.append("Raw decision map: best label by regime and target delta")
    lines.append("-" * 100)
    lines.append("")
    lines.append(raw_map.to_string())
    lines.append("")

    lines.append("-" * 100)
    lines.append("Practical decision map")
    lines.append("-" * 100)
    lines.append("")
    lines.append(practical_map.to_string())
    lines.append("")

    lines.append("-" * 100)
    lines.append("Regime stability summary")
    lines.append("-" * 100)
    lines.append("")

    for _, row in stability_df.iterrows():
        lines.append(f"Regime: {row['Regime']}")
        lines.append(
            f"    Practical rules observed: {row['Practical_Rules_Observed']}"
        )
        lines.append(f"    Delta stability:          {row['Delta_Stability']}")
        lines.append(f"    Any material edge:        {row['Any_Material_Edge']}")
        lines.append(f"    Conclusion:               {row['Conclusion']}")
        lines.append("")

    lines.append("-" * 100)
    lines.append("Detailed winners")
    lines.append("-" * 100)
    lines.append("")

    for _, row in detailed_df.iterrows():
        lines.append(
            f"{str(row['Regime']):<18} "
            f"Delta={float(row['Target_Delta']):.2f} | "
            f"Best={str(row['Best_Rule_Label']):<32} | "
            f"Practical={str(row['Practical_Rule']):<8} | "
            f"Outperf={format_decimal(row['Best_Mean_Outperformance'])} | "
            f"Second={str(row['Second_Best_Rule_Label']):<32} | "
            f"Edge={format_decimal(row['Outperformance_Edge'])} | "
            f"Material={row['Material_Edge']} | "
            f"Net option={format_currency(row['Best_Mean_Net_Option_Effect'])} | "
            f"Cost={format_currency(row['Best_Mean_Total_Transaction_Cost'])}"
        )

    lines.append("")
    lines.append("=" * 100)
    lines.append("Overall conclusion")
    lines.append("=" * 100)
    lines.append("")
    lines.append(
        "The delta sensitivity test does not currently justify adding target_delta "
        "to the adaptive rule logic."
    )
    lines.append("")
    lines.append(
        "Across the tested deltas, the practical rule map remains essentially "
        "unchanged: Wait10d/adaptive behavior in baseline, bullish, high-volatility, "
        "and most low-volatility cases; Close50 in sideways and bearish markets."
    )
    lines.append("")
    lines.append(
        "The only practical exception in the screening run was low_volatility at "
        "delta 0.20, where HoldToExpiration appeared as the best label. Its edge "
        "was very small and should not be treated as a robust rule change without "
        "a larger 1000-path confirmation run."
    )
    lines.append("")
    lines.append(
        "Recommendation: keep the current DTE-aware adaptive rule unchanged. "
        "Do not add delta as a decision variable yet."
    )

    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)

    winners_df = load_winners()

    raw_map = build_decision_map(winners_df)
    practical_map = build_practical_decision_map(winners_df)
    detailed_df = build_detailed_map(winners_df)
    stability_df = summarize_regime_stability(detailed_df)

    raw_map.to_csv(DECISION_MAP_PATH)
    detailed_df.to_csv(DETAILED_MAP_PATH, index=False)

    report_text = build_report(
        raw_map=raw_map,
        practical_map=practical_map,
        detailed_df=detailed_df,
        stability_df=stability_df,
    )

    REPORT_PATH.write_text(report_text, encoding="utf-8")

    print("")
    print("=" * 100)
    print("Delta decision map complete.")
    print("=" * 100)
    print("")
    print("Saved files:")
    print(f"  {DECISION_MAP_PATH}")
    print(f"  {DETAILED_MAP_PATH}")
    print(f"  {REPORT_PATH}")
    print("")
    print("Done.")
    print("")


if __name__ == "__main__":
    main()