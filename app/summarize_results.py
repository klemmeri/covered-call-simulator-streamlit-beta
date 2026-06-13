"""
summarize_results.py

Reads the Covered Call Simulator comparison outputs and prints a clean
regime-level recommendation report.

It also saves the same report to:

    outputs/tables/comparison/final_recommendation_report.txt

Input files:

    outputs/tables/comparison/strategy_map.csv
    outputs/tables/comparison/management_rule_comparison.csv

This script does not run simulations. It only summarizes existing results.

Use after running:

    app/main.py

Current adaptive rules summarized:

    1. AdaptiveClose50Wait10
    2. AdaptiveClose50Wait10CostAware
    3. AdaptiveRegimeDTECost
"""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

STRATEGY_MAP_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "comparison"
    / "strategy_map.csv"
)

MANAGEMENT_RULE_COMPARISON_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "comparison"
    / "management_rule_comparison.csv"
)

FINAL_REPORT_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "comparison"
    / "final_recommendation_report.txt"
)


REGIME_ORDER = [
    "baseline",
    "sideways_market",
    "bullish_market",
    "bearish_market",
    "high_volatility",
    "low_volatility",
]


ORIGINAL_ADAPTIVE_LABEL = "AdaptiveClose50Wait10"
COST_AWARE_ADAPTIVE_LABEL = "AdaptiveClose50Wait10CostAware"
DTE_AWARE_ADAPTIVE_LABEL = "AdaptiveRegimeDTECost"

SIDEWAYS_COST_AWARE_COMMISSION_THRESHOLD = 1.25
SIDEWAYS_COST_AWARE_SLIPPAGE_THRESHOLD = 0.025

DTE_AWARE_SIDEWAYS_HOLD_MAX_DTE = 14
DTE_AWARE_LONG_DTE_HOLD_THRESHOLD = 45


def load_csv(path: Path, description: str) -> pd.DataFrame:
    """
    Load a CSV file with a clear error message.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Could not find {description} at:\n{path}\n\n"
            "Run app/main.py first to generate the comparison files."
        )

    return pd.read_csv(path)


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


def format_decimal(value: object, digits: int = 4) -> str:
    """
    Format a decimal value.
    """
    numeric = pd.to_numeric(value, errors="coerce")

    if pd.isna(numeric):
        return "NA"

    return f"{float(numeric):,.{digits}f}"


def format_currency(value: object) -> str:
    """
    Format a currency value.
    """
    numeric = pd.to_numeric(value, errors="coerce")

    if pd.isna(numeric):
        return "NA"

    return f"${float(numeric):,.2f}"


def get_strategy_row(strategy_df: pd.DataFrame, regime: str) -> pd.Series | None:
    """
    Return the strategy_map row for one regime.
    """
    regime_matches = strategy_df["Regime"].apply(normalize_text) == normalize_text(regime)
    regime_df = strategy_df[regime_matches]

    if regime_df.empty:
        return None

    return regime_df.iloc[0]


def get_wide_value(
    wide_df: pd.DataFrame,
    regime: str,
    label: str,
    metric: str,
) -> float | None:
    """
    Pull a value from management_rule_comparison.csv.

    Example column names:

        Wait10d_Mean_Outperformance
        Close50_Mean_Net_Option_Effect
        AdaptiveClose50Wait10_Mean_Outperformance
        AdaptiveClose50Wait10CostAware_Mean_Outperformance
        AdaptiveRegimeDTECost_Mean_Outperformance
    """
    if "Regime" not in wide_df.columns:
        return None

    regime_matches = wide_df["Regime"].apply(normalize_text) == normalize_text(regime)
    regime_df = wide_df[regime_matches]

    if regime_df.empty:
        return None

    column_name = f"{label}_{metric}"

    if column_name not in wide_df.columns:
        return None

    value = pd.to_numeric(regime_df.iloc[0][column_name], errors="coerce")

    if pd.isna(value):
        return None

    return float(value)


def classify_practical_rule(
    preferred_label: str,
    second_label: str,
    edge: float,
) -> str:
    """
    Convert the preferred and second-best labels into a practical recommendation.
    """
    materiality_threshold = 0.005

    adaptive_labels = {
        ORIGINAL_ADAPTIVE_LABEL,
        COST_AWARE_ADAPTIVE_LABEL,
        DTE_AWARE_ADAPTIVE_LABEL,
    }

    if abs(edge) < materiality_threshold:
        if preferred_label in adaptive_labels:
            return (
                "Use the adaptive rule; it ties the best fixed rule within "
                "the materiality threshold."
            )

        if second_label in adaptive_labels:
            return (
                "Use the adaptive rule; it ties the preferred fixed rule within "
                "the materiality threshold and is simpler to implement as a "
                "decision map."
            )

        return (
            "No strong edge; use the simpler or lower-turnover rule among "
            "the top choices."
        )

    if preferred_label == ORIGINAL_ADAPTIVE_LABEL:
        return "Use the original adaptive rule."

    if preferred_label == COST_AWARE_ADAPTIVE_LABEL:
        return "Use the cost-aware adaptive rule."

    if preferred_label == DTE_AWARE_ADAPTIVE_LABEL:
        return "Use the DTE-aware adaptive rule."

    if preferred_label == "Wait10d":
        return "Close at 50% profit, then wait 10 trading days before reselling."

    if preferred_label == "Close50":
        return "Close at 50% profit and immediately resell."

    if preferred_label == "Hold":
        return "Hold covered calls to expiration."

    if preferred_label.startswith("Wait"):
        return f"Close at 50% profit, then use {preferred_label}."

    if preferred_label.startswith("Pullback"):
        return f"Use the pullback rule: {preferred_label}."

    return f"Use {preferred_label}."


class ReportBuilder:
    """
    Helper class that collects report lines, then can print and save them.
    """

    def __init__(self) -> None:
        self.lines: list[str] = []

    def add(self, line: str = "") -> None:
        """
        Add one line to the report.
        """
        self.lines.append(line)

    def add_header(self, title: str) -> None:
        """
        Add a formatted section header.
        """
        self.add()
        self.add("=" * 100)
        self.add(title)
        self.add("=" * 100)

    def add_separator(self) -> None:
        """
        Add a formatted separator.
        """
        self.add("-" * 100)

    def text(self) -> str:
        """
        Return the full report text.
        """
        return "\n".join(self.lines)

    def print(self) -> None:
        """
        Print the report to the console.
        """
        print(self.text())

    def save(self, path: Path) -> None:
        """
        Save the report to a text file.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.text(), encoding="utf-8")


def add_adaptive_metric_block(
    report: ReportBuilder,
    wide_df: pd.DataFrame,
    regime: str,
    label: str,
    heading: str,
) -> None:
    """
    Add a metric block for one adaptive rule label.
    """

    adaptive_outperf = get_wide_value(
        wide_df=wide_df,
        regime=regime,
        label=label,
        metric="Mean_Outperformance",
    )

    adaptive_net_effect = get_wide_value(
        wide_df=wide_df,
        regime=regime,
        label=label,
        metric="Mean_Net_Option_Effect",
    )

    adaptive_transaction_cost = get_wide_value(
        wide_df=wide_df,
        regime=regime,
        label=label,
        metric="Mean_Total_Transaction_Cost",
    )

    adaptive_commission_cost = get_wide_value(
        wide_df=wide_df,
        regime=regime,
        label=label,
        metric="Mean_Total_Commission_Cost",
    )

    adaptive_slippage_cost = get_wide_value(
        wide_df=wide_df,
        regime=regime,
        label=label,
        metric="Mean_Total_Slippage_Cost",
    )

    adaptive_cycles = get_wide_value(
        wide_df=wide_df,
        regime=regime,
        label=label,
        metric="Mean_Option_Cycles",
    )

    if (
        adaptive_outperf is None
        and adaptive_net_effect is None
        and adaptive_transaction_cost is None
        and adaptive_commission_cost is None
        and adaptive_slippage_cost is None
        and adaptive_cycles is None
    ):
        return

    report.add(f"{heading}:")

    if adaptive_outperf is not None:
        report.add(f"    Mean outperformance:        {format_decimal(adaptive_outperf)}")

    if adaptive_net_effect is not None:
        report.add(f"    Net option effect:          {format_currency(adaptive_net_effect)}")

    if adaptive_transaction_cost is not None:
        report.add(f"    Transaction cost:           {format_currency(adaptive_transaction_cost)}")

    if adaptive_commission_cost is not None:
        report.add(f"    Commission cost:            {format_currency(adaptive_commission_cost)}")

    if adaptive_slippage_cost is not None:
        report.add(f"    Slippage cost:              {format_currency(adaptive_slippage_cost)}")

    if adaptive_cycles is not None:
        report.add(f"    Mean option cycles:         {format_decimal(adaptive_cycles, 2)}")

    report.add()


def add_regime_summary(
    report: ReportBuilder,
    strategy_df: pd.DataFrame,
    wide_df: pd.DataFrame,
) -> None:
    """
    Add one clean summary block per regime.
    """
    report.add_header("COVERED CALL SIMULATOR - FINAL REGIME SUMMARY")

    report.add()
    report.add(f"Strategy map file:               {STRATEGY_MAP_PATH}")
    report.add(f"Management rule comparison file: {MANAGEMENT_RULE_COMPARISON_PATH}")
    report.add(f"Saved report file:               {FINAL_REPORT_PATH}")
    report.add()

    for regime in REGIME_ORDER:
        row = get_strategy_row(strategy_df, regime)

        report.add_separator()
        report.add(f"Regime: {regime}")
        report.add_separator()

        if row is None:
            report.add("No results found for this regime.")
            report.add()
            continue

        preferred_label = str(row["Preferred_Label"])
        second_label = str(row["Second_Best_Label"])

        best_outperf = pd.to_numeric(row["Best_Mean_Outperformance"], errors="coerce")
        second_outperf = pd.to_numeric(
            row["Second_Best_Mean_Outperformance"],
            errors="coerce",
        )
        edge = pd.to_numeric(row["Outperformance_Edge"], errors="coerce")
        best_net_effect = pd.to_numeric(row["Best_Net_Option_Effect"], errors="coerce")

        if "Best_Transaction_Cost" in row.index:
            best_transaction_cost = pd.to_numeric(
                row["Best_Transaction_Cost"],
                errors="coerce",
            )
        else:
            best_transaction_cost = None

        signal_strength = str(row["Signal_Strength"])
        recommended_action = str(row["Recommended_Action"])
        main_reason = str(row["Main_Reason"])

        practical_rule = classify_practical_rule(
            preferred_label=preferred_label,
            second_label=second_label,
            edge=float(edge) if not pd.isna(edge) else 0.0,
        )

        preferred_transaction_cost = get_wide_value(
            wide_df=wide_df,
            regime=regime,
            label=preferred_label,
            metric="Mean_Total_Transaction_Cost",
        )

        preferred_commission_cost = get_wide_value(
            wide_df=wide_df,
            regime=regime,
            label=preferred_label,
            metric="Mean_Total_Commission_Cost",
        )

        preferred_slippage_cost = get_wide_value(
            wide_df=wide_df,
            regime=regime,
            label=preferred_label,
            metric="Mean_Total_Slippage_Cost",
        )

        report.add(f"Preferred label:               {preferred_label}")
        report.add(f"Second-best label:             {second_label}")
        report.add(f"Signal strength:               {signal_strength}")
        report.add(f"Best mean outperformance:      {format_decimal(best_outperf)}")
        report.add(f"Second-best outperformance:    {format_decimal(second_outperf)}")
        report.add(f"Outperformance edge:           {format_decimal(edge)}")
        report.add(f"Best net option effect:        {format_currency(best_net_effect)}")

        if best_transaction_cost is not None:
            report.add(f"Best transaction cost:         {format_currency(best_transaction_cost)}")

        report.add()

        if preferred_transaction_cost is not None:
            report.add(f"Preferred transaction cost:    {format_currency(preferred_transaction_cost)}")

        if preferred_commission_cost is not None:
            report.add(f"Preferred commission cost:     {format_currency(preferred_commission_cost)}")

        if preferred_slippage_cost is not None:
            report.add(f"Preferred slippage cost:       {format_currency(preferred_slippage_cost)}")

        if (
            preferred_transaction_cost is not None
            or preferred_commission_cost is not None
            or preferred_slippage_cost is not None
        ):
            report.add()

        add_adaptive_metric_block(
            report=report,
            wide_df=wide_df,
            regime=regime,
            label=ORIGINAL_ADAPTIVE_LABEL,
            heading="Original adaptive rule",
        )

        add_adaptive_metric_block(
            report=report,
            wide_df=wide_df,
            regime=regime,
            label=COST_AWARE_ADAPTIVE_LABEL,
            heading="Cost-aware adaptive rule",
        )

        add_adaptive_metric_block(
            report=report,
            wide_df=wide_df,
            regime=regime,
            label=DTE_AWARE_ADAPTIVE_LABEL,
            heading="DTE-aware adaptive rule",
        )

        report.add(f"Recommended action:            {recommended_action}")
        report.add(f"Main reason:                   {main_reason}")
        report.add(f"Practical interpretation:      {practical_rule}")
        report.add()


def add_final_recommendation(report: ReportBuilder) -> None:
    """
    Add the overall practical recommendation.
    """
    report.add_header("OVERALL PRACTICAL RULE")

    report.add()
    report.add("Use the DTE-aware adaptive rule as the newest candidate working recommendation:")
    report.add()
    report.add("    If regime is bearish_market:")
    report.add("        Close at 50% profit and immediately resell.")
    report.add()
    report.add("    If regime is sideways_market:")
    report.add(f"        If DTE <= {DTE_AWARE_SIDEWAYS_HOLD_MAX_DTE}:")
    report.add("            Hold covered calls to expiration.")
    report.add()
    report.add(f"        If DTE >= {DTE_AWARE_SIDEWAYS_HOLD_MAX_DTE + 7}:")
    report.add("            Close at 50% profit and immediately resell,")
    report.add("            unless transaction costs are high.")
    report.add()
    report.add("        If transaction costs are high:")
    report.add("            Hold covered calls to expiration.")
    report.add()
    report.add("    If regime is baseline, bullish_market, high_volatility, or low_volatility:")
    report.add(f"        If DTE < {DTE_AWARE_LONG_DTE_HOLD_THRESHOLD}:")
    report.add("            Close at 50% profit, then wait 10 trading days before reselling.")
    report.add()
    report.add(f"        If DTE >= {DTE_AWARE_LONG_DTE_HOLD_THRESHOLD}:")
    report.add("            Hold covered calls to expiration.")
    report.add()
    report.add("Sideways-market transaction-cost threshold:")
    report.add(
        f"    Commission threshold: ${SIDEWAYS_COST_AWARE_COMMISSION_THRESHOLD:.2f} "
        "per contract"
    )
    report.add(
        f"    Slippage threshold:   ${SIDEWAYS_COST_AWARE_SLIPPAGE_THRESHOLD:.3f} "
        "per share"
    )
    report.add()
    report.add("    Rule trigger:")
    report.add(
        "        If commission >= threshold OR slippage >= threshold, treat "
        "sideways_market as high-cost and prefer hold_to_expiration."
    )
    report.add()
    report.add("Interpretation:")
    report.add(
        "    The earlier regime-only adaptive rule was stable for the default "
        "DTE, but the DTE sensitivity test showed that rule preference can "
        "change when DTE changes."
    )
    report.add(
        "    The DTE-aware rule keeps the original regime logic where it remains "
        "robust, especially bearish_market, but adds DTE as another decision "
        "variable."
    )
    report.add(
        "    For the current default DTE and low transaction costs, the DTE-aware "
        "rule should behave like the earlier adaptive rules. Its advantage is "
        "that it has a rule structure for shorter and longer DTE settings."
    )
    report.add()
    report.add("Important caution:")
    report.add(
        "    The DTE-aware rule is currently a candidate rule. It should remain "
        "side-by-side with the original adaptive and cost-aware adaptive rules "
        "until robustness testing confirms it should become the default."
    )
    report.add()


def build_report(strategy_df: pd.DataFrame, wide_df: pd.DataFrame) -> ReportBuilder:
    """
    Build the full report object.
    """
    report = ReportBuilder()

    add_regime_summary(
        report=report,
        strategy_df=strategy_df,
        wide_df=wide_df,
    )

    add_final_recommendation(report)

    return report


def validate_strategy_map(strategy_df: pd.DataFrame) -> None:
    """
    Validate required strategy_map.csv columns.
    """
    required_strategy_columns = [
        "Regime",
        "Recommended_Action",
        "Preferred_Label",
        "Signal_Strength",
        "Best_Mean_Outperformance",
        "Second_Best_Mean_Outperformance",
        "Outperformance_Edge",
        "Best_Net_Option_Effect",
        "Second_Best_Label",
        "Main_Reason",
    ]

    missing_columns = [
        col for col in required_strategy_columns
        if col not in strategy_df.columns
    ]

    if missing_columns:
        raise KeyError(
            "strategy_map.csv is missing these expected columns:\n"
            f"{missing_columns}\n\n"
            f"Available columns are:\n{list(strategy_df.columns)}"
        )


def validate_management_rule_comparison(wide_df: pd.DataFrame) -> None:
    """
    Validate required management_rule_comparison.csv columns.
    """
    if "Regime" not in wide_df.columns:
        raise KeyError(
            "management_rule_comparison.csv is missing the Regime column.\n\n"
            f"Available columns are:\n{list(wide_df.columns)}"
        )


def main() -> None:
    strategy_df = load_csv(
        STRATEGY_MAP_PATH,
        "strategy_map.csv",
    )

    wide_df = load_csv(
        MANAGEMENT_RULE_COMPARISON_PATH,
        "management_rule_comparison.csv",
    )

    validate_strategy_map(strategy_df)
    validate_management_rule_comparison(wide_df)

    report = build_report(
        strategy_df=strategy_df,
        wide_df=wide_df,
    )

    report.print()
    report.save(FINAL_REPORT_PATH)

    print()
    print("=" * 100)
    print("Report saved to:")
    print(FINAL_REPORT_PATH)
    print("=" * 100)


if __name__ == "__main__":
    main()