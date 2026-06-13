"""
phase2_v0_comparison_adapter.py

Standalone Phase 2 comparison adapter for the Covered Call Strategy Stress Test.

This module compares the existing v0.1 paid-simulator scenario output with the
new Phase 2 scenario-payoff scaffold output. It is intentionally add-only and
safe: it does not modify the Streamlit dashboard, the v0.1 simulator engine, or
any config files.

Inputs
------
outputs/tables/paid_simulator/scenario_comparison.csv
outputs/tables/paid_simulator/scenario_payoff_report_scaffold.csv

Outputs
-------
outputs/tables/paid_simulator/phase2_v0_comparison_scaffold.csv
outputs/reports/paid_simulator/phase2_v0_comparison_scaffold.html
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

V0_SCENARIO_CSV = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_comparison.csv"
PHASE2_REPORT_CSV = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_payoff_report_scaffold.csv"
OUTPUT_CSV = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase2_v0_comparison_scaffold.csv"
OUTPUT_HTML = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2_v0_comparison_scaffold.html"


SCENARIO_CANDIDATES = [
    "scenario_display_name",
    "scenario_name",
    "scenario",
    "market_path",
    "path",
    "scenario_label",
    "label",
    "name",
    "Scenario",
]

RELATIVE_RESULT_CANDIDATES = [
    "covered_call_minus_buy_hold",
    "covered_call_minus_buy_and_hold",
    "relative_result",
    "relative_p_l",
    "relative_pl",
    "relative_pnl",
    "outperformance",
    "covered_call_outperformance",
    "net_option_effect",
    "Relative result",
]

RETURN_CANDIDATES = [
    "scenario_total_simple_return_percent",
    "modeled_return_percent",
    "realized_path_return_percent",
    "Modeled return",
    "Scenario return",
]


@dataclass(frozen=True)
class ComparisonStatus:
    input_v0_exists: bool
    input_phase2_exists: bool
    output_csv: Path
    output_html: Path
    row_count: int
    message: str


def normalize_column_name(name: Any) -> str:
    return str(name).strip().lower().replace(" ", "_").replace("-", "_").replace("/", "_")


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


def scenario_key(value: Any) -> str:
    text = str(value).strip().lower()
    replacements = {
        "&": "and",
        "-": " ",
        "_": " ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return " ".join(text.split())


def signed_currency(value: Any) -> str:
    try:
        number = float(value)
    except Exception:
        return str(value)
    sign = "+" if number >= 0 else "-"
    return f"{sign}${abs(number):,.2f}"


def read_v0_summary() -> pd.DataFrame:
    df = pd.read_csv(V0_SCENARIO_CSV)
    scenario_col = find_column(df, SCENARIO_CANDIDATES)
    relative_col = find_column(df, RELATIVE_RESULT_CANDIDATES)
    return_col = find_column(df, RETURN_CANDIDATES)

    if scenario_col is None:
        raise ValueError("Could not identify the scenario column in v0 scenario_comparison.csv.")
    if relative_col is None:
        raise ValueError("Could not identify the v0 relative-result column in scenario_comparison.csv.")

    out = pd.DataFrame()
    out["scenario_key"] = df[scenario_col].map(scenario_key)
    out["scenario"] = df[scenario_col].astype(str)
    out["v0_relative_result"] = pd.to_numeric(df[relative_col], errors="coerce")
    if return_col is not None:
        out["v0_modeled_return"] = df[return_col]
    else:
        out["v0_modeled_return"] = ""
    return out


def read_phase2_summary() -> pd.DataFrame:
    df = pd.read_csv(PHASE2_REPORT_CSV)
    scenario_col = find_column(df, SCENARIO_CANDIDATES)
    relative_col = find_column(df, RELATIVE_RESULT_CANDIDATES)
    return_col = find_column(df, RETURN_CANDIDATES)

    if scenario_col is None:
        raise ValueError("Could not identify the scenario column in Phase 2 scenario_payoff_report_scaffold.csv.")
    if relative_col is None:
        raise ValueError("Could not identify the Phase 2 relative-result column in scenario_payoff_report_scaffold.csv.")

    out = pd.DataFrame()
    out["scenario_key"] = df[scenario_col].map(scenario_key)
    out["phase2_scenario"] = df[scenario_col].astype(str)
    out["phase2_relative_result"] = pd.to_numeric(df[relative_col], errors="coerce")
    if return_col is not None:
        out["phase2_modeled_return"] = df[return_col]
    else:
        out["phase2_modeled_return"] = ""
    return out


def build_interpretation(row: pd.Series) -> str:
    v0_value = row.get("v0_relative_result")
    p2_value = row.get("phase2_relative_result")

    if pd.isna(v0_value) and pd.isna(p2_value):
        return "No comparable relative-result values were available."
    if pd.isna(v0_value):
        return "Scenario exists in Phase 2 output but was not matched to v0 output."
    if pd.isna(p2_value):
        return "Scenario exists in v0 output but was not matched to Phase 2 output."

    diff = float(p2_value) - float(v0_value)
    if abs(diff) < 1e-6:
        return "Phase 2 scaffold matches the v0 relative result for this scenario."
    if diff > 0:
        return "Phase 2 scaffold is more favorable to the covered call than the v0 output for this scenario."
    return "Phase 2 scaffold is less favorable to the covered call than the v0 output for this scenario."


def build_phase2_v0_comparison() -> pd.DataFrame:
    v0 = read_v0_summary()
    p2 = read_phase2_summary()

    merged = pd.merge(v0, p2, on="scenario_key", how="outer")
    merged["scenario"] = merged["scenario"].fillna(merged["phase2_scenario"])
    merged["relative_result_difference_phase2_minus_v0"] = (
        pd.to_numeric(merged["phase2_relative_result"], errors="coerce")
        - pd.to_numeric(merged["v0_relative_result"], errors="coerce")
    )
    merged["interpretation"] = merged.apply(build_interpretation, axis=1)

    columns = [
        "scenario",
        "v0_modeled_return",
        "phase2_modeled_return",
        "v0_relative_result",
        "phase2_relative_result",
        "relative_result_difference_phase2_minus_v0",
        "interpretation",
    ]
    return merged[columns].sort_values("scenario").reset_index(drop=True)


def write_html_report(df: pd.DataFrame) -> None:
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)

    display_df = df.copy()
    for col in ["v0_relative_result", "phase2_relative_result", "relative_result_difference_phase2_minus_v0"]:
        if col in display_df.columns:
            display_df[col] = display_df[col].map(lambda value: signed_currency(value) if pd.notna(value) else "")

    html_table = display_df.to_html(index=False, escape=True)
    html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>Phase 2 vs v0 Comparison Scaffold</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 36px; color: #111827; }}
    h1 {{ margin-bottom: 0.2rem; }}
    .subtitle {{ color: #4b5563; margin-bottom: 1.5rem; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 0.92rem; }}
    th, td {{ border: 1px solid #d1d5db; padding: 8px 10px; vertical-align: top; }}
    th {{ background: #f3f4f6; text-align: left; }}
    .note {{ background: #eff6ff; border: 1px solid #bfdbfe; padding: 12px 14px; border-radius: 8px; margin: 1rem 0; }}
  </style>
</head>
<body>
  <h1>Phase 2 vs v0 Comparison Scaffold</h1>
  <div class=\"subtitle\">Compares the existing v0.1 paid-simulator scenario output with the Phase 2 scenario-payoff scaffold.</div>
  <div class=\"note\">
    This is a development comparison report. It is not yet the customer-facing simulator output.
    Its purpose is to show where the Phase 2 scaffold agrees with or differs from the current v0.1 output.
  </div>
  {html_table}
</body>
</html>
"""
    OUTPUT_HTML.write_text(html, encoding="utf-8")


def run_adapter() -> ComparisonStatus:
    if not V0_SCENARIO_CSV.exists():
        return ComparisonStatus(False, PHASE2_REPORT_CSV.exists(), OUTPUT_CSV, OUTPUT_HTML, 0, f"Missing v0 input: {V0_SCENARIO_CSV}")
    if not PHASE2_REPORT_CSV.exists():
        return ComparisonStatus(V0_SCENARIO_CSV.exists(), False, OUTPUT_CSV, OUTPUT_HTML, 0, f"Missing Phase 2 input: {PHASE2_REPORT_CSV}")

    df = build_phase2_v0_comparison()
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    write_html_report(df)

    return ComparisonStatus(True, True, OUTPUT_CSV, OUTPUT_HTML, len(df), "Phase 2 vs v0 comparison report created.")


if __name__ == "__main__":
    result = run_adapter()
    print(result.message)
    print(f"Rows: {result.row_count}")
    print(f"CSV:  {result.output_csv}")
    print(f"HTML: {result.output_html}")
