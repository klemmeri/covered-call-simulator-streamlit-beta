"""
regime_detection_test.py

Diagnostic test for the rule-based regime detector.

This script compares two approaches:

    1. Manually assigned regimes
    2. Automatically detected regimes

It asks:

    If we use the regime detector instead of manually assigning regime_name,
    does the adaptive covered-call recommendation change?

This script does not modify app/main.py.
It is a standalone diagnostic script.

Outputs:

    outputs/tables/comparison/regime_detection_test_summary.csv
    outputs/tables/comparison/regime_detection_test_report.txt
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

TEST_CASES = [
    {
        "Case": "baseline_manual",
        "Manual_Regime": "baseline",
        "Annual_Return": 0.08,
        "Annual_Volatility": 0.25,
    },
    {
        "Case": "sideways_manual",
        "Manual_Regime": "sideways_market",
        "Annual_Return": 0.00,
        "Annual_Volatility": 0.15,
    },
    {
        "Case": "bullish_manual",
        "Manual_Regime": "bullish_market",
        "Annual_Return": 0.18,
        "Annual_Volatility": 0.22,
    },
    {
        "Case": "bearish_manual",
        "Manual_Regime": "bearish_market",
        "Annual_Return": -0.12,
        "Annual_Volatility": 0.30,
    },
    {
        "Case": "high_volatility_manual",
        "Manual_Regime": "high_volatility",
        "Annual_Return": 0.08,
        "Annual_Volatility": 0.45,
    },
    {
        "Case": "low_volatility_manual",
        "Manual_Regime": "low_volatility",
        "Annual_Return": 0.06,
        "Annual_Volatility": 0.12,
    },
    {
        "Case": "leveraged_uptrend",
        "Manual_Regime": "high_volatility",
        "Annual_Return": 0.18,
        "Annual_Volatility": 0.70,
    },
    {
        "Case": "negative_high_volatility",
        "Manual_Regime": "bearish_market",
        "Annual_Return": -0.08,
        "Annual_Volatility": 0.48,
    },
]

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

MATERIALITY_THRESHOLD = 0.0050


# =============================================================================
# Output paths
# =============================================================================

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "comparison"

SUMMARY_PATH = OUTPUT_TABLE_DIR / "regime_detection_test_summary.csv"
REPORT_PATH = OUTPUT_TABLE_DIR / "regime_detection_test_report.txt"


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
    regime_source: str,
    rule_label: str,
) -> SimulationConfig:
    """
    Build one simulation config.

    regime_source:
        "manual"   -> use Manual_Regime
        "detected" -> use detect_regime()
    """

    base_config = SimulationConfig()

    annual_return = float(test_case["Annual_Return"])
    annual_volatility = float(test_case["Annual_Volatility"])

    if regime_source == "manual":
        regime_name = str(test_case["Manual_Regime"])
    elif regime_source == "detected":
        regime_name = detect_regime(
            annual_return=annual_return,
            annual_volatility=annual_volatility,
        )
    else:
        raise ValueError(
            "regime_source must be either 'manual' or 'detected'."
        )

    rule_settings = RULE_CONFIGS[rule_label]

    config = clone_config(
        base_config,
        n_paths=N_PATHS,
        annual_return=annual_return,
        annual_volatility=annual_volatility,
        regime_name=regime_name,
        **rule_settings,
    )

    return config


def run_single_experiment(
    test_case: dict,
    regime_source: str,
    rule_label: str,
) -> dict:
    """
    Run one test-case/regime-source/rule experiment.
    """

    case_name = str(test_case["Case"])

    experiment_name = f"{case_name}__{regime_source}__{rule_label}"

    print("=" * 100)
    print(f"Running experiment: {experiment_name}")
    print("=" * 100)

    config = build_config(
        test_case=test_case,
        regime_source=regime_source,
        rule_label=rule_label,
    )

    engine = SimulationEngine(config)
    path_results_df = engine.run()

    detected_regime = detect_regime(
        annual_return=float(test_case["Annual_Return"]),
        annual_volatility=float(test_case["Annual_Volatility"]),
    )

    summary = {
        "Case": case_name,
        "Regime_Source": regime_source,
        "Manual_Regime": test_case["Manual_Regime"],
        "Detected_Regime": detected_regime,
        "Used_Regime": config.regime_name,
        "Annual_Return": float(test_case["Annual_Return"]),
        "Annual_Volatility": float(test_case["Annual_Volatility"]),
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


def run_regime_detection_test() -> pd.DataFrame:
    """
    Run the full manual-vs-detected regime test.
    """

    rows = []

    regime_sources = ["manual", "detected"]

    total_experiments = (
        len(TEST_CASES)
        * len(regime_sources)
        * len(RULE_ORDER)
    )

    print("")
    print("=" * 100)
    print("COVERED CALL SIMULATOR - REGIME DETECTION TEST")
    print("=" * 100)
    print(f"Paths per experiment: {N_PATHS}")
    print(f"Test cases:           {len(TEST_CASES)}")
    print(f"Regime sources:       {regime_sources}")
    print(f"Rules tested:         {RULE_ORDER}")
    print(f"Total experiments:    {total_experiments}")
    print("=" * 100)
    print("")

    experiment_count = 0

    for test_case in TEST_CASES:
        for regime_source in regime_sources:
            for rule_label in RULE_ORDER:
                experiment_count += 1

                print(
                    f"Progress: {experiment_count} of {total_experiments}"
                )

                summary = run_single_experiment(
                    test_case=test_case,
                    regime_source=regime_source,
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
        ["Case", "Regime_Source", "Rule_Label"]
    ).reset_index(drop=True)

    return summary_df


# =============================================================================
# Analysis and report
# =============================================================================

def find_best_rule(group_df: pd.DataFrame) -> pd.Series | None:
    """
    Find best rule in one group.
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
    Compare manual and detected regime results by case.
    """

    rows = []

    for case_name in sorted(summary_df["Case"].astype(str).unique()):
        case_df = summary_df[
            summary_df["Case"].astype(str) == case_name
        ].copy()

        manual_df = case_df[case_df["Regime_Source"] == "manual"]
        detected_df = case_df[case_df["Regime_Source"] == "detected"]

        manual_best = find_best_rule(manual_df)
        detected_best = find_best_rule(detected_df)

        if manual_best is None or detected_best is None:
            continue

        manual_rule = str(manual_best["Rule_Label"])
        detected_rule = str(detected_best["Rule_Label"])

        outperformance_diff = (
            float(detected_best["Mean_Outperformance"])
            - float(manual_best["Mean_Outperformance"])
        )

        regime_changed = (
            str(manual_best["Manual_Regime"])
            != str(detected_best["Detected_Regime"])
        )

        rule_changed = manual_rule != detected_rule

        material_difference = (
            abs(outperformance_diff) >= MATERIALITY_THRESHOLD
        )

        rows.append(
            {
                "Case": case_name,
                "Manual_Regime": manual_best["Manual_Regime"],
                "Detected_Regime": detected_best["Detected_Regime"],
                "Regime_Changed": regime_changed,
                "Manual_Best_Rule": manual_rule,
                "Detected_Best_Rule": detected_rule,
                "Rule_Changed": rule_changed,
                "Manual_Best_Outperformance": manual_best[
                    "Mean_Outperformance"
                ],
                "Detected_Best_Outperformance": detected_best[
                    "Mean_Outperformance"
                ],
                "Detected_Minus_Manual_Outperformance": outperformance_diff,
                "Material_Difference": material_difference,
            }
        )

    return pd.DataFrame(rows)


def build_report(
    summary_df: pd.DataFrame,
    comparison_df: pd.DataFrame,
) -> str:
    """
    Build a plain-text regime detection test report.
    """

    lines = []

    lines.append("COVERED CALL SIMULATOR - REGIME DETECTION TEST REPORT")
    lines.append("=" * 100)
    lines.append("")
    lines.append(f"Paths per experiment:       {N_PATHS}")
    lines.append(f"Materiality threshold:      {MATERIALITY_THRESHOLD:.4f}")
    lines.append(f"Summary file:               {SUMMARY_PATH}")
    lines.append("")
    lines.append(
        "This test compares manually assigned regimes with automatically "
        "detected regimes."
    )
    lines.append("")
    lines.append(
        "The purpose is to decide whether the regime detector can be used "
        "inside future adaptive-rule simulations without changing the "
        "strategy recommendation unexpectedly."
    )
    lines.append("")

    lines.append("-" * 100)
    lines.append("Case comparison")
    lines.append("-" * 100)
    lines.append("")

    for _, row in comparison_df.iterrows():
        lines.append(f"Case: {row['Case']}")
        lines.append(f"    Manual regime:        {row['Manual_Regime']}")
        lines.append(f"    Detected regime:      {row['Detected_Regime']}")
        lines.append(f"    Regime changed:       {row['Regime_Changed']}")
        lines.append(f"    Manual best rule:     {row['Manual_Best_Rule']}")
        lines.append(f"    Detected best rule:   {row['Detected_Best_Rule']}")
        lines.append(f"    Rule changed:         {row['Rule_Changed']}")
        lines.append(
            "    Manual outperf:       "
            f"{format_decimal(row['Manual_Best_Outperformance'])}"
        )
        lines.append(
            "    Detected outperf:     "
            f"{format_decimal(row['Detected_Best_Outperformance'])}"
        )
        lines.append(
            "    Detected - manual:    "
            f"{format_decimal(row['Detected_Minus_Manual_Outperformance'])}"
        )
        lines.append(f"    Material difference:  {row['Material_Difference']}")
        lines.append("")

    lines.append("-" * 100)
    lines.append("Detailed results")
    lines.append("-" * 100)
    lines.append("")

    for case_name in sorted(summary_df["Case"].astype(str).unique()):
        lines.append(f"Case: {case_name}")
        lines.append("-" * 100)

        case_df = summary_df[
            summary_df["Case"].astype(str) == case_name
        ].copy()

        for regime_source in ["manual", "detected"]:
            source_df = case_df[
                case_df["Regime_Source"] == regime_source
            ].copy()

            if source_df.empty:
                continue

            used_regime = source_df.iloc[0]["Used_Regime"]

            lines.append(f"    Regime source: {regime_source}")
            lines.append(f"    Used regime:   {used_regime}")

            for _, row in source_df.iterrows():
                lines.append(
                    f"        {str(row['Rule_Label']):<28} | "
                    f"Outperf={format_decimal(row['Mean_Outperformance'])} | "
                    f"Net option={format_currency(row['Mean_Net_Option_Effect'])} | "
                    f"Cost={format_currency(row['Mean_Total_Transaction_Cost'])} | "
                    f"Cycles={format_decimal(row['Mean_Option_Cycles'], 2)}"
                )

            lines.append("")

    material_count = int(
        comparison_df["Material_Difference"].fillna(False).sum()
    )

    rule_change_count = int(
        comparison_df["Rule_Changed"].fillna(False).sum()
    )

    regime_change_count = int(
        comparison_df["Regime_Changed"].fillna(False).sum()
    )

    lines.append("=" * 100)
    lines.append("Overall conclusion")
    lines.append("=" * 100)
    lines.append("")
    lines.append(f"Cases tested:                 {len(comparison_df)}")
    lines.append(f"Cases where regime changed:   {regime_change_count}")
    lines.append(f"Cases where best rule changed:{rule_change_count}")
    lines.append(f"Material differences:         {material_count}")
    lines.append("")

    if material_count == 0:
        lines.append(
            "No material performance difference was detected between manually "
            "assigned regimes and automatically detected regimes."
        )
        lines.append("")
        lines.append(
            "This supports using the rule-based regime detector as a future "
            "input to adaptive-rule testing."
        )
    else:
        lines.append(
            "At least one material difference was detected. Review those cases "
            "before connecting regime detection to the main simulator."
        )

    lines.append("")
    lines.append(
        "Recommendation: keep regime detection as a standalone diagnostic for "
        "now. Do not wire it into app/main.py until the logic has been tested "
        "against more examples or historical data."
    )

    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)

    summary_df = run_regime_detection_test()
    comparison_df = build_case_comparison(summary_df)

    summary_df.to_csv(SUMMARY_PATH, index=False)

    report_text = build_report(
        summary_df=summary_df,
        comparison_df=comparison_df,
    )

    REPORT_PATH.write_text(report_text, encoding="utf-8")

    print("")
    print("=" * 100)
    print("Regime detection test complete.")
    print("=" * 100)
    print("")
    print("Saved files:")
    print(f"  {SUMMARY_PATH}")
    print(f"  {REPORT_PATH}")
    print("")
    print("Done.")
    print("")


if __name__ == "__main__":
    main()