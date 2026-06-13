"""
regime_detection.py

Simple rule-based regime detection for the Covered Call Simulator.

This script classifies a market regime from annual return and annual volatility.

It is intentionally simple. The goal is to create a first regime-detection
module that matches the current simulator structure.

Current possible regimes:

    baseline
    sideways_market
    bullish_market
    bearish_market
    high_volatility
    low_volatility

This script does not modify app/main.py.
It is a standalone diagnostic script.

Important revision:
    The first borderline test showed that the original thresholds were too
    sharp near two boundaries:

        annual_return = -0.029
        annual_return = +0.030

    The detector switched out of bearish_market too quickly and classified a
    mildly positive market as sideways_market too easily.

    Therefore, the thresholds have been revised to:

        BEARISH_RETURN_THRESHOLD = -0.020
        SIDEWAYS_ABS_RETURN_THRESHOLD = 0.020

    This makes the detector more conservative near boundaries.

Outputs:

    outputs/tables/comparison/regime_detection_examples.csv
    outputs/tables/comparison/regime_detection_report.txt
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

EXAMPLES_PATH = OUTPUT_TABLE_DIR / "regime_detection_examples.csv"
REPORT_PATH = OUTPUT_TABLE_DIR / "regime_detection_report.txt"


# =============================================================================
# Regime detection thresholds
# =============================================================================

# These are first-pass thresholds.
# They can be tuned later using historical data or simulator performance.
#
# Revised after the borderline regime-detection test:
#
# Original:
#     BEARISH_RETURN_THRESHOLD = -0.030
#     SIDEWAYS_ABS_RETURN_THRESHOLD = 0.030
#
# Revised:
#     BEARISH_RETURN_THRESHOLD = -0.020
#     SIDEWAYS_ABS_RETURN_THRESHOLD = 0.020
#
# Reason:
#     The -0.029 case behaved more like bearish_market for covered-call
#     management.
#
#     The +0.030 case behaved more like baseline than sideways_market for
#     covered-call management.

BEARISH_RETURN_THRESHOLD = -0.020
SIDEWAYS_ABS_RETURN_THRESHOLD = 0.020
BULLISH_RETURN_THRESHOLD = 0.120

LOW_VOLATILITY_THRESHOLD = 0.150
SIDEWAYS_VOLATILITY_MAX = 0.220
BULLISH_VOLATILITY_MAX = 0.350
HIGH_VOLATILITY_THRESHOLD = 0.400


# =============================================================================
# Example cases
# =============================================================================

EXAMPLE_CASES = [
    {
        "Case": "Flat low-volatility market",
        "Annual_Return": 0.00,
        "Annual_Volatility": 0.12,
    },
    {
        "Case": "Flat moderate-volatility market",
        "Annual_Return": 0.01,
        "Annual_Volatility": 0.18,
    },
    {
        "Case": "Normal baseline market",
        "Annual_Return": 0.08,
        "Annual_Volatility": 0.25,
    },
    {
        "Case": "Strong bullish market",
        "Annual_Return": 0.18,
        "Annual_Volatility": 0.22,
    },
    {
        "Case": "Bearish market",
        "Annual_Return": -0.10,
        "Annual_Volatility": 0.28,
    },
    {
        "Case": "High-volatility market",
        "Annual_Return": 0.06,
        "Annual_Volatility": 0.45,
    },
    {
        "Case": "Low-volatility upward market",
        "Annual_Return": 0.06,
        "Annual_Volatility": 0.12,
    },
    {
        "Case": "Leveraged ETF style",
        "Annual_Return": 0.15,
        "Annual_Volatility": 0.55,
    },
    {
        "Case": "Negative high-volatility market",
        "Annual_Return": -0.08,
        "Annual_Volatility": 0.48,
    },
    {
        "Case": "Mildly negative borderline market",
        "Annual_Return": -0.029,
        "Annual_Volatility": 0.25,
    },
    {
        "Case": "Mildly positive borderline market",
        "Annual_Return": 0.030,
        "Annual_Volatility": 0.18,
    },
]


# =============================================================================
# Regime detection logic
# =============================================================================

def detect_regime(
    annual_return: float,
    annual_volatility: float,
) -> str:
    """
    Classify the market regime from annual return and annual volatility.

    Parameters
    ----------
    annual_return:
        Expected or estimated annual return, expressed as a decimal.
        Example: 0.08 means +8%.

    annual_volatility:
        Expected or estimated annual volatility, expressed as a decimal.
        Example: 0.25 means 25%.

    Returns
    -------
    str
        One of the simulator regime names.
    """

    if annual_return <= BEARISH_RETURN_THRESHOLD:
        return "bearish_market"

    if annual_volatility >= HIGH_VOLATILITY_THRESHOLD:
        return "high_volatility"

    if (
        abs(annual_return) <= SIDEWAYS_ABS_RETURN_THRESHOLD
        and annual_volatility <= SIDEWAYS_VOLATILITY_MAX
    ):
        return "sideways_market"

    if (
        annual_return >= BULLISH_RETURN_THRESHOLD
        and annual_volatility <= BULLISH_VOLATILITY_MAX
    ):
        return "bullish_market"

    if annual_volatility <= LOW_VOLATILITY_THRESHOLD:
        return "low_volatility"

    return "baseline"


def explain_regime(
    annual_return: float,
    annual_volatility: float,
    regime_name: str,
) -> str:
    """
    Return a plain-English explanation for a regime classification.
    """

    if regime_name == "bearish_market":
        return (
            "Annual return is below the revised bearish threshold, so the "
            "market is classified as bearish. This is intentionally conservative "
            "near mildly negative returns."
        )

    if regime_name == "high_volatility":
        return (
            "Annual volatility is above the high-volatility threshold, so the "
            "market is classified as high_volatility."
        )

    if regime_name == "sideways_market":
        return (
            "Annual return is very near zero and volatility is not high, so the "
            "market is classified as sideways_market."
        )

    if regime_name == "bullish_market":
        return (
            "Annual return is strong and volatility is not excessive, so the "
            "market is classified as bullish_market."
        )

    if regime_name == "low_volatility":
        return (
            "Annual volatility is very low and the market is not bearish or "
            "sideways, so the market is classified as low_volatility."
        )

    return (
        "The return and volatility values do not trigger a special regime, "
        "so the market is classified as baseline."
    )


# =============================================================================
# Build examples and report
# =============================================================================

def build_examples_table() -> pd.DataFrame:
    """
    Build a table of example regime classifications.
    """

    rows = []

    for case in EXAMPLE_CASES:
        annual_return = float(case["Annual_Return"])
        annual_volatility = float(case["Annual_Volatility"])

        regime_name = detect_regime(
            annual_return=annual_return,
            annual_volatility=annual_volatility,
        )

        explanation = explain_regime(
            annual_return=annual_return,
            annual_volatility=annual_volatility,
            regime_name=regime_name,
        )

        rows.append(
            {
                "Case": case["Case"],
                "Annual_Return": annual_return,
                "Annual_Volatility": annual_volatility,
                "Detected_Regime": regime_name,
                "Explanation": explanation,
            }
        )

    return pd.DataFrame(rows)


def build_report(examples_df: pd.DataFrame) -> str:
    """
    Build a plain-text regime detection report.
    """

    lines = []

    lines.append("COVERED CALL SIMULATOR - REGIME DETECTION REPORT")
    lines.append("=" * 100)
    lines.append("")
    lines.append("This is a first-pass rule-based regime detector.")
    lines.append("")
    lines.append("Inputs:")
    lines.append("    annual_return")
    lines.append("    annual_volatility")
    lines.append("")
    lines.append("Possible outputs:")
    lines.append("    baseline")
    lines.append("    sideways_market")
    lines.append("    bullish_market")
    lines.append("    bearish_market")
    lines.append("    high_volatility")
    lines.append("    low_volatility")
    lines.append("")

    lines.append("-" * 100)
    lines.append("Thresholds")
    lines.append("-" * 100)
    lines.append("")
    lines.append(f"bearish return threshold:        {BEARISH_RETURN_THRESHOLD:.4f}")
    lines.append(f"sideways abs return threshold:   {SIDEWAYS_ABS_RETURN_THRESHOLD:.4f}")
    lines.append(f"bullish return threshold:        {BULLISH_RETURN_THRESHOLD:.4f}")
    lines.append(f"low volatility threshold:        {LOW_VOLATILITY_THRESHOLD:.4f}")
    lines.append(f"sideways volatility max:         {SIDEWAYS_VOLATILITY_MAX:.4f}")
    lines.append(f"bullish volatility max:          {BULLISH_VOLATILITY_MAX:.4f}")
    lines.append(f"high volatility threshold:       {HIGH_VOLATILITY_THRESHOLD:.4f}")
    lines.append("")

    lines.append("-" * 100)
    lines.append("Threshold revision note")
    lines.append("-" * 100)
    lines.append("")
    lines.append("The bearish and sideways return thresholds were revised after the")
    lines.append("borderline regime-detection test.")
    lines.append("")
    lines.append("Original values:")
    lines.append("    bearish return threshold:       -0.0300")
    lines.append("    sideways abs return threshold:   0.0300")
    lines.append("")
    lines.append("Revised values:")
    lines.append(f"    bearish return threshold:       {BEARISH_RETURN_THRESHOLD:.4f}")
    lines.append(f"    sideways abs return threshold:  {SIDEWAYS_ABS_RETURN_THRESHOLD:.4f}")
    lines.append("")
    lines.append("Reason:")
    lines.append("    The annual_return = -0.029 case behaved more like bearish_market")
    lines.append("    for covered-call management.")
    lines.append("")
    lines.append("    The annual_return = +0.030 case behaved more like baseline than")
    lines.append("    sideways_market for covered-call management.")
    lines.append("")

    lines.append("-" * 100)
    lines.append("Rule order")
    lines.append("-" * 100)
    lines.append("")
    lines.append("1. If annual_return <= bearish threshold:")
    lines.append("       bearish_market")
    lines.append("")
    lines.append("2. Else if annual_volatility >= high-volatility threshold:")
    lines.append("       high_volatility")
    lines.append("")
    lines.append("3. Else if return is very near zero and volatility is not high:")
    lines.append("       sideways_market")
    lines.append("")
    lines.append("4. Else if return is strongly positive and volatility is not excessive:")
    lines.append("       bullish_market")
    lines.append("")
    lines.append("5. Else if volatility is very low:")
    lines.append("       low_volatility")
    lines.append("")
    lines.append("6. Otherwise:")
    lines.append("       baseline")
    lines.append("")

    lines.append("-" * 100)
    lines.append("Example classifications")
    lines.append("-" * 100)
    lines.append("")

    for _, row in examples_df.iterrows():
        lines.append(f"Case: {row['Case']}")
        lines.append(f"    annual_return:      {row['Annual_Return']:.4f}")
        lines.append(f"    annual_volatility:  {row['Annual_Volatility']:.4f}")
        lines.append(f"    detected_regime:    {row['Detected_Regime']}")
        lines.append(f"    explanation:        {row['Explanation']}")
        lines.append("")

    lines.append("=" * 100)
    lines.append("Interpretation")
    lines.append("=" * 100)
    lines.append("")
    lines.append(
        "This regime detector is intentionally simple. It is not yet a "
        "statistical classifier and does not yet use realized price data."
    )
    lines.append("")
    lines.append(
        "The purpose is to create a clean first version that can later be "
        "connected to the adaptive covered-call rule."
    )
    lines.append("")
    lines.append(
        "The rule order matters. Bearish markets are classified first because "
        "a negative return environment should trigger the defensive covered-call "
        "logic even if volatility is also high."
    )
    lines.append("")
    lines.append(
        "High volatility is checked before bullish and baseline classifications "
        "because very high volatility can dominate the strategy behavior."
    )
    lines.append("")
    lines.append(
        "The revised thresholds are more conservative near mildly negative "
        "markets and less likely to classify mildly positive markets as sideways."
    )
    lines.append("")
    lines.append(
        "Future improvements can replace these fixed thresholds with historical "
        "estimates, rolling returns, realized volatility, trend filters, or "
        "machine-learning regime classification."
    )

    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)

    examples_df = build_examples_table()
    examples_df.to_csv(EXAMPLES_PATH, index=False)

    report_text = build_report(examples_df)
    REPORT_PATH.write_text(report_text, encoding="utf-8")

    print("")
    print("=" * 100)
    print("Regime detection diagnostic complete.")
    print("=" * 100)
    print("")
    print("Saved files:")
    print(f"  {EXAMPLES_PATH}")
    print(f"  {REPORT_PATH}")
    print("")
    print("Done.")
    print("")


if __name__ == "__main__":
    main()