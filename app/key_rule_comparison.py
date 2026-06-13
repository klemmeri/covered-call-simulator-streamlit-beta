"""
key_rule_comparison.py

Focused comparison report for the Covered Call Simulator.

This script compares the five key management rules:

    1. Close50
    2. Wait10d
    3. AdaptiveClose50Wait10
    4. AdaptiveClose50Wait10CostAware
    5. AdaptiveRegimeDTECost

It reads the existing output file:

    outputs/tables/comparison/management_rule_comparison.csv

and creates:

    outputs/tables/comparison/key_rule_comparison.csv
    outputs/tables/comparison/key_rule_comparison_report.txt
    outputs/charts/comparison/key_rule_mean_outperformance.png
    outputs/charts/comparison/key_rule_net_option_effect.png
    outputs/charts/comparison/key_rule_transaction_cost.png

This script does not run simulations.
Run app/main.py first.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# =============================================================================
# Paths
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MANAGEMENT_RULE_COMPARISON_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "comparison"
    / "management_rule_comparison.csv"
)

OUTPUT_TABLE_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "comparison"
)

OUTPUT_CHART_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "charts"
    / "comparison"
)

KEY_RULE_TABLE_PATH = OUTPUT_TABLE_DIR / "key_rule_comparison.csv"
KEY_RULE_REPORT_PATH = OUTPUT_TABLE_DIR / "key_rule_comparison_report.txt"

OUTPERFORMANCE_CHART_PATH = OUTPUT_CHART_DIR / "key_rule_mean_outperformance.png"
NET_EFFECT_CHART_PATH = OUTPUT_CHART_DIR / "key_rule_net_option_effect.png"
TRANSACTION_COST_CHART_PATH = OUTPUT_CHART_DIR / "key_rule_transaction_cost.png"


# =============================================================================
# Rule and metric settings
# =============================================================================

REGIME_ORDER = [
    "baseline",
    "sideways_market",
    "bullish_market",
    "bearish_market",
    "high_volatility",
    "low_volatility",
]

KEY_RULE_LABELS = [
    "Close50",
    "Wait10d",
    "AdaptiveClose50Wait10",
    "AdaptiveClose50Wait10CostAware",
    "AdaptiveRegimeDTECost",
]

METRICS = [
    "Mean_Outperformance",
    "Mean_Net_Option_Effect",
    "Mean_Total_Transaction_Cost",
    "Mean_Total_Commission_Cost",
    "Mean_Total_Slippage_Cost",
    "Mean_Option_Cycles",
    "Mean_Assignments",
]


# =============================================================================
# Helpers
# =============================================================================

def load_management_rule_comparison() -> pd.DataFrame:
    """
    Load management_rule_comparison.csv.
    """

    if not MANAGEMENT_RULE_COMPARISON_PATH.exists():
        raise FileNotFoundError(
            "Could not find management_rule_comparison.csv at:\n"
            f"{MANAGEMENT_RULE_COMPARISON_PATH}\n\n"
            "Run app/main.py first."
        )

    return pd.read_csv(MANAGEMENT_RULE_COMPARISON_PATH)


def normalize_text(value: object) -> str:
    """
    Normalize text for robust matching.
    """

    text = (
        str(value)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )

    while "__" in text:
        text = text.replace("__", "_")

    return text.strip("_")


def get_value(
    df: pd.DataFrame,
    regime: str,
    rule_label: str,
    metric: str,
) -> float | None:
    """
    Pull one value from the wide management_rule_comparison.csv file.

    Example columns:

        Close50_Mean_Outperformance
        Wait10d_Mean_Net_Option_Effect
        AdaptiveClose50Wait10CostAware_Mean_Total_Transaction_Cost
        AdaptiveRegimeDTECost_Mean_Outperformance
    """

    if "Regime" not in df.columns:
        return None

    regime_mask = df["Regime"].apply(normalize_text) == normalize_text(regime)
    regime_df = df[regime_mask]

    if regime_df.empty:
        return None

    column_name = f"{rule_label}_{metric}"

    if column_name not in df.columns:
        return None

    value = pd.to_numeric(regime_df.iloc[0][column_name], errors="coerce")

    if pd.isna(value):
        return None

    return float(value)


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


# =============================================================================
# Build focused table
# =============================================================================

def build_key_rule_table(wide_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a long-format table with one row per regime/rule pair.
    """

    rows = []

    for regime in REGIME_ORDER:
        for rule_label in KEY_RULE_LABELS:
            row = {
                "Regime": regime,
                "Rule_Label": rule_label,
            }

            for metric in METRICS:
                row[metric] = get_value(
                    df=wide_df,
                    regime=regime,
                    rule_label=rule_label,
                    metric=metric,
                )

            rows.append(row)

    result_df = pd.DataFrame(rows)

    result_df["Regime"] = pd.Categorical(
        result_df["Regime"],
        categories=REGIME_ORDER,
        ordered=True,
    )

    result_df["Rule_Label"] = pd.Categorical(
        result_df["Rule_Label"],
        categories=KEY_RULE_LABELS,
        ordered=True,
    )

    result_df = result_df.sort_values(
        ["Regime", "Rule_Label"]
    ).reset_index(drop=True)

    return result_df


# =============================================================================
# Report
# =============================================================================

def find_best_rule(
    table_df: pd.DataFrame,
    regime: str,
    metric: str,
    higher_is_better: bool = True,
) -> pd.Series | None:
    """
    Find the best rule for one regime and metric.
    """

    regime_df = table_df[table_df["Regime"].astype(str) == regime].copy()

    regime_df[metric] = pd.to_numeric(regime_df[metric], errors="coerce")
    regime_df = regime_df.dropna(subset=[metric])

    if regime_df.empty:
        return None

    if higher_is_better:
        idx = regime_df[metric].idxmax()
    else:
        idx = regime_df[metric].idxmin()

    return regime_df.loc[idx]


def build_report(table_df: pd.DataFrame) -> str:
    """
    Build a plain-text focused comparison report.
    """

    lines = []

    lines.append("Covered Call Simulator — Key Rule Comparison")
    lines.append("=" * 72)
    lines.append("")
    lines.append("Rules compared:")
    for rule_label in KEY_RULE_LABELS:
        lines.append(f"    {rule_label}")
    lines.append("")
    lines.append(f"Input file:  {MANAGEMENT_RULE_COMPARISON_PATH}")
    lines.append(f"Output file: {KEY_RULE_TABLE_PATH}")
    lines.append("")

    for regime in REGIME_ORDER:
        lines.append("-" * 72)
        lines.append(f"Regime: {regime}")
        lines.append("-" * 72)

        regime_df = table_df[table_df["Regime"].astype(str) == regime].copy()

        if regime_df.empty:
            lines.append("No data available.")
            lines.append("")
            continue

        best_outperf = find_best_rule(
            table_df=table_df,
            regime=regime,
            metric="Mean_Outperformance",
            higher_is_better=True,
        )

        lowest_cost = find_best_rule(
            table_df=table_df,
            regime=regime,
            metric="Mean_Total_Transaction_Cost",
            higher_is_better=False,
        )

        if best_outperf is not None:
            lines.append(
                "Best mean outperformance: "
                f"{best_outperf['Rule_Label']} "
                f"({format_decimal(best_outperf['Mean_Outperformance'])})"
            )

        if lowest_cost is not None:
            lines.append(
                "Lowest transaction cost:  "
                f"{lowest_cost['Rule_Label']} "
                f"({format_currency(lowest_cost['Mean_Total_Transaction_Cost'])})"
            )

        lines.append("")
        lines.append("Rule details:")

        for _, row in regime_df.iterrows():
            lines.append(
                f"    {row['Rule_Label']:<34} "
                f"Outperf: {format_decimal(row['Mean_Outperformance']):>10} | "
                f"Net option: {format_currency(row['Mean_Net_Option_Effect']):>12} | "
                f"Cost: {format_currency(row['Mean_Total_Transaction_Cost']):>10} | "
                f"Cycles: {format_decimal(row['Mean_Option_Cycles'], 2):>8}"
            )

        lines.append("")

    lines.append("=" * 72)
    lines.append("Interpretation")
    lines.append("=" * 72)
    lines.append("")
    lines.append(
        "The adaptive rules are designed to reproduce the preferred fixed rule "
        "within each regime under the assumptions they are built for."
    )
    lines.append("")
    lines.append(
        "AdaptiveClose50Wait10 is the original regime-aware rule. "
        "AdaptiveClose50Wait10CostAware adds the sideways-market transaction-cost "
        "override. AdaptiveRegimeDTECost adds DTE as another decision variable."
    )
    lines.append("")
    lines.append(
        "Under the current default DTE and low transaction costs, all three "
        "adaptive rules may behave the same in several regimes. The DTE-aware "
        "rule becomes more useful when testing shorter or longer DTE values."
    )
    lines.append("")
    lines.append(
        "The sideways-market cost threshold remains: commission >= $1.25 per "
        "contract or slippage >= $0.025/share."
    )
    lines.append("")
    lines.append(
        "This focused report is intended to make the practical comparison easier "
        "to explain than the full 66-experiment table."
    )

    return "\n".join(lines)


# =============================================================================
# Charts
# =============================================================================

def save_grouped_bar_chart(
    table_df: pd.DataFrame,
    metric: str,
    title: str,
    ylabel: str,
    output_path: Path,
) -> None:
    """
    Save a grouped bar chart by regime and rule.
    """

    plot_df = table_df.copy()
    plot_df[metric] = pd.to_numeric(plot_df[metric], errors="coerce")
    plot_df = plot_df.dropna(subset=[metric])

    if plot_df.empty:
        return

    pivot = plot_df.pivot(
        index="Regime",
        columns="Rule_Label",
        values=metric,
    )

    pivot = pivot.reindex(REGIME_ORDER)
    pivot = pivot[KEY_RULE_LABELS]

    ax = pivot.plot(kind="bar", figsize=(15, 7))
    ax.axhline(0, linewidth=1)
    ax.set_title(title)
    ax.set_xlabel("Regime")
    ax.set_ylabel(ylabel)

    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()


def save_charts(table_df: pd.DataFrame) -> None:
    """
    Save all focused comparison charts.
    """

    save_grouped_bar_chart(
        table_df=table_df,
        metric="Mean_Outperformance",
        title="Key Rules — Mean Outperformance by Regime",
        ylabel="Mean Outperformance",
        output_path=OUTPERFORMANCE_CHART_PATH,
    )

    save_grouped_bar_chart(
        table_df=table_df,
        metric="Mean_Net_Option_Effect",
        title="Key Rules — Mean Net Option Effect by Regime",
        ylabel="Mean Net Option Effect",
        output_path=NET_EFFECT_CHART_PATH,
    )

    save_grouped_bar_chart(
        table_df=table_df,
        metric="Mean_Total_Transaction_Cost",
        title="Key Rules — Mean Transaction Cost by Regime",
        ylabel="Mean Transaction Cost",
        output_path=TRANSACTION_COST_CHART_PATH,
    )


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_CHART_DIR.mkdir(parents=True, exist_ok=True)

    wide_df = load_management_rule_comparison()

    key_rule_df = build_key_rule_table(wide_df)

    key_rule_df.to_csv(KEY_RULE_TABLE_PATH, index=False)

    report_text = build_report(key_rule_df)
    KEY_RULE_REPORT_PATH.write_text(report_text, encoding="utf-8")

    save_charts(key_rule_df)

    print("")
    print("Covered Call Simulator — Key Rule Comparison")
    print("=" * 72)
    print("")
    print("Saved files:")
    print(f"  {KEY_RULE_TABLE_PATH}")
    print(f"  {KEY_RULE_REPORT_PATH}")
    print(f"  {OUTPERFORMANCE_CHART_PATH}")
    print(f"  {NET_EFFECT_CHART_PATH}")
    print(f"  {TRANSACTION_COST_CHART_PATH}")
    print("")
    print("Done.")
    print("")


if __name__ == "__main__":
    main()