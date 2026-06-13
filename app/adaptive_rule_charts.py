"""
adaptive_rule_charts.py

Creates focused charts comparing the three adaptive covered-call rules:

    1. AdaptiveClose50Wait10
    2. AdaptiveClose50Wait10CostAware
    3. AdaptiveRegimeDTECost

This script reads:

    outputs/tables/comparison/management_rule_comparison.csv

and creates:

    outputs/charts/comparison/adaptive_rules_mean_outperformance.png
    outputs/charts/comparison/adaptive_rules_net_option_effect.png
    outputs/charts/comparison/adaptive_rules_transaction_cost.png
    outputs/tables/comparison/adaptive_rule_chart_data.csv
    outputs/tables/comparison/adaptive_rule_chart_report.txt

This script does not run simulations.
Run app/main.py first if the comparison CSV is missing or stale.
"""

from pathlib import Path

import matplotlib.pyplot as plt
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

CHART_DATA_PATH = OUTPUT_TABLE_DIR / "adaptive_rule_chart_data.csv"
REPORT_PATH = OUTPUT_TABLE_DIR / "adaptive_rule_chart_report.txt"

OUTPERFORMANCE_CHART_PATH = (
    OUTPUT_CHART_DIR / "adaptive_rules_mean_outperformance.png"
)

NET_EFFECT_CHART_PATH = (
    OUTPUT_CHART_DIR / "adaptive_rules_net_option_effect.png"
)

TRANSACTION_COST_CHART_PATH = (
    OUTPUT_CHART_DIR / "adaptive_rules_transaction_cost.png"
)


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

ADAPTIVE_RULE_LABELS = [
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

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            "Could not find management_rule_comparison.csv at:\n"
            f"{INPUT_PATH}\n\n"
            "Run app/main.py first."
        )

    return pd.read_csv(INPUT_PATH)


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
    Pull one metric from the wide management_rule_comparison.csv file.
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
# Build chart data
# =============================================================================

def build_adaptive_chart_data(wide_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a long-format adaptive-rule comparison table.
    """

    rows = []

    for regime in REGIME_ORDER:
        for rule_label in ADAPTIVE_RULE_LABELS:
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
        categories=ADAPTIVE_RULE_LABELS,
        ordered=True,
    )

    result_df = result_df.sort_values(
        ["Regime", "Rule_Label"]
    ).reset_index(drop=True)

    return result_df


# =============================================================================
# Report
# =============================================================================

def build_report(chart_df: pd.DataFrame) -> str:
    """
    Build a concise text report explaining whether the adaptive rules differ.
    """

    lines = []

    lines.append("COVERED CALL SIMULATOR - ADAPTIVE RULE CHART REPORT")
    lines.append("=" * 100)
    lines.append("")
    lines.append(f"Input file:       {INPUT_PATH}")
    lines.append(f"Chart data file:  {CHART_DATA_PATH}")
    lines.append("")
    lines.append("Adaptive rules compared:")
    for rule_label in ADAPTIVE_RULE_LABELS:
        lines.append(f"    {rule_label}")
    lines.append("")

    for regime in REGIME_ORDER:
        regime_df = chart_df[
            chart_df["Regime"].astype(str) == regime
        ].copy()

        lines.append("-" * 100)
        lines.append(f"Regime: {regime}")
        lines.append("-" * 100)

        if regime_df.empty:
            lines.append("No data available.")
            lines.append("")
            continue

        for _, row in regime_df.iterrows():
            lines.append(
                f"{str(row['Rule_Label']):<34} | "
                f"Outperf={format_decimal(row['Mean_Outperformance'])} | "
                f"Net option={format_currency(row['Mean_Net_Option_Effect'])} | "
                f"Cost={format_currency(row['Mean_Total_Transaction_Cost'])} | "
                f"Cycles={format_decimal(row['Mean_Option_Cycles'], 2)}"
            )

        outperf_values = pd.to_numeric(
            regime_df["Mean_Outperformance"],
            errors="coerce",
        ).dropna()

        cost_values = pd.to_numeric(
            regime_df["Mean_Total_Transaction_Cost"],
            errors="coerce",
        ).dropna()

        if not outperf_values.empty:
            outperf_range = float(outperf_values.max() - outperf_values.min())
        else:
            outperf_range = float("nan")

        if not cost_values.empty:
            cost_range = float(cost_values.max() - cost_values.min())
        else:
            cost_range = float("nan")

        lines.append("")
        lines.append(
            f"Outperformance range across adaptive rules: "
            f"{format_decimal(outperf_range, 8)}"
        )
        lines.append(
            f"Transaction-cost range across adaptive rules: "
            f"{format_currency(cost_range)}"
        )

        if pd.notna(outperf_range) and abs(outperf_range) < 0.000001:
            lines.append("Interpretation: adaptive rules are identical in this regime.")
        else:
            lines.append("Interpretation: adaptive rules differ in this regime.")

        lines.append("")

    lines.append("=" * 100)
    lines.append("Overall interpretation")
    lines.append("=" * 100)
    lines.append("")
    lines.append(
        "These charts are intended to show whether the three adaptive rules "
        "produce different results under the current simulator assumptions."
    )
    lines.append("")
    lines.append(
        "At the current default DTE and low transaction costs, the adaptive rules "
        "are expected to be identical or nearly identical in most regimes."
    )
    lines.append("")
    lines.append(
        "The DTE-aware rule becomes more useful when DTE changes. The cost-aware "
        "rule becomes more useful when transaction costs rise in sideways markets."
    )
    lines.append("")
    lines.append(
        "If this report shows no meaningful differences, that is not a problem. "
        "It confirms that the more general adaptive rules reduce to the simpler "
        "adaptive rule under the current default assumptions."
    )

    return "\n".join(lines)


# =============================================================================
# Charts
# =============================================================================

def save_grouped_bar_chart(
    chart_df: pd.DataFrame,
    metric: str,
    title: str,
    ylabel: str,
    output_path: Path,
) -> None:
    """
    Save a grouped bar chart by regime and adaptive rule.
    """

    plot_df = chart_df.copy()
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
    pivot = pivot[ADAPTIVE_RULE_LABELS]

    ax = pivot.plot(kind="bar", figsize=(14, 7))
    ax.axhline(0, linewidth=1)
    ax.set_title(title)
    ax.set_xlabel("Regime")
    ax.set_ylabel(ylabel)

    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()


def save_charts(chart_df: pd.DataFrame) -> None:
    """
    Save all adaptive-rule charts.
    """

    save_grouped_bar_chart(
        chart_df=chart_df,
        metric="Mean_Outperformance",
        title="Adaptive Rules - Mean Outperformance by Regime",
        ylabel="Mean Outperformance",
        output_path=OUTPERFORMANCE_CHART_PATH,
    )

    save_grouped_bar_chart(
        chart_df=chart_df,
        metric="Mean_Net_Option_Effect",
        title="Adaptive Rules - Mean Net Option Effect by Regime",
        ylabel="Mean Net Option Effect",
        output_path=NET_EFFECT_CHART_PATH,
    )

    save_grouped_bar_chart(
        chart_df=chart_df,
        metric="Mean_Total_Transaction_Cost",
        title="Adaptive Rules - Mean Transaction Cost by Regime",
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
    chart_df = build_adaptive_chart_data(wide_df)

    chart_df.to_csv(CHART_DATA_PATH, index=False)

    report_text = build_report(chart_df)
    REPORT_PATH.write_text(report_text, encoding="utf-8")

    save_charts(chart_df)

    print("")
    print("=" * 100)
    print("Adaptive rule charts complete.")
    print("=" * 100)
    print("")
    print("Saved files:")
    print(f"  {CHART_DATA_PATH}")
    print(f"  {REPORT_PATH}")
    print(f"  {OUTPERFORMANCE_CHART_PATH}")
    print(f"  {NET_EFFECT_CHART_PATH}")
    print(f"  {TRANSACTION_COST_CHART_PATH}")
    print("")
    print("Done.")
    print("")


if __name__ == "__main__":
    main()