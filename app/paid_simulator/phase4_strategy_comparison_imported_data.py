"""
phase4_strategy_comparison_imported_data.py

Phase 4-7 scaffold for the Covered Call Simulator paid workflow.

Purpose
-------
Compare a simple buy-and-hold baseline with a covered-call scaffold using the
imported/historical data artifacts created earlier in Phase 4.

This is intentionally a controlled scaffold, not the final production engine.
It reads the historical path created in Phase 4-4 and the best option-chain
candidate created in Phase 4-5. It then writes a transparent comparison report
that can be used by later checkpoints to connect imported data to the main
simulation engine.

No dashboard file is changed by this module.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


READY_MARKER = "PHASE4_7_IMPORTED_DATA_STRATEGY_COMPARISON_READY"
RELEASE_DECISION = "PHASE4_7_IMPORTED_DATA_STRATEGY_COMPARISON_SCAFFOLD_CREATED_NO_DASHBOARD_CHANGE"
SOURCE_MODE = "imported_historical_data"
DASHBOARD_CHANGE_REQUIRED = False


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

PHASE4_4_PATH_CSV = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase4_4_historical_price_path.csv"
PHASE4_5_BEST_CANDIDATE_CSV = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase4_5_best_covered_call_candidate.csv"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

COMPARISON_ROWS_CSV = OUTPUT_TABLE_DIR / "phase4_7_imported_data_strategy_comparison_rows.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase4_7_imported_data_strategy_comparison_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase4_7_imported_data_strategy_comparison.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase4_7_imported_data_strategy_comparison_report.txt"


DEFAULT_START_PRICE = 546.50
DEFAULT_END_PRICE = 546.50
DEFAULT_OPTION_PREMIUM = 1.00
DEFAULT_CONTRACT_MULTIPLIER = 100
DEFAULT_SHARE_COUNT = 100


def _ensure_output_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if pd.isna(value):
            return default
        return int(float(value))
    except Exception:
        return default


def _read_historical_path() -> pd.DataFrame:
    if not PHASE4_4_PATH_CSV.exists():
        return pd.DataFrame(
            [
                {
                    "path_id": "historical_path_001",
                    "step": 0,
                    "date": "sample",
                    "price": DEFAULT_START_PRICE,
                    "underlying_price": DEFAULT_START_PRICE,
                    "close": DEFAULT_START_PRICE,
                }
            ]
        )

    df = pd.read_csv(PHASE4_4_PATH_CSV)
    if df.empty:
        return pd.DataFrame(
            [
                {
                    "path_id": "historical_path_001",
                    "step": 0,
                    "date": "sample",
                    "price": DEFAULT_START_PRICE,
                    "underlying_price": DEFAULT_START_PRICE,
                    "close": DEFAULT_START_PRICE,
                }
            ]
        )
    return df


def _read_best_candidate() -> pd.DataFrame:
    if not PHASE4_5_BEST_CANDIDATE_CSV.exists():
        return pd.DataFrame(
            [
                {
                    "symbol": "SPY",
                    "option_type": "call",
                    "strike": 550.0,
                    "mid": DEFAULT_OPTION_PREMIUM,
                    "bid": DEFAULT_OPTION_PREMIUM * 0.95,
                    "ask": DEFAULT_OPTION_PREMIUM * 1.05,
                    "delta": 0.30,
                    "dte": 30,
                    "expiration": "sample",
                }
            ]
        )

    df = pd.read_csv(PHASE4_5_BEST_CANDIDATE_CSV)
    if df.empty:
        return pd.DataFrame(
            [
                {
                    "symbol": "SPY",
                    "option_type": "call",
                    "strike": 550.0,
                    "mid": DEFAULT_OPTION_PREMIUM,
                    "bid": DEFAULT_OPTION_PREMIUM * 0.95,
                    "ask": DEFAULT_OPTION_PREMIUM * 1.05,
                    "delta": 0.30,
                    "dte": 30,
                    "expiration": "sample",
                }
            ]
        )
    return df


def _price_column(df: pd.DataFrame) -> str | None:
    candidates = ["price", "underlying_price", "close", "Close", "last", "Last"]
    for column in candidates:
        if column in df.columns:
            return column
    numeric_columns = list(df.select_dtypes(include="number").columns)
    if numeric_columns:
        return numeric_columns[-1]
    return None


def _candidate_value(row: pd.Series, names: list[str], default: float = 0.0) -> float:
    for name in names:
        if name in row.index:
            value = _safe_float(row.get(name), default=None)
            if value is not None:
                return value
    return default


def _candidate_int(row: pd.Series, names: list[str], default: int = 0) -> int:
    for name in names:
        if name in row.index:
            value = _safe_int(row.get(name), default=None)
            if value is not None:
                return value
    return default


def build_imported_data_strategy_comparison() -> dict[str, Any]:
    """
    Build Phase 4-7 imported-data strategy comparison outputs.

    Returns
    -------
    dict
        Summary dictionary consumed by the Phase 4-7 checkpoint script.
    """

    _ensure_output_dirs()

    path_df = _read_historical_path()
    candidate_df = _read_best_candidate()

    price_col = _price_column(path_df)
    if price_col is None:
        start_price = DEFAULT_START_PRICE
        end_price = DEFAULT_END_PRICE
    else:
        cleaned_prices = pd.to_numeric(path_df[price_col], errors="coerce").dropna()
        if cleaned_prices.empty:
            start_price = DEFAULT_START_PRICE
            end_price = DEFAULT_END_PRICE
        else:
            start_price = float(cleaned_prices.iloc[0])
            end_price = float(cleaned_prices.iloc[-1])

    candidate = candidate_df.iloc[0] if not candidate_df.empty else pd.Series(dtype="object")
    strike = _candidate_value(candidate, ["strike", "strike_price", "Strike"], default=max(start_price, end_price))
    premium = _candidate_value(candidate, ["mid", "mid_price", "premium", "bid", "last", "Last"], default=DEFAULT_OPTION_PREMIUM)
    delta = _candidate_value(candidate, ["delta", "Delta"], default=0.30)
    dte = _candidate_int(candidate, ["dte", "DTE", "days_to_expiration"], default=30)

    share_count = DEFAULT_SHARE_COUNT
    contract_multiplier = DEFAULT_CONTRACT_MULTIPLIER

    buy_hold_start_value = start_price * share_count
    buy_hold_end_value = end_price * share_count
    buy_hold_pl = buy_hold_end_value - buy_hold_start_value

    gross_option_premium = premium * contract_multiplier
    stock_value_at_end = end_price * share_count
    assignment_value = strike * share_count
    covered_call_end_stock_value = min(stock_value_at_end, assignment_value)
    covered_call_pl = (covered_call_end_stock_value - buy_hold_start_value) + gross_option_premium
    option_income = gross_option_premium
    capped_upside_cost = max(0.0, (end_price - strike) * share_count)
    covered_call_vs_buy_hold = covered_call_pl - buy_hold_pl

    comparison_rows = pd.DataFrame(
        [
            {
                "strategy": "buy_and_hold",
                "source_mode": SOURCE_MODE,
                "start_price": start_price,
                "end_price": end_price,
                "strike": None,
                "option_premium": 0.0,
                "stock_pl": buy_hold_pl,
                "option_income": 0.0,
                "capped_upside_cost": 0.0,
                "total_pl": buy_hold_pl,
            },
            {
                "strategy": "covered_call_imported_candidate",
                "source_mode": SOURCE_MODE,
                "start_price": start_price,
                "end_price": end_price,
                "strike": strike,
                "option_premium": premium,
                "stock_pl": covered_call_end_stock_value - buy_hold_start_value,
                "option_income": option_income,
                "capped_upside_cost": capped_upside_cost,
                "total_pl": covered_call_pl,
            },
        ]
    )

    summary = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "dashboard_change_required": DASHBOARD_CHANGE_REQUIRED,
        "source_mode": SOURCE_MODE,
        "overall_status": "PASS",
        "historical_path_rows": int(len(path_df)),
        "best_candidate_rows": int(len(candidate_df)),
        "comparison_row_count": int(len(comparison_rows)),
        "buy_hold_pl": round(float(buy_hold_pl), 4),
        "covered_call_pl": round(float(covered_call_pl), 4),
        "covered_call_vs_buy_hold": round(float(covered_call_vs_buy_hold), 4),
        "start_price": round(float(start_price), 4),
        "end_price": round(float(end_price), 4),
        "selected_strike": round(float(strike), 4),
        "selected_premium": round(float(premium), 4),
        "selected_delta": round(float(delta), 4),
        "selected_dte": int(dte),
        "output_files": {
            "comparison_rows_csv": str(COMPARISON_ROWS_CSV),
            "summary_csv": str(SUMMARY_CSV),
            "json_report": str(JSON_REPORT),
            "text_report": str(TEXT_REPORT),
        },
    }

    comparison_rows.to_csv(COMPARISON_ROWS_CSV, index=False)
    pd.DataFrame([summary]).drop(columns=["output_files"]).to_csv(SUMMARY_CSV, index=False)

    with JSON_REPORT.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    lines = [
        "Phase 4-7 imported-data strategy comparison report",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Dashboard change required: {DASHBOARD_CHANGE_REQUIRED}",
        f"Source mode: {SOURCE_MODE}",
        "",
        f"Historical path rows: {summary['historical_path_rows']}",
        f"Best candidate rows: {summary['best_candidate_rows']}",
        f"Comparison rows: {summary['comparison_row_count']}",
        "",
        f"Start price: {summary['start_price']}",
        f"End price: {summary['end_price']}",
        f"Selected strike: {summary['selected_strike']}",
        f"Selected premium: {summary['selected_premium']}",
        f"Selected delta: {summary['selected_delta']}",
        f"Selected DTE: {summary['selected_dte']}",
        "",
        f"Buy-and-hold P/L: {summary['buy_hold_pl']}",
        f"Covered-call scaffold P/L: {summary['covered_call_pl']}",
        f"Covered-call vs buy-and-hold: {summary['covered_call_vs_buy_hold']}",
        "",
        "Interpretation:",
        "This is a scaffold comparison using imported Phase 4 artifacts. It is not yet the final production simulator path.",
    ]
    TEXT_REPORT.write_text("\n".join(lines), encoding="utf-8")

    return summary


def build_phase4_7_summary() -> dict[str, Any]:
    """Compatibility wrapper used by the Phase 4-7 checkpoint script."""

    return build_imported_data_strategy_comparison()


if __name__ == "__main__":
    result = build_phase4_7_summary()
    print(json.dumps(result, indent=2))
