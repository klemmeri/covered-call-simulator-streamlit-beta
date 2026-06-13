"""
regime_detection_borderline_test.py

Borderline diagnostic test for the rule-based regime detector.

This script stress-tests regime classification near the current threshold
boundaries.

It asks:

    1. Are boundary classifications logical?
    2. Do small changes around thresholds change the detected regime?
    3. If the detected regime changes, does the preferred covered-call rule
       change in a material way?

This script does not modify app/main.py.
It is a standalone diagnostic script.

Outputs:

    outputs/tables/comparison/regime_detection_borderline_summary.csv
    outputs/tables/comparison/regime_detection_borderline_comparison.csv
    outputs/tables/comparison/regime_detection_borderline_report.txt
"""

import copy
import sys
from pathlib import Path

import pandas as pd


# =============================================================================
# Import project modules
# =============================================================================

CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import SimulationConfig
from app.simulator import SimulationEngine
from app.regime_detection import detect_regime


# =============================================================================
# User settings
# =============================================================================

N_PATHS = 250

MATERIALITY_THRESHOLD = 0.0050

RULE_CONFIGS = {
    "HoldToExpiration": {
        "management_rule": "hold_to_expiration",
        "wait_days_after_profit_close": 0,
        "pullback_fraction_after_profit_close": 0.0,
        "max_wait_days_after_profit_close": 0,
        "adaptive_wait_days_after_profit_close": 10,
    },
    "Close50": {
        "management_rule": "close_at_50_percent_profit",
        "wait_days_after_profit_close": 0,
        "pullback_fraction_after_profit_close": 0.0,
        "max_wait_days_after_profit_close": 0,
        "adaptive_wait_days_after_profit_close": 10,
    },
    "Wait10d": {
        "management_rule": "close_at_50_percent_profit_then_wait",
        "wait_days_after_profit_close": 10,
        "pullback_fraction_after_profit_close": 0.0,
        "max_wait_days_after_profit_close": 0,
        "adaptive_wait_days_after_profit_close": 10,
    },
    "AdaptiveRegimeDTECost": {
        "management_rule": "adaptive_by_regime_dte_cost",
        "wait_days_after_profit_close": 0,
        "pullback_fraction_after_profit_close": 0.0,
        "max_wait_days_after_profit_close": 0,
        "adaptive_wait_days_after_profit_close": 10,
    },
}

RULE_ORDER = list(RULE_CONFIGS.keys())


# =============================================================================
# Borderline test cases
# =============================================================================

TEST_CASES = [
    # -------------------------------------------------------------------------
    # Bearish return threshold: -0.03
    # -------------------------------------------------------------------------
    {
        "Group": "Return threshold",
        "Case": "just_above_bearish_threshold",
        "Annual_Return": -0.029,
        "Annual_Volatility": 0.250,
        "Expected_Comment": "Slightly above bearish threshold; should avoid bearish classification.",
    },
    {
        "Group": "Return threshold",
        "Case": "exactly_bearish_threshold",
        "Annual_Return": -0.030,
        "Annual_Volatility": 0.250,
        "Expected_Comment": "Exactly at bearish threshold; current rule uses <=, so bearish_market is expected.",
    },
    {
        "Group": "Return threshold",
        "Case": "just_below_bearish_threshold",
        "Annual_Return": -0.031,
        "Annual_Volatility": 0.250,
        "Expected_Comment": "Slightly below bearish threshold; bearish_market is expected.",
    },

    # -------------------------------------------------------------------------
    # Sideways return threshold: +/- 0.03
    # -------------------------------------------------------------------------
    {
        "Group": "Return threshold",
        "Case": "sideways_positive_inside_threshold",
        "Annual_Return": 0.029,
        "Annual_Volatility": 0.180,
        "Expected_Comment": "Inside sideways return threshold and vol below sideways max; sideways_market expected.",
    },
    {
        "Group": "Return threshold",
        "Case": "sideways_positive_exact_threshold",
        "Annual_Return": 0.030,
        "Annual_Volatility": 0.180,
        "Expected_Comment": "Exactly at positive sideways threshold; current rule uses <= abs return, so sideways_market expected.",
    },
    {
        "Group": "Return threshold",
        "Case": "sideways_positive_outside_threshold",
        "Annual_Return": 0.031,
        "Annual_Volatility": 0.180,
        "Expected_Comment": "Just outside sideways return threshold; should not be sideways.",
    },

    # -------------------------------------------------------------------------
    # Bullish return threshold: 0.12
    # -------------------------------------------------------------------------
    {
        "Group": "Return threshold",
        "Case": "just_below_bullish_threshold",
        "Annual_Return": 0.119,
        "Annual_Volatility": 0.250,
        "Expected_Comment": "Slightly below bullish threshold; should avoid bullish classification.",
    },
    {
        "Group": "Return threshold",
        "Case": "exactly_bullish_threshold",
        "Annual_Return": 0.120,
        "Annual_Volatility": 0.250,
        "Expected_Comment": "Exactly at bullish threshold; current rule uses >=, so bullish_market expected.",
    },
    {
        "Group": "Return threshold",
        "Case": "just_above_bullish_threshold",
        "Annual_Return": 0.121,
        "Annual_Volatility": 0.250,
        "Expected_Comment": "Slightly above bullish threshold; bullish_market expected.",
    },

    # -------------------------------------------------------------------------
    # Low volatility threshold: 0.15
    # -------------------------------------------------------------------------
    {
        "Group": "Volatility threshold",
        "Case": "just_below_low_vol_threshold",
        "Annual_Return": 0.060,
        "Annual_Volatility": 0.149,
        "Expected_Comment": "Slightly below low-vol threshold; low_volatility expected unless sideways triggers first.",
    },
    {
        "Group": "Volatility threshold",
        "Case": "exactly_low_vol_threshold",
        "Annual_Return": 0.060,
        "Annual_Volatility": 0.150,
        "Expected_Comment": "Exactly at low-vol threshold; current rule uses <=, so low_volatility expected unless sideways triggers first.",
    },
    {
        "Group": "Volatility threshold",
        "Case": "just_above_low_vol_threshold",
        "Annual_Return": 0.060,
        "Annual_Volatility": 0.151,
        "Expected_Comment": "Slightly above low-vol threshold; should avoid low_volatility.",
    },

    # -------------------------------------------------------------------------
    # Sideways volatility max: 0.22
    # -------------------------------------------------------------------------
    {
        "Group": "Volatility threshold",
        "Case": "just_below_sideways_vol_max",
        "Annual_Return": 0.010,
        "Annual_Volatility": 0.219,
        "Expected_Comment": "Near-zero return and vol below sideways max; sideways_market expected.",
    },
    {
        "Group": "Volatility threshold",
        "Case": "exactly_sideways_vol_max",
        "Annual_Return": 0.010,
        "Annual_Volatility": 0.220,
        "Expected_Comment": "Near-zero return and exactly sideways vol max; current rule uses <=, so sideways_market expected.",
    },
    {
        "Group": "Volatility threshold",
        "Case": "just_above_sideways_vol_max",
        "Annual_Return": 0.010,
        "Annual_Volatility": 0.221,
        "Expected_Comment": "Near-zero return but just above sideways vol max; should avoid sideways_market.",
    },

    # -------------------------------------------------------------------------
    # Bullish volatility max: 0.35
    # -------------------------------------------------------------------------
    {
        "Group": "Volatility threshold",
        "Case": "just_below_bullish_vol_max",
        "Annual_Return": 0.150,
        "Annual_Volatility": 0.349,
        "Expected_Comment": "Strong return and vol below bullish max; bullish_market expected.",
    },
    {
        "Group": "Volatility threshold",
        "Case": "exactly_bullish_vol_max",
        "Annual_Return": 0.150,
        "Annual_Volatility": 0.350,
        "Expected_Comment": "Strong return and exactly bullish vol max; current rule uses <=, so bullish_market expected.",
    },
    {
        "Group": "Volatility threshold",
        "Case": "just_above_bullish_vol_max",
        "Annual_Return": 0.150,
        "Annual_Volatility": 0.351,
        "Expected_Comment": "Strong return but just above bullish vol max; should avoid bullish_market.",
    },

    # -------------------------------------------------------------------------
    # High volatility threshold: 0.40
    # -------------------------------------------------------------------------
    {
        "Group": "Volatility threshold",
        "Case": "just_below_high_vol_threshold",
        "Annual_Return": 0.080,
        "Annual_Volatility": 0.399,
        "Expected_Comment": "Just below high-vol threshold; should avoid high_volatility.",
    },
    {
        "Group": "Volatility threshold",
        "Case": "exactly_high_vol_threshold",
        "Annual_Return": 0.080,
        "Annual_Volatility": 0.400,
        "Expected_Comment": "Exactly at high-vol threshold; current rule uses >=, so high_volatility expected.",
    },
    {
        "Group": "Volatility threshold",
        "Case": "just_above_high_vol_threshold",
        "Annual_Return": 0.080,
        "Annual_Volatility": 0.401,
        "Expected_Comment": "Just above high-vol threshold; high_volatility expected.",
    },

    # -------------------------------------------------------------------------
    # Ambiguous combined cases
    # -------------------------------------------------------------------------
    {
        "Group": "Ambiguous combined",
        "Case": "bearish_and_high_vol",
        "Annual_Return": -0.050,
        "Annual_Volatility": 0.450,
        "Expected_Comment": "Both bearish and high vol; bearish should win because bearish is checked first.",
    },
    {
        "Group": "Ambiguous combined",
        "Case": "sideways_and_low_vol",
        "Annual_Return": 0.000,
        "Annual_Volatility": 0.120,
        "Expected_Comment": "Both sideways and low vol; sideways should win because sideways is checked before low_volatility.",
    },
    {
        "Group": "Ambiguous combined",
        "Case": "bullish_and_high_vol",
        "Annual_Return": 0.180,
        "Annual_Volatility": 0.450,
        "Expected_Comment": "Both bullish return and high vol; high_volatility should win because high vol is checked before bullish.",
    },
    {
        "Group": "Ambiguous combined",
        "Case": "bullish_and_low_vol",
        "Annual_Return": 0.150,
        "Annual_Volatility": 0.120,
        "Expected_Comment": "Both bullish and low vol; bullish should win because bullish is checked before low_volatility.",
    },
]


# =============================================================================
# Output paths
# =============================================================================

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "comparison"

SUMMARY_PATH = OUTPUT_TABLE_DIR / "regime_detection_borderline_summary.csv"
COMPARISON_PATH = OUTPUT_TABLE_DIR / "regime_detection_borderline_comparison.csv"
REPORT_PATH = OUTPUT_TABLE_DIR / "regime_detection_borderline_report.txt"


# =============================================================================
# Helpers
# =============================================================================

def clone_config(base_config: SimulationConfig, **updates) -> SimulationConfig:
    """
    Copy a SimulationConfig and update selected fields.
    """

    config = copy.deepcopy(base_config)

    for key, value in updates.items():
        if not hasattr(config, key):
            raise AttributeError(
                f"SimulationConfig has no field named '{key}'."
            )
        setattr(config, key, value)

    return config


def get_metric(df: pd.DataFrame, column_name: str) -> float:
    """
    Safely get the mean of a numeric result column.
    """

    if column_name not in df.columns:
        return float("nan")

    values = pd.to_numeric(df[column_name], errors="coerce")

    if values.dropna().empty:
        return float("nan")

    return float(values.mean())


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
# Simulation
# =============================================================================

def build_config(
    test_case: dict,
    rule_label: str,
) -> SimulationConfig:
    """
    Build one simulation config using the detected regime.
    """

    base_config = SimulationConfig()

    annual_return = float(test_case["Annual_Return"])
    annual_volatility = float(test_case["Annual_Volatility"])

    detected_regime = detect_regime(
        annual_return=annual_return,
        annual_volatility=annual_volatility,
    )

    rule_settings = RULE_CONFIGS[rule_label]

    config = clone_config(
        base_config,
        n_paths=N_PATHS,
        annual_return=annual_return,
        annual_volatility=annual_volatility,
        regime_name=detected_regime,
        **rule_settings,
    )

    return config


def run_single_experiment(
    test_case: dict,
    rule_label: str,
) -> dict:
    """
    Run one borderline-case/rule experiment.
    """

    case_name = str(test_case["Case"])

    experiment_name = f"{case_name}__{rule_label}"

    print("=" * 100)
    print(f"Running experiment: {experiment_name}")
    print("=" * 100)

    config = build_config(
        test_case=test_case,
        rule_label=rule_label,
    )

    engine = SimulationEngine(config)
    path_results_df = engine.run()

    annual_return = float(test_case["Annual_Return"])
    annual_volatility = float(test_case["Annual_Volatility"])

    detected_regime = detect_regime(
        annual_return=annual_return,
        annual_volatility=annual_volatility,
    )

    summary = {
        "Group": test_case["Group"],
        "Case": case_name,
        "Annual_Return": annual_return,
        "Annual_Volatility": annual_volatility,
        "Detected_Regime": detected_regime,
        "Expected_Comment": test_case["Expected_Comment"],
        "Rule_Label": rule_label,
        "Management_Rule": config.management_rule,
        "N_Paths": config.n_paths,
        "Mean_Outperformance": get_metric(
            path_results_df,
            "outperformance",
        ),
        "Mean_Net_Option_Effect": get_metric(
            path_results_df,
            "net_option_effect",
        ),
        "Mean_Total_Transaction_Cost": get_metric(
            path_results_df,
            "total_transaction_cost",
        ),
        "Mean_Option_Cycles": get_metric(
            path_results_df,
            "option_cycles",
        ),
        "Mean_Assignments": get_metric(
            path_results_df,
            "assignments",
        ),
    }

    return summary


def run_borderline_test() -> pd.DataFrame:
    """
    Run the full borderline regime-detection test.
    """

    rows = []

    total_experiments = len(TEST_CASES) * len(RULE_ORDER)

    print("")
    print("=" * 100)
    print("COVERED CALL SIMULATOR - REGIME DETECTION BORDERLINE TEST")
    print("=" * 100)
    print(f"Paths per experiment: {N_PATHS}")
    print(f"Test cases:           {len(TEST_CASES)}")
    print(f"Rules tested:         {RULE_ORDER}")
    print(f"Total experiments:    {total_experiments}")
    print("=" * 100)
    print("")

    experiment_count = 0

    for test_case in TEST_CASES:
        for rule_label in RULE_ORDER:
            experiment_count += 1

            print(f"Progress: {experiment_count} of {total_experiments}")

            summary = run_single_experiment(
                test_case=test_case,
                rule_label=rule_label,
            )

            rows.append(summary)

    summary_df = pd.DataFrame(rows)

    summary_df["Rule_Label"] = pd.Categorical(
        summary_df["Rule_Label"],
        categories=RULE_ORDER,
        ordered=True,
    )

    summary_df = summary_df.sort_values(
        ["Group", "Case", "Rule_Label"]
    ).reset_index(drop=True)

    return summary_df


# =============================================================================
# Analysis and report
# =============================================================================

def find_best_rule(group_df: pd.DataFrame) -> pd.Series | None:
    """
    Find best rule in one case.
    """

    df = group_df.copy()
    df["Mean_Outperformance"] = pd.to_numeric(
        df["Mean_Outperformance"],
        errors="coerce",
    )
    df = df.dropna(subset=["Mean_Outperformance"])

    if df.empty:
        return None

    idx = df["Mean_Outperformance"].idxmax()
    return df.loc[idx]


def build_case_comparison(summary_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build one best-rule row per borderline test case.
    """

    rows = []

    for case_name in sorted(summary_df["Case"].astype(str).unique()):
        case_df = summary_df[
            summary_df["Case"].astype(str) == case_name
        ].copy()

        best = find_best_rule(case_df)

        if best is None:
            continue

        adaptive_row = case_df[
            case_df["Rule_Label"].astype(str) == "AdaptiveRegimeDTECost"
        ]

        adaptive_outperformance = float("nan")

        if not adaptive_row.empty:
            adaptive_outperformance = float(
                pd.to_numeric(
                    adaptive_row.iloc[0]["Mean_Outperformance"],
                    errors="coerce",
                )
            )

        best_outperformance = float(best["Mean_Outperformance"])

        adaptive_minus_best = adaptive_outperformance - best_outperformance

        adaptive_materially_worse = (
            abs(adaptive_minus_best) >= MATERIALITY_THRESHOLD
            and adaptive_minus_best < 0
        )

        rows.append(
            {
                "Group": best["Group"],
                "Case": case_name,
                "Annual_Return": best["Annual_Return"],
                "Annual_Volatility": best["Annual_Volatility"],
                "Detected_Regime": best["Detected_Regime"],
                "Expected_Comment": best["Expected_Comment"],
                "Best_Rule": best["Rule_Label"],
                "Best_Outperformance": best_outperformance,
                "Adaptive_Outperformance": adaptive_outperformance,
                "Adaptive_Minus_Best": adaptive_minus_best,
                "Adaptive_Materially_Worse": adaptive_materially_worse,
            }
        )

    comparison_df = pd.DataFrame(rows)

    if not comparison_df.empty:
        comparison_df = comparison_df.sort_values(
            ["Group", "Case"]
        ).reset_index(drop=True)

    return comparison_df


def build_report(
    summary_df: pd.DataFrame,
    comparison_df: pd.DataFrame,
) -> str:
    """
    Build a plain-text borderline regime-detection report.
    """

    lines = []

    lines.append("COVERED CALL SIMULATOR - REGIME DETECTION BORDERLINE REPORT")
    lines.append("=" * 100)
    lines.append("")
    lines.append(f"Paths per experiment:       {N_PATHS}")
    lines.append(f"Materiality threshold:      {MATERIALITY_THRESHOLD:.4f}")
    lines.append(f"Summary file:               {SUMMARY_PATH}")
    lines.append(f"Comparison file:            {COMPARISON_PATH}")
    lines.append("")
    lines.append(
        "This test stress-tests the first-pass rule-based regime detector "
        "near threshold boundaries."
    )
    lines.append("")
    lines.append(
        "The purpose is to check whether borderline classifications are "
        "logical and whether the adaptive covered-call rule becomes materially "
        "worse near regime boundaries."
    )
    lines.append("")

    lines.append("-" * 100)
    lines.append("Best-rule comparison by borderline case")
    lines.append("-" * 100)
    lines.append("")

    for _, row in comparison_df.iterrows():
        lines.append(f"Case: {row['Case']}")
        lines.append(f"    Group:                      {row['Group']}")
        lines.append(
            f"    annual_return:              {format_decimal(row['Annual_Return'])}"
        )
        lines.append(
            f"    annual_volatility:          {format_decimal(row['Annual_Volatility'])}"
        )
        lines.append(f"    detected_regime:            {row['Detected_Regime']}")
        lines.append(f"    best_rule:                  {row['Best_Rule']}")
        lines.append(
            f"    best_outperformance:        {format_decimal(row['Best_Outperformance'])}"
        )
        lines.append(
            f"    adaptive_outperformance:    {format_decimal(row['Adaptive_Outperformance'])}"
        )
        lines.append(
            f"    adaptive_minus_best:        {format_decimal(row['Adaptive_Minus_Best'])}"
        )
        lines.append(
            "    adaptive_materially_worse: "
            f"{row['Adaptive_Materially_Worse']}"
        )
        lines.append(f"    comment:                    {row['Expected_Comment']}")
        lines.append("")

    lines.append("-" * 100)
    lines.append("Detailed rule results")
    lines.append("-" * 100)
    lines.append("")

    for case_name in sorted(summary_df["Case"].astype(str).unique()):
        case_df = summary_df[
            summary_df["Case"].astype(str) == case_name
        ].copy()

        if case_df.empty:
            continue

        first_row = case_df.iloc[0]

        lines.append(f"Case: {case_name}")
        lines.append(f"    Group:             {first_row['Group']}")
        lines.append(
            f"    annual_return:     {format_decimal(first_row['Annual_Return'])}"
        )
        lines.append(
            f"    annual_volatility: {format_decimal(first_row['Annual_Volatility'])}"
        )
        lines.append(f"    detected_regime:   {first_row['Detected_Regime']}")
        lines.append("")

        for _, row in case_df.iterrows():
            lines.append(
                f"        {str(row['Rule_Label']):<28} | "
                f"Outperf={format_decimal(row['Mean_Outperformance'])} | "
                f"Net option={format_currency(row['Mean_Net_Option_Effect'])} | "
                f"Cost={format_currency(row['Mean_Total_Transaction_Cost'])} | "
                f"Cycles={format_decimal(row['Mean_Option_Cycles'], 2)}"
            )

        lines.append("")

    adaptive_worse_count = 0
    best_rule_change_count = 0

    if not comparison_df.empty:
        adaptive_worse_count = int(
            comparison_df["Adaptive_Materially_Worse"].fillna(False).sum()
        )

        best_rule_change_count = int(
            (
                comparison_df["Best_Rule"].astype(str)
                != "AdaptiveRegimeDTECost"
            ).sum()
        )

    detected_regime_counts = (
        comparison_df["Detected_Regime"]
        .astype(str)
        .value_counts()
        .sort_index()
        if not comparison_df.empty
        else pd.Series(dtype=int)
    )

    lines.append("=" * 100)
    lines.append("Detected regime counts")
    lines.append("=" * 100)
    lines.append("")

    for regime_name, count in detected_regime_counts.items():
        lines.append(f"{regime_name:<24} {int(count)}")

    lines.append("")
    lines.append("=" * 100)
    lines.append("Overall conclusion")
    lines.append("=" * 100)
    lines.append("")
    lines.append(f"Borderline cases tested:       {len(comparison_df)}")
    lines.append(f"Best rule not adaptive:        {best_rule_change_count}")
    lines.append(f"Adaptive materially worse:     {adaptive_worse_count}")
    lines.append("")

    if adaptive_worse_count == 0:
        lines.append(
            "The adaptive DTE/cost rule was not materially worse than the best "
            "fixed rule in any borderline case."
        )
        lines.append("")
        lines.append(
            "This supports keeping the current regime detector thresholds for "
            "additional testing."
        )
    else:
        lines.append(
            "At least one borderline case made the adaptive rule materially worse. "
            "Review those cases before using detected regimes in the main simulator."
        )

    lines.append("")
    lines.append(
        "Recommendation: keep regime detection as a standalone diagnostic. "
        "Do not wire it into app/main.py yet. The next useful step is either "
        "to add historical ticker data or to test rolling return/volatility "
        "regime detection."
    )

    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)

    summary_df = run_borderline_test()
    comparison_df = build_case_comparison(summary_df)

    summary_df.to_csv(SUMMARY_PATH, index=False)
    comparison_df.to_csv(COMPARISON_PATH, index=False)

    report_text = build_report(
        summary_df=summary_df,
        comparison_df=comparison_df,
    )

    REPORT_PATH.write_text(report_text, encoding="utf-8")

    print("")
    print("=" * 100)
    print("Regime detection borderline test complete.")
    print("=" * 100)
    print("")
    print("Saved files:")
    print(f"  {SUMMARY_PATH}")
    print(f"  {COMPARISON_PATH}")
    print(f"  {REPORT_PATH}")
    print("")
    print("Done.")
    print("")


if __name__ == "__main__":
    main()