"""
premium_aware_payoff_runner.py

Phase 2B premium-aware payoff adapter for the paid covered-call simulator.

This module is intentionally standalone. It reads existing scaffold outputs and
creates a new scenario-level payoff table that uses the option-premium scaffold's
estimated call strike and premium instead of the earlier simple heuristic payoff.

Inputs expected, when available:
    outputs/tables/paid_simulator/scenario_price_paths_scaffold.csv
    outputs/tables/paid_simulator/option_premium_scaffold.csv

Outputs written:
    outputs/tables/paid_simulator/premium_aware_payoff_scaffold.csv
    outputs/reports/paid_simulator/premium_aware_payoff_scaffold.html
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]
PAID_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
PAID_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
PRICE_PATHS_CSV = PAID_TABLE_DIR / "scenario_price_paths_scaffold.csv"
OPTION_PREMIUM_CSV = PAID_TABLE_DIR / "option_premium_scaffold.csv"
OUTPUT_CSV = PAID_TABLE_DIR / "premium_aware_payoff_scaffold.csv"
OUTPUT_HTML = PAID_REPORT_DIR / "premium_aware_payoff_scaffold.html"

DEFAULT_STARTING_PRICE = 545.25
DEFAULT_SHARES = 100


SCENARIO_COLUMNS = [
    "scenario_name",
    "scenario",
    "Scenario",
    "scenario_display_name",
    "display_name",
    "market_path",
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
STRIKE_COLUMNS = [
    "call_strike",
    "strike",
    "selected_strike",
    "estimated_call_strike",
    "short_call_strike",
]
PREMIUM_COLUMNS = [
    "call_premium",
    "premium",
    "estimated_call_premium",
    "short_call_premium",
    "option_premium",
]
DELTA_COLUMNS = [
    "call_delta",
    "estimated_call_delta",
    "delta",
    "target_delta",
]
IV_COLUMNS = [
    "implied_volatility",
    "iv",
    "estimated_iv",
    "scenario_iv",
]
DISPLAY_COLUMNS = [
    "scenario_display_name",
    "display_name",
    "Scenario",
    "scenario",
]


@dataclass
class PremiumAwarePayoffRow:
    scenario_name: str
    scenario_display_name: str
    starting_price: float
    final_price: float
    modeled_return_percent: float
    call_strike: float
    call_premium: float
    call_delta: float | None
    implied_volatility: float | None
    buy_and_hold_pl: float
    covered_call_pl: float
    covered_call_minus_buy_hold: float
    premium_income: float
    intrinsic_call_loss: float
    assigned: bool
    interpretation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_name": self.scenario_name,
            "scenario_display_name": self.scenario_display_name,
            "starting_price": self.starting_price,
            "final_price": self.final_price,
            "modeled_return_percent": self.modeled_return_percent,
            "call_strike": self.call_strike,
            "call_premium": self.call_premium,
            "call_delta": self.call_delta,
            "implied_volatility": self.implied_volatility,
            "buy_and_hold_pl": self.buy_and_hold_pl,
            "covered_call_pl": self.covered_call_pl,
            "covered_call_minus_buy_hold": self.covered_call_minus_buy_hold,
            "premium_income": self.premium_income,
            "intrinsic_call_loss": self.intrinsic_call_loss,
            "assigned": self.assigned,
            "interpretation": self.interpretation,
        }


def _normalize_column_name(name: Any) -> str:
    return str(name).strip().lower().replace(" ", "_").replace("-", "_")


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    normalized = {_normalize_column_name(col): col for col in df.columns}
    for candidate in candidates:
        key = _normalize_column_name(candidate)
        if key in normalized:
            return normalized[key]
    for col in df.columns:
        norm = _normalize_column_name(col)
        for candidate in candidates:
            if _normalize_column_name(candidate) in norm:
                return col
    return None


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def _scenario_key(value: Any) -> str:
    return str(value).strip().lower().replace(" ", "_").replace("-", "_")


def load_price_path_finals(price_paths_csv: Path = PRICE_PATHS_CSV) -> pd.DataFrame:
    """Return one final price-path row per scenario."""
    if not price_paths_csv.exists():
        raise FileNotFoundError(f"Missing price-path scaffold CSV: {price_paths_csv}")

    df = pd.read_csv(price_paths_csv)
    if df.empty:
        raise ValueError(f"Price-path scaffold CSV is empty: {price_paths_csv}")

    scenario_col = find_column(df, SCENARIO_COLUMNS)
    if scenario_col is None:
        raise ValueError("Could not detect a scenario column in the price-path scaffold CSV.")

    step_col = find_column(df, STEP_COLUMNS)
    price_col = find_column(df, PRICE_COLUMNS)
    if price_col is None:
        raise ValueError("Could not detect a price column in the price-path scaffold CSV.")

    work = df.copy()
    if step_col is not None:
        work["_step_numeric"] = pd.to_numeric(work[step_col], errors="coerce")
        final_rows = work.sort_values("_step_numeric").groupby(scenario_col, as_index=False).tail(1)
    else:
        final_rows = work.groupby(scenario_col, as_index=False).tail(1)

    final_rows = final_rows.copy()
    final_rows["_scenario_key"] = final_rows[scenario_col].map(_scenario_key)
    final_rows["_final_price"] = pd.to_numeric(final_rows[price_col], errors="coerce")

    start_col = find_column(work, START_PRICE_COLUMNS)
    if start_col is not None:
        final_rows["_starting_price"] = pd.to_numeric(final_rows[start_col], errors="coerce").fillna(DEFAULT_STARTING_PRICE)
    else:
        # Try the first price in each scenario as the starting price.
        first_rows = work.sort_values("_step_numeric") if step_col is not None else work
        first_rows = first_rows.groupby(scenario_col, as_index=False).head(1).copy()
        first_map = dict(zip(first_rows[scenario_col].map(_scenario_key), pd.to_numeric(first_rows[price_col], errors="coerce")))
        final_rows["_starting_price"] = final_rows["_scenario_key"].map(first_map).fillna(DEFAULT_STARTING_PRICE)

    return final_rows


def load_premium_estimates(option_premium_csv: Path = OPTION_PREMIUM_CSV) -> pd.DataFrame:
    """Load scenario-level option premium estimates."""
    if not option_premium_csv.exists():
        raise FileNotFoundError(f"Missing option-premium scaffold CSV: {option_premium_csv}")

    df = pd.read_csv(option_premium_csv)
    if df.empty:
        raise ValueError(f"Option-premium scaffold CSV is empty: {option_premium_csv}")

    scenario_col = find_column(df, SCENARIO_COLUMNS)
    strike_col = find_column(df, STRIKE_COLUMNS)
    premium_col = find_column(df, PREMIUM_COLUMNS)
    if scenario_col is None:
        raise ValueError("Could not detect a scenario column in option-premium scaffold CSV.")
    if strike_col is None:
        raise ValueError("Could not detect a call-strike column in option-premium scaffold CSV.")
    if premium_col is None:
        raise ValueError("Could not detect a call-premium column in option-premium scaffold CSV.")

    work = df.copy()
    work["_scenario_key"] = work[scenario_col].map(_scenario_key)
    work["_call_strike"] = pd.to_numeric(work[strike_col], errors="coerce")
    work["_call_premium"] = pd.to_numeric(work[premium_col], errors="coerce")

    delta_col = find_column(work, DELTA_COLUMNS)
    iv_col = find_column(work, IV_COLUMNS)
    display_col = find_column(work, DISPLAY_COLUMNS)

    work["_call_delta"] = pd.to_numeric(work[delta_col], errors="coerce") if delta_col else None
    work["_implied_volatility"] = pd.to_numeric(work[iv_col], errors="coerce") if iv_col else None
    work["_display_name"] = work[display_col].astype(str) if display_col else work[scenario_col].astype(str)

    return work


def interpret_payoff(relative_result: float, final_price: float, call_strike: float) -> str:
    if relative_result > 0:
        return "The premium-aware covered call outperformed buy-and-hold in this modeled path because premium income exceeded any upside cap effect."
    if final_price > call_strike:
        return "The premium-aware covered call lagged buy-and-hold because the final price finished above the call strike and upside was capped."
    return "The premium-aware covered call lagged slightly or was near buy-and-hold after accounting for premium and the modeled final price."


def run_premium_aware_payoff(
    price_paths_csv: Path = PRICE_PATHS_CSV,
    option_premium_csv: Path = OPTION_PREMIUM_CSV,
    output_csv: Path = OUTPUT_CSV,
    output_html: Path = OUTPUT_HTML,
    shares: int = DEFAULT_SHARES,
) -> pd.DataFrame:
    """Create premium-aware covered-call payoff results by scenario."""
    path_finals = load_price_path_finals(price_paths_csv)
    premiums = load_premium_estimates(option_premium_csv)

    rows: list[dict[str, Any]] = []
    premium_by_key = {row["_scenario_key"]: row for _, row in premiums.iterrows()}

    scenario_col = find_column(path_finals, SCENARIO_COLUMNS)
    if scenario_col is None:
        raise ValueError("Could not detect scenario column after loading price-path final rows.")

    for _, path_row in path_finals.iterrows():
        key = path_row["_scenario_key"]
        if key not in premium_by_key:
            continue

        premium_row = premium_by_key[key]
        scenario_name = str(path_row[scenario_col])
        display_name = str(premium_row.get("_display_name", scenario_name))
        starting_price = _safe_float(path_row.get("_starting_price"), DEFAULT_STARTING_PRICE)
        final_price = _safe_float(path_row.get("_final_price"), starting_price)
        call_strike = _safe_float(premium_row.get("_call_strike"), starting_price * 1.03)
        call_premium = _safe_float(premium_row.get("_call_premium"), 0.0)
        call_delta_raw = premium_row.get("_call_delta")
        iv_raw = premium_row.get("_implied_volatility")
        call_delta = None if pd.isna(call_delta_raw) else _safe_float(call_delta_raw)
        implied_volatility = None if pd.isna(iv_raw) else _safe_float(iv_raw)

        buy_and_hold_pl = (final_price - starting_price) * shares
        premium_income = call_premium * shares
        intrinsic_call_loss = max(final_price - call_strike, 0.0) * shares
        covered_call_pl = buy_and_hold_pl + premium_income - intrinsic_call_loss
        relative_result = covered_call_pl - buy_and_hold_pl
        assigned = final_price > call_strike
        modeled_return_percent = ((final_price / starting_price) - 1.0) * 100.0 if starting_price else 0.0

        row = PremiumAwarePayoffRow(
            scenario_name=scenario_name,
            scenario_display_name=display_name,
            starting_price=starting_price,
            final_price=final_price,
            modeled_return_percent=modeled_return_percent,
            call_strike=call_strike,
            call_premium=call_premium,
            call_delta=call_delta,
            implied_volatility=implied_volatility,
            buy_and_hold_pl=buy_and_hold_pl,
            covered_call_pl=covered_call_pl,
            covered_call_minus_buy_hold=relative_result,
            premium_income=premium_income,
            intrinsic_call_loss=intrinsic_call_loss,
            assigned=assigned,
            interpretation=interpret_payoff(relative_result, final_price, call_strike),
        )
        rows.append(row.to_dict())

    if not rows:
        raise ValueError("No premium-aware payoff rows were created. Check scenario-name consistency between input CSVs.")

    output_df = pd.DataFrame(rows).sort_values("covered_call_minus_buy_hold", ascending=False)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_html.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(output_csv, index=False)
    write_html_report(output_df, output_html)
    return output_df


def write_html_report(df: pd.DataFrame, output_html: Path = OUTPUT_HTML) -> None:
    best = df.iloc[0]
    worst = df.iloc[-1]
    avg_relative = df["covered_call_minus_buy_hold"].mean()

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset=\"utf-8\">
<title>Premium-Aware Payoff Scaffold</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 32px; color: #111827; }}
h1, h2 {{ color: #111827; }}
table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
th, td {{ border: 1px solid #d1d5db; padding: 8px; text-align: right; }}
th:first-child, td:first-child, td:last-child {{ text-align: left; }}
th {{ background: #f3f4f6; }}
.summary {{ background: #f9fafb; border: 1px solid #e5e7eb; padding: 16px; border-radius: 8px; }}
.warning {{ background: #fff7ed; border: 1px solid #fed7aa; padding: 12px; border-radius: 8px; }}
</style>
</head>
<body>
<h1>Phase 2B Premium-Aware Payoff Scaffold</h1>
<div class=\"summary\">
<p><strong>Best scenario:</strong> {best['scenario_display_name']} ({best['covered_call_minus_buy_hold']:,.2f} relative result)</p>
<p><strong>Worst scenario:</strong> {worst['scenario_display_name']} ({worst['covered_call_minus_buy_hold']:,.2f} relative result)</p>
<p><strong>Average relative result:</strong> {avg_relative:,.2f}</p>
</div>
<p class=\"warning\"><strong>Important:</strong> This is still a scaffold. It uses the option-premium scaffold output and simplified payoff math. It is not yet a complete live option-pricing or execution model.</p>
<h2>Premium-aware scenario table</h2>
{df.to_html(index=False, escape=True)}
</body>
</html>
"""
    output_html.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    result_df = run_premium_aware_payoff()
    print(result_df.to_string(index=False))
    print(f"\nSaved CSV: {OUTPUT_CSV}")
    print(f"Saved HTML: {OUTPUT_HTML}")
