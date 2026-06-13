"""
premium_vs_scaffold_comparison.py

Phase 2B comparison adapter for the Covered Call Strategy Stress Test.

This module compares the older Phase 2 payoff scaffold output against the
newer premium-aware payoff scaffold output. It is intentionally standalone and
add-only: it does not replace the v0.1 dashboard or the existing Phase 2 files.

Inputs
------
outputs/tables/paid_simulator/scenario_payoff_scaffold.csv
outputs/tables/paid_simulator/premium_aware_payoff_scaffold.csv

Outputs
-------
outputs/tables/paid_simulator/premium_vs_scaffold_comparison.csv
outputs/reports/paid_simulator/premium_vs_scaffold_comparison.html
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

OLD_PAYOFF_PATH = TABLE_DIR / "scenario_payoff_scaffold.csv"
PREMIUM_AWARE_PATH = TABLE_DIR / "premium_aware_payoff_scaffold.csv"
COMPARISON_CSV_PATH = TABLE_DIR / "premium_vs_scaffold_comparison.csv"
COMPARISON_HTML_PATH = REPORT_DIR / "premium_vs_scaffold_comparison.html"

SCENARIO_CANDIDATES = [
    "scenario_name",
    "scenario",
    "Scenario",
    "scenario_display_name",
    "display_name",
    "market_path",
    "path",
    "name",
]

RELATIVE_RESULT_CANDIDATES = [
    "covered_call_minus_buy_hold",
    "covered_call_minus_buy_and_hold",
    "covered_call_minus_buy_hold_p_l",
    "covered_call_minus_buy_hold_pl",
    "relative_result",
    "relative_p_l",
    "relative_pl",
    "relative_pnl",
    "Relative result",
    "Relative Result",
    "outperformance",
    "net_option_effect",
]

PREMIUM_CANDIDATES = [
    "estimated_call_premium",
    "call_premium",
    "premium_per_share",
    "premium",
    "selected_call_premium",
]

STRIKE_CANDIDATES = [
    "estimated_call_strike",
    "call_strike",
    "strike",
    "selected_strike",
]

DELTA_CANDIDATES = [
    "estimated_call_delta",
    "call_delta",
    "delta",
    "selected_delta",
]

IV_CANDIDATES = [
    "implied_volatility",
    "scenario_implied_volatility",
    "iv",
    "estimated_iv",
]


@dataclass(frozen=True)
class ComparisonResult:
    csv_path: Path
    html_path: Path
    row_count: int
    premium_better_count: int
    premium_worse_count: int
    premium_same_count: int


def normalize_column_name(name: Any) -> str:
    return str(name).strip().lower().replace(" ", "_").replace("-", "_")


def normalize_scenario_name(name: Any) -> str:
    return normalize_column_name(name)


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    normalized = {normalize_column_name(col): col for col in df.columns}
    for candidate in candidates:
        key = normalize_column_name(candidate)
        if key in normalized:
            return normalized[key]
    for col in df.columns:
        norm = normalize_column_name(col)
        for candidate in candidates:
            if normalize_column_name(candidate) in norm:
                return col
    return None


def format_currency(value: Any) -> str:
    try:
        number = float(value)
        sign = "+" if number >= 0 else "-"
        return f"{sign}${abs(number):,.2f}"
    except Exception:
        return str(value)


def load_input_tables(
    old_path: Path = OLD_PAYOFF_PATH,
    premium_path: Path = PREMIUM_AWARE_PATH,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not old_path.exists():
        raise FileNotFoundError(f"Old Phase 2 payoff scaffold file not found: {old_path}")
    if not premium_path.exists():
        raise FileNotFoundError(f"Premium-aware payoff scaffold file not found: {premium_path}")

    old_df = pd.read_csv(old_path)
    premium_df = pd.read_csv(premium_path)

    if old_df.empty:
        raise ValueError(f"Old Phase 2 payoff scaffold file is empty: {old_path}")
    if premium_df.empty:
        raise ValueError(f"Premium-aware payoff scaffold file is empty: {premium_path}")

    return old_df, premium_df


def prepare_comparison_frame(old_df: pd.DataFrame, premium_df: pd.DataFrame) -> pd.DataFrame:
    old_scenario_col = find_column(old_df, SCENARIO_CANDIDATES)
    premium_scenario_col = find_column(premium_df, SCENARIO_CANDIDATES)
    old_relative_col = find_column(old_df, RELATIVE_RESULT_CANDIDATES)
    premium_relative_col = find_column(premium_df, RELATIVE_RESULT_CANDIDATES)

    missing: list[str] = []
    if old_scenario_col is None:
        missing.append("scenario column in old Phase 2 payoff scaffold")
    if premium_scenario_col is None:
        missing.append("scenario column in premium-aware payoff scaffold")
    if old_relative_col is None:
        missing.append("relative-result column in old Phase 2 payoff scaffold")
    if premium_relative_col is None:
        missing.append("relative-result column in premium-aware payoff scaffold")
    if missing:
        raise ValueError("Could not detect required columns: " + ", ".join(missing))

    old_work = pd.DataFrame(
        {
            "scenario_key": old_df[old_scenario_col].map(normalize_scenario_name),
            "scenario_old_label": old_df[old_scenario_col].astype(str),
            "old_phase2_relative_result": pd.to_numeric(old_df[old_relative_col], errors="coerce"),
        }
    )

    premium_work = pd.DataFrame(
        {
            "scenario_key": premium_df[premium_scenario_col].map(normalize_scenario_name),
            "scenario_premium_label": premium_df[premium_scenario_col].astype(str),
            "premium_aware_relative_result": pd.to_numeric(premium_df[premium_relative_col], errors="coerce"),
        }
    )

    optional_columns = {
        "estimated_call_premium": find_column(premium_df, PREMIUM_CANDIDATES),
        "estimated_call_strike": find_column(premium_df, STRIKE_CANDIDATES),
        "estimated_call_delta": find_column(premium_df, DELTA_CANDIDATES),
        "estimated_implied_volatility": find_column(premium_df, IV_CANDIDATES),
    }
    for output_name, source_col in optional_columns.items():
        if source_col is not None:
            premium_work[output_name] = premium_df[source_col]

    merged = old_work.merge(premium_work, on="scenario_key", how="outer")
    merged["scenario"] = merged["scenario_premium_label"].fillna(merged["scenario_old_label"]).fillna(merged["scenario_key"])
    merged["premium_minus_old"] = merged["premium_aware_relative_result"] - merged["old_phase2_relative_result"]

    def classify(row: pd.Series) -> str:
        diff = row.get("premium_minus_old")
        if pd.isna(diff):
            return "Incomplete comparison"
        if abs(float(diff)) < 0.01:
            return "No material change"
        if float(diff) > 0:
            return "Premium-aware model improves relative result"
        return "Premium-aware model reduces relative result"

    def interpretation(row: pd.Series) -> str:
        diff = row.get("premium_minus_old")
        scenario = row.get("scenario", "scenario")
        if pd.isna(diff):
            return f"The {scenario} row could not be fully compared because one model output is missing."
        diff_text = format_currency(diff)
        if abs(float(diff)) < 0.01:
            return f"For {scenario}, the premium-aware payoff is effectively unchanged versus the older Phase 2 scaffold."
        if float(diff) > 0:
            return f"For {scenario}, the premium-aware payoff is {diff_text} higher than the older Phase 2 scaffold."
        return f"For {scenario}, the premium-aware payoff is {diff_text} lower than the older Phase 2 scaffold."

    merged["comparison_classification"] = merged.apply(classify, axis=1)
    merged["plain_english_interpretation"] = merged.apply(interpretation, axis=1)

    ordered_columns = [
        "scenario",
        "old_phase2_relative_result",
        "premium_aware_relative_result",
        "premium_minus_old",
        "comparison_classification",
        "plain_english_interpretation",
        "estimated_call_premium",
        "estimated_call_strike",
        "estimated_call_delta",
        "estimated_implied_volatility",
        "scenario_key",
    ]
    keep_columns = [col for col in ordered_columns if col in merged.columns]
    output = merged[keep_columns].sort_values("scenario").reset_index(drop=True)
    return output


def write_html_report(comparison_df: pd.DataFrame, html_path: Path = COMPARISON_HTML_PATH) -> None:
    html_path.parent.mkdir(parents=True, exist_ok=True)

    diff_values = pd.to_numeric(comparison_df.get("premium_minus_old"), errors="coerce")
    valid_diffs = diff_values.dropna()
    avg_diff = valid_diffs.mean() if not valid_diffs.empty else float("nan")
    max_diff = valid_diffs.max() if not valid_diffs.empty else float("nan")
    min_diff = valid_diffs.min() if not valid_diffs.empty else float("nan")

    summary_rows = [
        ("Scenarios compared", str(len(comparison_df))),
        ("Average premium-aware minus old", format_currency(avg_diff) if not pd.isna(avg_diff) else "Not available"),
        ("Largest improvement", format_currency(max_diff) if not pd.isna(max_diff) else "Not available"),
        ("Largest reduction", format_currency(min_diff) if not pd.isna(min_diff) else "Not available"),
    ]

    summary_html = "".join(f"<tr><th>{label}</th><td>{value}</td></tr>" for label, value in summary_rows)
    table_html = comparison_df.to_html(index=False, border=0, classes="comparison-table")

    html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>Premium-aware payoff comparison</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; color: #111827; }}
    h1, h2 {{ color: #111827; }}
    .note {{ background: #eef2ff; border-left: 4px solid #4f46e5; padding: 0.8rem 1rem; margin: 1rem 0; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
    th, td {{ border: 1px solid #e5e7eb; padding: 0.45rem 0.6rem; text-align: left; vertical-align: top; }}
    th {{ background: #f9fafb; }}
    .comparison-table td {{ font-size: 0.92rem; }}
  </style>
</head>
<body>
  <h1>Phase 2B Premium-Aware Payoff Comparison</h1>
  <div class=\"note\">
    This scaffold compares the older Phase 2 payoff output against the newer premium-aware payoff output.
    It is a model-development diagnostic, not a customer-facing recommendation.
  </div>
  <h2>Summary</h2>
  <table>{summary_html}</table>
  <h2>Scenario comparison</h2>
  {table_html}
</body>
</html>"""
    html_path.write_text(html, encoding="utf-8")


def build_premium_vs_scaffold_comparison(
    old_path: Path = OLD_PAYOFF_PATH,
    premium_path: Path = PREMIUM_AWARE_PATH,
    csv_path: Path = COMPARISON_CSV_PATH,
    html_path: Path = COMPARISON_HTML_PATH,
) -> ComparisonResult:
    old_df, premium_df = load_input_tables(old_path=old_path, premium_path=premium_path)
    comparison_df = prepare_comparison_frame(old_df=old_df, premium_df=premium_df)

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    comparison_df.to_csv(csv_path, index=False)
    write_html_report(comparison_df=comparison_df, html_path=html_path)

    diff_values = pd.to_numeric(comparison_df["premium_minus_old"], errors="coerce")
    premium_better_count = int((diff_values > 0.01).sum())
    premium_worse_count = int((diff_values < -0.01).sum())
    premium_same_count = int((diff_values.abs() <= 0.01).sum())

    return ComparisonResult(
        csv_path=csv_path,
        html_path=html_path,
        row_count=len(comparison_df),
        premium_better_count=premium_better_count,
        premium_worse_count=premium_worse_count,
        premium_same_count=premium_same_count,
    )


if __name__ == "__main__":
    result = build_premium_vs_scaffold_comparison()
    print(f"CSV written:  {result.csv_path}")
    print(f"HTML written: {result.html_path}")
    print(f"Rows:         {result.row_count}")
