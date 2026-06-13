"""
adjusted_premium_payoff_comparison.py

Phase 2E adjusted-premium payoff comparison scaffold for the Covered Call
Strategy Stress Test project.

This module compares the controlled adjusted-premium output against the
existing premium-aware payoff result. It does not overwrite any prior Phase 2B
or Phase 2E files. It writes a separate adjusted-payoff comparison so the effect
of the controlled premium adjustment can be inspected before any model change is
promoted into the main customer-facing workflow.

Inputs
------
outputs/tables/paid_simulator/scenario_price_paths_scaffold.csv
outputs/tables/paid_simulator/premium_model_adjusted_premiums.csv
outputs/tables/paid_simulator/premium_aware_payoff_scaffold.csv  optional context

Outputs
-------
outputs/tables/paid_simulator/adjusted_premium_payoff_comparison.csv
outputs/reports/paid_simulator/adjusted_premium_payoff_comparison.html
outputs/reports/paid_simulator/adjusted_premium_payoff_summary.txt
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

PRICE_PATHS_CSV = OUTPUT_TABLE_DIR / "scenario_price_paths_scaffold.csv"
ADJUSTED_PREMIUM_CSV = OUTPUT_TABLE_DIR / "premium_model_adjusted_premiums.csv"
PRIOR_PREMIUM_AWARE_PAYOFF_CSV = OUTPUT_TABLE_DIR / "premium_aware_payoff_scaffold.csv"

OUTPUT_CSV = OUTPUT_TABLE_DIR / "adjusted_premium_payoff_comparison.csv"
OUTPUT_HTML = OUTPUT_REPORT_DIR / "adjusted_premium_payoff_comparison.html"
OUTPUT_SUMMARY_TXT = OUTPUT_REPORT_DIR / "adjusted_premium_payoff_summary.txt"

DEFAULT_STARTING_PRICE = 545.25
DEFAULT_SHARES = 100

SCENARIO_COLUMNS = [
    "scenario_name",
    "scenario",
    "name",
    "Scenario",
    "scenario_display_name",
    "display_name",
    "market_path",
]
DISPLAY_COLUMNS = [
    "display_name",
    "scenario_display_name",
    "Scenario",
    "scenario",
    "scenario_name",
]
STEP_COLUMNS = ["step", "Step", "day", "Day", "path_step"]
PRICE_COLUMNS = [
    "price",
    "modeled_price",
    "stock_price",
    "underlying_price",
    "final_price",
    "Final price",
]
START_PRICE_COLUMNS = [
    "starting_price",
    "start_price",
    "initial_price",
    "Start price",
]

ADJUSTED_PREMIUM_COLUMNS = {
    "scenario": ["scenario_name", "scenario", "name"],
    "display_name": ["display_name", "scenario_display_name", "market_path", "scenario_label"],
    "strike": ["estimated_strike", "call_strike", "strike", "selected_strike", "strike_price"],
    "original_premium": ["original_call_premium", "call_premium", "estimated_call_premium", "premium"],
    "adjusted_premium": ["adjusted_call_premium", "call_premium_adjusted", "adjusted_premium"],
    "original_iv": ["original_implied_volatility", "implied_volatility", "estimated_iv", "iv"],
    "adjusted_iv": ["adjusted_implied_volatility", "adjusted_iv"],
    "iv_adjustment": ["iv_adjustment", "implied_volatility_adjustment"],
    "original_delta": ["original_call_delta", "estimated_call_delta", "call_delta", "delta"],
    "adjusted_delta": ["adjusted_call_delta", "call_delta_adjusted", "adjusted_delta"],
    "premium_change": ["premium_change", "adjusted_minus_original_premium"],
    "adjustment_status": ["adjustment_status", "status"],
    "adjustment_reason": ["adjustment_reason", "reason", "notes"],
}

PRIOR_PAYOFF_COLUMNS = {
    "scenario": ["scenario_name", "scenario", "name"],
    "prior_relative": [
        "covered_call_minus_buy_hold",
        "covered_call_minus_buy_and_hold",
        "relative_result",
        "premium_aware_relative_result",
    ],
    "prior_covered_call_pl": ["covered_call_pl", "covered_call_profit_loss"],
    "prior_call_premium": ["call_premium", "estimated_call_premium", "premium"],
}


@dataclass
class AdjustedPayoffRow:
    scenario_name: str
    scenario_display_name: str
    starting_price: float
    final_price: float
    modeled_return_percent: float
    call_strike: float
    original_call_premium: float
    adjusted_call_premium: float
    premium_change: float
    original_implied_volatility: float | None
    adjusted_implied_volatility: float | None
    iv_adjustment: float | None
    original_call_delta: float | None
    adjusted_call_delta: float | None
    buy_and_hold_pl: float
    original_model_covered_call_pl: float
    adjusted_model_covered_call_pl: float
    adjusted_covered_call_minus_buy_hold: float
    intrinsic_call_loss: float
    original_premium_income: float
    adjusted_premium_income: float
    adjusted_minus_original_model_pl: float
    prior_premium_aware_relative_result: float | None
    adjusted_minus_prior_relative_result: float | None
    assigned: bool
    adjustment_status: str
    interpretation: str
    adjustment_reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_name": self.scenario_name,
            "scenario_display_name": self.scenario_display_name,
            "starting_price": self.starting_price,
            "final_price": self.final_price,
            "modeled_return_percent": self.modeled_return_percent,
            "call_strike": self.call_strike,
            "original_call_premium": self.original_call_premium,
            "adjusted_call_premium": self.adjusted_call_premium,
            "premium_change": self.premium_change,
            "original_implied_volatility": self.original_implied_volatility,
            "adjusted_implied_volatility": self.adjusted_implied_volatility,
            "iv_adjustment": self.iv_adjustment,
            "original_call_delta": self.original_call_delta,
            "adjusted_call_delta": self.adjusted_call_delta,
            "buy_and_hold_pl": self.buy_and_hold_pl,
            "original_model_covered_call_pl": self.original_model_covered_call_pl,
            "adjusted_model_covered_call_pl": self.adjusted_model_covered_call_pl,
            "adjusted_covered_call_minus_buy_hold": self.adjusted_covered_call_minus_buy_hold,
            "intrinsic_call_loss": self.intrinsic_call_loss,
            "original_premium_income": self.original_premium_income,
            "adjusted_premium_income": self.adjusted_premium_income,
            "adjusted_minus_original_model_pl": self.adjusted_minus_original_model_pl,
            "prior_premium_aware_relative_result": self.prior_premium_aware_relative_result,
            "adjusted_minus_prior_relative_result": self.adjusted_minus_prior_relative_result,
            "assigned": self.assigned,
            "adjustment_status": self.adjustment_status,
            "interpretation": self.interpretation,
            "adjustment_reason": self.adjustment_reason,
        }


def normalize_column_name(value: Any) -> str:
    return "".join(ch.lower() for ch in str(value) if ch.isalnum())


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    normalized = {normalize_column_name(col): col for col in df.columns}
    for candidate in candidates:
        key = normalize_column_name(candidate)
        if key in normalized:
            return normalized[key]
    for col in df.columns:
        normalized_col = normalize_column_name(col)
        for candidate in candidates:
            candidate_key = normalize_column_name(candidate)
            if candidate_key and candidate_key in normalized_col:
                return col
    return None


def safe_float(value: Any, default: float | None = None) -> float | None:
    if value is None:
        return default
    try:
        if pd.isna(value):
            return default
    except TypeError:
        pass
    try:
        return float(str(value).replace("$", "").replace(",", "").replace("%", "").strip())
    except (TypeError, ValueError):
        return default


def scenario_key(value: Any) -> str:
    text = str(value or "").strip().lower()
    return text.replace(" ", "_").replace("-", "_") or "unknown"


def ensure_output_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def load_price_path_finals() -> pd.DataFrame:
    if not PRICE_PATHS_CSV.exists():
        raise FileNotFoundError(f"Missing price-path scaffold CSV: {PRICE_PATHS_CSV}")

    df = pd.read_csv(PRICE_PATHS_CSV)
    if df.empty:
        raise ValueError(f"Price-path scaffold CSV has no rows: {PRICE_PATHS_CSV}")

    scenario_col = find_column(df, SCENARIO_COLUMNS)
    price_col = find_column(df, PRICE_COLUMNS)
    step_col = find_column(df, STEP_COLUMNS)
    if scenario_col is None:
        raise ValueError("Could not detect a scenario column in scenario_price_paths_scaffold.csv.")
    if price_col is None:
        raise ValueError("Could not detect a price column in scenario_price_paths_scaffold.csv.")

    work = df.copy()
    if step_col is not None:
        work["_step_numeric"] = pd.to_numeric(work[step_col], errors="coerce")
        ordered = work.sort_values([scenario_col, "_step_numeric"])
    else:
        work["_step_numeric"] = range(len(work))
        ordered = work

    final_rows = ordered.groupby(scenario_col, as_index=False).tail(1).copy()
    first_rows = ordered.groupby(scenario_col, as_index=False).head(1).copy()

    final_rows["_scenario_key"] = final_rows[scenario_col].map(scenario_key)
    final_rows["_final_price"] = pd.to_numeric(final_rows[price_col], errors="coerce")

    start_col = find_column(work, START_PRICE_COLUMNS)
    if start_col is not None:
        final_rows["_starting_price"] = pd.to_numeric(final_rows[start_col], errors="coerce")
    else:
        first_map = dict(zip(first_rows[scenario_col].map(scenario_key), pd.to_numeric(first_rows[price_col], errors="coerce")))
        final_rows["_starting_price"] = final_rows["_scenario_key"].map(first_map)

    final_rows["_starting_price"] = final_rows["_starting_price"].fillna(DEFAULT_STARTING_PRICE)
    final_rows["_final_price"] = final_rows["_final_price"].fillna(final_rows["_starting_price"])
    return final_rows


def build_adjusted_column_map(df: pd.DataFrame) -> dict[str, str | None]:
    return {key: find_column(df, candidates) for key, candidates in ADJUSTED_PREMIUM_COLUMNS.items()}


def build_prior_column_map(df: pd.DataFrame) -> dict[str, str | None]:
    return {key: find_column(df, candidates) for key, candidates in PRIOR_PAYOFF_COLUMNS.items()}


def load_adjusted_premiums() -> pd.DataFrame:
    if not ADJUSTED_PREMIUM_CSV.exists():
        raise FileNotFoundError(f"Missing adjusted-premium CSV: {ADJUSTED_PREMIUM_CSV}")

    df = pd.read_csv(ADJUSTED_PREMIUM_CSV)
    if df.empty:
        raise ValueError(f"Adjusted-premium CSV has no rows: {ADJUSTED_PREMIUM_CSV}")

    columns = build_adjusted_column_map(df)
    required = ["scenario", "strike", "original_premium", "adjusted_premium"]
    missing = [key for key in required if columns.get(key) is None]
    if missing:
        raise ValueError(f"Missing required adjusted-premium columns: {missing}")

    work = df.copy()
    scenario_col = columns["scenario"]
    assert scenario_col is not None
    work["_scenario_key"] = work[scenario_col].map(scenario_key)
    return work


def load_prior_payoff_lookup() -> dict[str, dict[str, float | None]]:
    if not PRIOR_PREMIUM_AWARE_PAYOFF_CSV.exists():
        return {}

    df = pd.read_csv(PRIOR_PREMIUM_AWARE_PAYOFF_CSV)
    if df.empty:
        return {}

    columns = build_prior_column_map(df)
    scenario_col = columns.get("scenario")
    if scenario_col is None:
        return {}

    lookup: dict[str, dict[str, float | None]] = {}
    for _, row in df.iterrows():
        key = scenario_key(row.get(scenario_col))
        prior_relative = safe_float(row.get(columns.get("prior_relative") or ""), None)
        prior_pl = safe_float(row.get(columns.get("prior_covered_call_pl") or ""), None)
        prior_premium = safe_float(row.get(columns.get("prior_call_premium") or ""), None)
        lookup[key] = {
            "prior_relative": prior_relative,
            "prior_covered_call_pl": prior_pl,
            "prior_call_premium": prior_premium,
        }
    return lookup


def interpret_result(
    premium_change: float,
    adjusted_minus_prior: float | None,
    assigned: bool,
) -> str:
    if adjusted_minus_prior is not None and abs(adjusted_minus_prior) < 0.01:
        return "The controlled premium adjustment produced essentially no payoff change for this scenario."
    if premium_change > 0:
        if assigned:
            return "The adjusted premium increased covered-call income, partly offsetting the capped-upside effect in this assigned scenario."
        return "The adjusted premium increased covered-call income in this modeled path."
    if premium_change < 0:
        if assigned:
            return "The adjusted premium reduced income while the upside cap still applied, making this scenario less favorable."
        return "The adjusted premium reduced covered-call income in this modeled path."
    return "The adjusted premium matched the original premium, so the modeled payoff is unchanged."


def run_adjusted_premium_payoff_comparison(shares: int = DEFAULT_SHARES) -> pd.DataFrame:
    ensure_output_dirs()
    price_finals = load_price_path_finals()
    adjusted_premiums = load_adjusted_premiums()
    prior_lookup = load_prior_payoff_lookup()

    price_scenario_col = find_column(price_finals, SCENARIO_COLUMNS)
    if price_scenario_col is None:
        raise ValueError("Could not detect scenario column in final price-path rows.")

    adjusted_columns = build_adjusted_column_map(adjusted_premiums)
    scenario_col = adjusted_columns["scenario"]
    display_col = adjusted_columns.get("display_name")
    strike_col = adjusted_columns["strike"]
    original_premium_col = adjusted_columns["original_premium"]
    adjusted_premium_col = adjusted_columns["adjusted_premium"]

    assert scenario_col is not None
    assert strike_col is not None
    assert original_premium_col is not None
    assert adjusted_premium_col is not None

    adjusted_by_key = {row["_scenario_key"]: row for _, row in adjusted_premiums.iterrows()}
    rows: list[dict[str, Any]] = []

    for _, path_row in price_finals.iterrows():
        key = path_row["_scenario_key"]
        if key not in adjusted_by_key:
            continue

        premium_row = adjusted_by_key[key]
        scenario_name = str(path_row.get(price_scenario_col, premium_row.get(scenario_col, key)))
        display_name = str(premium_row.get(display_col or scenario_col, scenario_name))
        starting_price = safe_float(path_row.get("_starting_price"), DEFAULT_STARTING_PRICE) or DEFAULT_STARTING_PRICE
        final_price = safe_float(path_row.get("_final_price"), starting_price) or starting_price
        call_strike = safe_float(premium_row.get(strike_col), starting_price * 1.03) or starting_price * 1.03
        original_call_premium = safe_float(premium_row.get(original_premium_col), 0.0) or 0.0
        adjusted_call_premium = safe_float(premium_row.get(adjusted_premium_col), original_call_premium) or original_call_premium

        original_iv = safe_float(premium_row.get(adjusted_columns.get("original_iv") or ""), None)
        adjusted_iv = safe_float(premium_row.get(adjusted_columns.get("adjusted_iv") or ""), None)
        iv_adjustment = safe_float(premium_row.get(adjusted_columns.get("iv_adjustment") or ""), None)
        original_delta = safe_float(premium_row.get(adjusted_columns.get("original_delta") or ""), None)
        adjusted_delta = safe_float(premium_row.get(adjusted_columns.get("adjusted_delta") or ""), None)
        premium_change_source = safe_float(premium_row.get(adjusted_columns.get("premium_change") or ""), None)
        premium_change = adjusted_call_premium - original_call_premium if premium_change_source is None else premium_change_source
        adjustment_status = str(premium_row.get(adjusted_columns.get("adjustment_status") or "", "UNKNOWN"))
        adjustment_reason = str(premium_row.get(adjusted_columns.get("adjustment_reason") or "", ""))

        buy_and_hold_pl = (final_price - starting_price) * shares
        intrinsic_call_loss = max(final_price - call_strike, 0.0) * shares
        original_premium_income = original_call_premium * shares
        adjusted_premium_income = adjusted_call_premium * shares
        original_model_covered_call_pl = buy_and_hold_pl + original_premium_income - intrinsic_call_loss
        adjusted_model_covered_call_pl = buy_and_hold_pl + adjusted_premium_income - intrinsic_call_loss
        adjusted_relative = adjusted_model_covered_call_pl - buy_and_hold_pl
        adjusted_minus_original_model_pl = adjusted_model_covered_call_pl - original_model_covered_call_pl

        prior = prior_lookup.get(key, {})
        prior_relative = prior.get("prior_relative") if prior else None
        adjusted_minus_prior = adjusted_relative - prior_relative if prior_relative is not None else None
        assigned = final_price > call_strike
        modeled_return_percent = ((final_price / starting_price) - 1.0) * 100.0 if starting_price else 0.0

        result = AdjustedPayoffRow(
            scenario_name=scenario_name,
            scenario_display_name=display_name,
            starting_price=round(starting_price, 4),
            final_price=round(final_price, 4),
            modeled_return_percent=round(modeled_return_percent, 4),
            call_strike=round(call_strike, 4),
            original_call_premium=round(original_call_premium, 4),
            adjusted_call_premium=round(adjusted_call_premium, 4),
            premium_change=round(premium_change, 4),
            original_implied_volatility=round(original_iv, 6) if original_iv is not None else None,
            adjusted_implied_volatility=round(adjusted_iv, 6) if adjusted_iv is not None else None,
            iv_adjustment=round(iv_adjustment, 6) if iv_adjustment is not None else None,
            original_call_delta=round(original_delta, 4) if original_delta is not None else None,
            adjusted_call_delta=round(adjusted_delta, 4) if adjusted_delta is not None else None,
            buy_and_hold_pl=round(buy_and_hold_pl, 2),
            original_model_covered_call_pl=round(original_model_covered_call_pl, 2),
            adjusted_model_covered_call_pl=round(adjusted_model_covered_call_pl, 2),
            adjusted_covered_call_minus_buy_hold=round(adjusted_relative, 2),
            intrinsic_call_loss=round(intrinsic_call_loss, 2),
            original_premium_income=round(original_premium_income, 2),
            adjusted_premium_income=round(adjusted_premium_income, 2),
            adjusted_minus_original_model_pl=round(adjusted_minus_original_model_pl, 2),
            prior_premium_aware_relative_result=round(prior_relative, 2) if prior_relative is not None else None,
            adjusted_minus_prior_relative_result=round(adjusted_minus_prior, 2) if adjusted_minus_prior is not None else None,
            assigned=assigned,
            adjustment_status=adjustment_status,
            interpretation=interpret_result(premium_change, adjusted_minus_prior, assigned),
            adjustment_reason=adjustment_reason,
        )
        rows.append(result.to_dict())

    if not rows:
        raise ValueError("No adjusted premium payoff rows were created. Check scenario-name consistency between price paths and adjusted premiums.")

    output_df = pd.DataFrame(rows).sort_values("adjusted_covered_call_minus_buy_hold", ascending=False)
    output_df.to_csv(OUTPUT_CSV, index=False)
    write_html_report(output_df)
    write_summary(output_df)
    return output_df


def write_html_report(df: pd.DataFrame) -> None:
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    best = df.iloc[0]
    worst = df.iloc[-1]
    avg_relative = float(df["adjusted_covered_call_minus_buy_hold"].mean()) if not df.empty else 0.0
    avg_change = float(df["adjusted_minus_original_model_pl"].mean()) if not df.empty else 0.0
    total_change = float(df["adjusted_minus_original_model_pl"].sum()) if not df.empty else 0.0
    adjusted_rows = int((df["adjustment_status"].astype(str).str.upper() == "ADJUSTED").sum()) if "adjustment_status" in df.columns else 0

    html = f"""<!doctype html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\">
<title>Phase 2E Adjusted Premium Payoff Comparison</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 32px; color: #111827; }}
h1, h2 {{ color: #111827; }}
.summary {{ background: #f3f4f6; border: 1px solid #e5e7eb; padding: 16px; border-radius: 10px; margin: 16px 0; }}
.warning {{ background: #fff7ed; border: 1px solid #fed7aa; padding: 12px; border-radius: 8px; }}
table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
th, td {{ border: 1px solid #d1d5db; padding: 8px; text-align: right; vertical-align: top; }}
th:first-child, td:first-child, td:nth-child(2), td:last-child {{ text-align: left; }}
th {{ background: #e5e7eb; }}
.small {{ color: #6b7280; font-size: 12px; }}
</style>
</head>
<body>
<h1>Phase 2E Adjusted Premium Payoff Comparison</h1>
<p class=\"small\">Generated: {generated}</p>
<div class=\"summary\">
<h2>Summary</h2>
<p><strong>Rows reviewed:</strong> {len(df)}</p>
<p><strong>Rows with adjusted premiums:</strong> {adjusted_rows}</p>
<p><strong>Best adjusted relative scenario:</strong> {best['scenario_display_name']} ({best['adjusted_covered_call_minus_buy_hold']:,.2f})</p>
<p><strong>Worst adjusted relative scenario:</strong> {worst['scenario_display_name']} ({worst['adjusted_covered_call_minus_buy_hold']:,.2f})</p>
<p><strong>Average adjusted relative result:</strong> {avg_relative:,.2f}</p>
<p><strong>Total payoff change vs original model:</strong> {total_change:,.2f}</p>
<p><strong>Average payoff change vs original model:</strong> {avg_change:,.2f}</p>
</div>
<p class=\"warning\"><strong>Important:</strong> This is still a scaffold. It compares the controlled adjusted-premium file against the previous premium-aware payoff logic. It does not replace the customer-facing model.</p>
<h2>Adjusted premium payoff comparison table</h2>
{df.to_html(index=False, escape=True)}
</body>
</html>
"""
    OUTPUT_HTML.write_text(html, encoding="utf-8")


def write_summary(df: pd.DataFrame) -> None:
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    avg_relative = float(df["adjusted_covered_call_minus_buy_hold"].mean()) if not df.empty else 0.0
    avg_change = float(df["adjusted_minus_original_model_pl"].mean()) if not df.empty else 0.0
    total_change = float(df["adjusted_minus_original_model_pl"].sum()) if not df.empty else 0.0
    adjusted_rows = int((df["adjustment_status"].astype(str).str.upper() == "ADJUSTED").sum()) if "adjustment_status" in df.columns else 0

    lines = [
        "Phase 2E Adjusted Premium Payoff Comparison Summary",
        "=" * 58,
        f"Generated: {generated}",
        f"Project root: {PROJECT_ROOT}",
        "",
        "Purpose",
        "-------",
        "Compare the controlled adjusted-premium output against the existing premium-aware payoff result.",
        "This does not replace any production or customer-facing model output.",
        "",
        "Summary metrics",
        "---------------",
        f"Rows reviewed: {len(df)}",
        f"Rows with adjusted premium status: {adjusted_rows}",
        f"Average adjusted covered-call minus buy-and-hold: {avg_relative:.2f}",
        f"Total payoff change vs original premium model: {total_change:.2f}",
        f"Average payoff change vs original premium model: {avg_change:.2f}",
        "",
        "Input files",
        "-----------",
        str(PRICE_PATHS_CSV),
        str(ADJUSTED_PREMIUM_CSV),
        str(PRIOR_PREMIUM_AWARE_PAYOFF_CSV),
        "",
        "Output files",
        "------------",
        str(OUTPUT_CSV),
        str(OUTPUT_HTML),
        str(OUTPUT_SUMMARY_TXT),
        "",
        "Overall",
        "-------",
        "The adjusted premium payoff comparison was created successfully.",
    ]
    OUTPUT_SUMMARY_TXT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    print("=" * 96)
    print("Phase 2E adjusted premium payoff comparison")
    print("=" * 96)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Input price paths:       {PRICE_PATHS_CSV}")
    print(f"Input adjusted premiums: {ADJUSTED_PREMIUM_CSV}")
    print(f"Prior premium-aware CSV: {PRIOR_PREMIUM_AWARE_PAYOFF_CSV}")
    print()

    df = run_adjusted_premium_payoff_comparison()
    print("Adjusted premium payoff comparison created.")
    print(f"Rows: {len(df)}")
    print(f"CSV:  {OUTPUT_CSV}")
    print(f"HTML: {OUTPUT_HTML}")
    print(f"TXT:  {OUTPUT_SUMMARY_TXT}")
    print()
    print("Overall Phase 2E adjusted premium payoff comparison status: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
