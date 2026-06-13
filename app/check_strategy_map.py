"""
check_strategy_map.py

Checks strategy_map.csv and management_rule_comparison.csv after the
Covered Call Simulator batch run.

This version validates all three adaptive rules:

    1. AdaptiveClose50Wait10
    2. AdaptiveClose50Wait10CostAware
    3. AdaptiveRegimeDTECost

Expected behavior under the current standard transaction costs and default DTE:

    option_commission_per_contract = $0.65
    option_slippage_per_share      = $0.01

The current default DTE is treated as the standard simulator DTE, currently
the same DTE used in the main 66-experiment batch.

Expected fixed-rule behavior at the current default DTE:

    baseline:
        should match Wait10d

    bearish_market:
        should match Close50

    bullish_market:
        should match Wait10d

    high_volatility:
        should match Wait10d

    low_volatility:
        should match Wait10d

    sideways_market:
        should match Close50

Why sideways_market still matches Close50 here:
    The current standard transaction costs are below the sideways-market
    cost-aware threshold:

        commission threshold = $1.25 per contract
        slippage threshold   = $0.025 per share

    Therefore, both cost-aware adaptive rules should still behave like Close50
    in sideways_market under the standard configuration.

The adaptive rules are implemented inside app/portfolio.py.
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


ORIGINAL_ADAPTIVE_LABEL = "AdaptiveClose50Wait10"
COST_AWARE_ADAPTIVE_LABEL = "AdaptiveClose50Wait10CostAware"
DTE_AWARE_ADAPTIVE_LABEL = "AdaptiveRegimeDTECost"

SIDEWAYS_COST_AWARE_COMMISSION_THRESHOLD = 1.25
SIDEWAYS_COST_AWARE_SLIPPAGE_THRESHOLD = 0.025

EXPECTED_FIXED_RULE_BY_REGIME = {
    "baseline": "Wait10d",
    "bearish_market": "Close50",
    "bullish_market": "Wait10d",
    "high_volatility": "Wait10d",
    "low_volatility": "Wait10d",
    "sideways_market": "Close50",
}

ADAPTIVE_LABELS_TO_CHECK = [
    ORIGINAL_ADAPTIVE_LABEL,
    COST_AWARE_ADAPTIVE_LABEL,
    DTE_AWARE_ADAPTIVE_LABEL,
]

METRICS_TO_CHECK = [
    "Mean_Outperformance",
    "Mean_Net_Option_Effect",
    "Mean_Total_Transaction_Cost",
    "Mean_Total_Commission_Cost",
    "Mean_Total_Slippage_Cost",
    "Mean_Option_Cycles",
]


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


def get_metric_from_wide_table(
    wide_df: pd.DataFrame,
    regime: str,
    label: str,
    metric: str,
) -> float | None:
    """
    Pull a metric value from management_rule_comparison.csv.

    Example columns:

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

    column = f"{label}_{metric}"

    if column not in wide_df.columns:
        return None

    value = pd.to_numeric(regime_df.iloc[0][column], errors="coerce")

    if pd.isna(value):
        return None

    return float(value)


def validate_strategy_map(strategy_df: pd.DataFrame) -> None:
    """
    Validate expected strategy_map.csv columns.
    """
    required_strategy_columns = [
        "Regime",
        "Preferred_Label",
        "Second_Best_Label",
        "Best_Mean_Outperformance",
        "Second_Best_Mean_Outperformance",
        "Outperformance_Edge",
        "Main_Reason",
    ]

    missing_strategy_columns = [
        col for col in required_strategy_columns
        if col not in strategy_df.columns
    ]

    if missing_strategy_columns:
        raise KeyError(
            "strategy_map.csv is missing these expected columns:\n"
            f"{missing_strategy_columns}\n\n"
            f"Available columns are:\n{list(strategy_df.columns)}"
        )


def validate_management_rule_comparison(wide_df: pd.DataFrame) -> None:
    """
    Validate expected management_rule_comparison.csv structure.
    """
    if "Regime" not in wide_df.columns:
        raise KeyError(
            "management_rule_comparison.csv is missing the Regime column.\n\n"
            f"Available columns are:\n{list(wide_df.columns)}"
        )


def print_strategy_map_context(
    strategy_df: pd.DataFrame,
    regime: str,
) -> None:
    """
    Print the strategy_map context for one regime.
    """
    strategy_match = (
        strategy_df["Regime"].apply(normalize_text) == normalize_text(regime)
    )
    regime_strategy_df = strategy_df[strategy_match]

    if regime_strategy_df.empty:
        print("strategy_map.csv context: missing regime")
        return

    row = regime_strategy_df.iloc[0]

    preferred_label = str(row["Preferred_Label"])
    second_best_label = str(row["Second_Best_Label"])
    best_outperf = pd.to_numeric(row["Best_Mean_Outperformance"], errors="coerce")
    second_outperf = pd.to_numeric(
        row["Second_Best_Mean_Outperformance"],
        errors="coerce",
    )
    edge = pd.to_numeric(row["Outperformance_Edge"], errors="coerce")
    main_reason = str(row["Main_Reason"])

    print("strategy_map.csv context:")
    print(f"  Preferred label:       {preferred_label}")
    print(f"  Second-best label:     {second_best_label}")

    if not pd.isna(best_outperf):
        print(f"  Best outperformance:   {float(best_outperf):,.4f}")

    if not pd.isna(second_outperf):
        print(f"  Second outperformance: {float(second_outperf):,.4f}")

    if not pd.isna(edge):
        print(f"  Reported edge:         {float(edge):,.4f}")

    print(f"  Main reason:           {main_reason}")
    print()


def check_one_adaptive_rule(
    wide_df: pd.DataFrame,
    regime: str,
    adaptive_label: str,
    expected_fixed_label: str,
) -> bool:
    """
    Check one adaptive rule against one expected fixed rule in one regime.

    Returns True if all available checked metrics match or if the adaptive
    metric beats the fixed metric where appropriate.

    For this simulator, the expected behavior is exact equivalence because
    these adaptive rules map directly to a fixed rule within each regime under
    the current standard DTE and transaction-cost assumptions.
    """

    print(f"Checking adaptive label: {adaptive_label}")
    print(f"Expected fixed label:   {expected_fixed_label}")
    print()

    all_metrics_passed = True

    for metric in METRICS_TO_CHECK:
        adaptive_value = get_metric_from_wide_table(
            wide_df=wide_df,
            regime=regime,
            label=adaptive_label,
            metric=metric,
        )

        expected_value = get_metric_from_wide_table(
            wide_df=wide_df,
            regime=regime,
            label=expected_fixed_label,
            metric=metric,
        )

        if adaptive_value is None and expected_value is None:
            print(f"  {metric}: both missing; skipped.")
            continue

        if adaptive_value is None:
            print(f"  {metric}: FAIL - adaptive value missing.")
            all_metrics_passed = False
            continue

        if expected_value is None:
            print(f"  {metric}: FAIL - expected fixed-rule value missing.")
            all_metrics_passed = False
            continue

        difference = adaptive_value - expected_value

        print(
            f"  {metric}: "
            f"adaptive={adaptive_value:,.6f}, "
            f"expected={expected_value:,.6f}, "
            f"difference={difference:,.12f}"
        )

        if abs(difference) < 1.0e-10:
            continue

        # For outperformance and net option effect, beating the expected rule
        # would not be harmful, but exact equivalence is expected because these
        # adaptive rules are deterministic mappings to fixed rules.
        if metric in {
            "Mean_Outperformance",
            "Mean_Net_Option_Effect",
        } and difference > 0:
            print("    PASS - adaptive value is better than expected fixed value.")
            continue

        print("    FAIL - adaptive value does not match expected fixed value.")
        all_metrics_passed = False

    if all_metrics_passed:
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")

    print()

    return all_metrics_passed


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

    print("Loaded strategy_map.csv")
    print(f"Path: {STRATEGY_MAP_PATH}")
    print(f"Rows: {len(strategy_df)}")
    print()

    print("Loaded management_rule_comparison.csv")
    print(f"Path: {MANAGEMENT_RULE_COMPARISON_PATH}")
    print(f"Rows: {len(wide_df)}")
    print()

    print("=" * 100)
    print("ADAPTIVE RULE CHECK ACROSS ALL REGIMES")
    print("=" * 100)
    print()
    print("Adaptive rules checked:")
    print(f"  {ORIGINAL_ADAPTIVE_LABEL}")
    print(f"  {COST_AWARE_ADAPTIVE_LABEL}")
    print(f"  {DTE_AWARE_ADAPTIVE_LABEL}")
    print()
    print("Cost-aware sideways-market threshold:")
    print(
        f"  commission >= ${SIDEWAYS_COST_AWARE_COMMISSION_THRESHOLD:.2f} "
        "per contract"
    )
    print(
        f"  slippage   >= ${SIDEWAYS_COST_AWARE_SLIPPAGE_THRESHOLD:.3f} "
        "per share"
    )
    print()
    print(
        "Under the current standard costs and default DTE, all adaptive rules "
        "should match the expected fixed-rule benchmark in each regime."
    )
    print("=" * 100)
    print()

    overall_passed = True

    for regime, expected_fixed_label in EXPECTED_FIXED_RULE_BY_REGIME.items():
        print("-" * 100)
        print(f"Regime: {regime}")
        print("-" * 100)
        print()

        print_strategy_map_context(
            strategy_df=strategy_df,
            regime=regime,
        )

        for adaptive_label in ADAPTIVE_LABELS_TO_CHECK:
            passed = check_one_adaptive_rule(
                wide_df=wide_df,
                regime=regime,
                adaptive_label=adaptive_label,
                expected_fixed_label=expected_fixed_label,
            )

            if not passed:
                overall_passed = False

    print("=" * 100)

    if overall_passed:
        print("OVERALL RESULT: PASS")
        print(
            "AdaptiveClose50Wait10, AdaptiveClose50Wait10CostAware, and "
            "AdaptiveRegimeDTECost correctly match or beat the expected "
            "fixed-rule benchmark in all tested regimes under the current "
            "DTE and transaction-cost assumptions."
        )
    else:
        print("OVERALL RESULT: REVIEW NEEDED")
        print(
            "At least one adaptive rule did not match the expected fixed-rule "
            "behavior. Review the regime blocks above."
        )

    print("=" * 100)


if __name__ == "__main__":
    main()