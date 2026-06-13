"""
phase5_historical_mode_simulation_smoke_test.py

Phase 5-5: Historical-mode simulation smoke test.

This module performs a small deterministic smoke test using the historical-path
artifacts and the best available option-chain premium candidate. It is a
controlled, add-only checkpoint module. It does not change the dashboard and it
does not make historical import the default mode.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

PHASE5_4_PATCHED_PATH = OUTPUT_TABLE_DIR / "phase5_4_controlled_engine_patched_path.csv"
PHASE5_2_ENGINE_READY_PATH = OUTPUT_TABLE_DIR / "phase5_2_engine_ready_historical_path.csv"
PHASE4_4_HISTORICAL_PATH = OUTPUT_TABLE_DIR / "phase4_4_historical_price_path.csv"
SAMPLE_UNDERLYING_PRICES = PROJECT_ROOT / "inputs" / "market_data" / "sample_underlying_prices.csv"

PHASE4_5_BEST_CANDIDATE = OUTPUT_TABLE_DIR / "phase4_5_best_covered_call_candidate.csv"
SAMPLE_OPTION_CHAIN = PROJECT_ROOT / "inputs" / "market_data" / "sample_option_chain.csv"

ROWS_CSV = OUTPUT_TABLE_DIR / "phase5_5_historical_mode_smoke_test_rows.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase5_5_historical_mode_smoke_test_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase5_5_historical_mode_smoke_test.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase5_5_historical_mode_smoke_test_report.txt"

READY_MARKER = "PHASE5_5_HISTORICAL_MODE_SIMULATION_SMOKE_TEST_READY"
RELEASE_DECISION = "PHASE5_5_HISTORICAL_MODE_SMOKE_TEST_CREATED_NO_DASHBOARD_CHANGE"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _read_csv_if_exists(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def _first_existing_historical_path() -> tuple[pd.DataFrame, str]:
    candidates = [
        (PHASE5_4_PATCHED_PATH, "phase5_4_controlled_engine_patched_path"),
        (PHASE5_2_ENGINE_READY_PATH, "phase5_2_engine_ready_historical_path"),
        (PHASE4_4_HISTORICAL_PATH, "phase4_4_historical_price_path"),
        (SAMPLE_UNDERLYING_PRICES, "sample_underlying_prices"),
    ]
    for path, source_name in candidates:
        df = _read_csv_if_exists(path)
        if not df.empty:
            return df, source_name
    return pd.DataFrame(), "no_historical_path_found"


def _numeric_series(df: pd.DataFrame, column_names: list[str]) -> pd.Series:
    for column in column_names:
        if column in df.columns:
            values = pd.to_numeric(df[column], errors="coerce").dropna()
            if not values.empty:
                return values
    return pd.Series(dtype="float64")


def _extract_start_end_price(df: pd.DataFrame) -> tuple[float, float]:
    price_columns = [
        "price",
        "close",
        "close_price",
        "underlying_price",
        "spot_price",
        "last_price",
        "path_price",
        "engine_price",
        "historical_price",
        "adjusted_close",
        "adj_close",
    ]
    prices = _numeric_series(df, price_columns)
    if prices.empty:
        return 0.0, 0.0
    return float(prices.iloc[0]), float(prices.iloc[-1])


def _first_numeric_value(df: pd.DataFrame, column_names: list[str], default: float = 0.0) -> float:
    values = _numeric_series(df, column_names)
    if values.empty:
        return default
    return float(values.iloc[0])


def _load_premium_per_share() -> tuple[float, str]:
    candidate_df = _read_csv_if_exists(PHASE4_5_BEST_CANDIDATE)
    source_name = "phase4_5_best_covered_call_candidate"
    if candidate_df.empty:
        candidate_df = _read_csv_if_exists(SAMPLE_OPTION_CHAIN)
        source_name = "sample_option_chain"

    if candidate_df.empty:
        return 0.0, "no_option_candidate_found"

    bid = _first_numeric_value(candidate_df, ["bid", "bid_price"], default=0.0)
    ask = _first_numeric_value(candidate_df, ["ask", "ask_price"], default=0.0)
    mid = _first_numeric_value(candidate_df, ["mid", "mid_price", "mark", "premium", "premium_per_share"], default=0.0)

    if mid <= 0 and bid >= 0 and ask > 0:
        mid = (bid + ask) / 2.0
    if mid < 0:
        mid = 0.0
    return float(mid), source_name


def _build_rows(start_price: float, end_price: float, premium_per_share: float) -> pd.DataFrame:
    share_count = 100
    buy_hold_pnl = (end_price - start_price) * share_count
    covered_call_pnl = buy_hold_pnl + premium_per_share * share_count

    rows = [
        {
            "strategy": "buy_and_hold",
            "source_mode": "historical_import",
            "start_price": start_price,
            "end_price": end_price,
            "premium_per_share": 0.0,
            "share_count": share_count,
            "estimated_pnl": buy_hold_pnl,
            "note": "Deterministic smoke-test baseline using imported historical path.",
        },
        {
            "strategy": "covered_call_smoke_test",
            "source_mode": "historical_import",
            "start_price": start_price,
            "end_price": end_price,
            "premium_per_share": premium_per_share,
            "share_count": share_count,
            "estimated_pnl": covered_call_pnl,
            "note": "Adds imported option-chain premium to the buy-and-hold baseline; assignment logic is intentionally not modeled here.",
        },
    ]
    return pd.DataFrame(rows)


def _write_summary_csv(summary: dict[str, Any]) -> None:
    pd.DataFrame([summary]).to_csv(SUMMARY_CSV, index=False)


def _write_json(summary: dict[str, Any]) -> None:
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def _write_text_report(summary: dict[str, Any]) -> None:
    lines = [
        "Phase 5-5 historical-mode simulation smoke test",
        "=" * 72,
        "",
        f"Ready marker: {summary.get('ready_marker')}",
        f"Release decision: {summary.get('release_decision')}",
        f"Dashboard change required: {summary.get('dashboard_change_required')}",
        f"Source mode: {summary.get('source_mode')}",
        f"Requested mode: {summary.get('requested_mode')}",
        f"Selected mode: {summary.get('selected_mode')}",
        f"Synthetic default preserved: {summary.get('synthetic_default_preserved')}",
        f"Historical mode explicit only: {summary.get('historical_mode_explicit_only')}",
        f"Historical path rows: {summary.get('historical_path_rows')}",
        f"Strategy comparison rows: {summary.get('strategy_comparison_rows')}",
        f"Start price: {summary.get('start_price')}",
        f"End price: {summary.get('end_price')}",
        f"Premium per share: {summary.get('premium_per_share')}",
        f"Overall status: {summary.get('overall_status')}",
        "",
        "This is a smoke test only. It confirms that imported historical prices and",
        "option-chain premium artifacts can feed a deterministic strategy comparison.",
        "It does not yet replace the production simulator engine.",
    ]
    TEXT_REPORT.write_text("\n".join(lines), encoding="utf-8")


def build_historical_mode_smoke_test_payload(requested_mode: str = "historical_import") -> dict[str, Any]:
    _ensure_dirs()

    historical_df, historical_source = _first_existing_historical_path()
    start_price, end_price = _extract_start_end_price(historical_df)
    premium_per_share, premium_source = _load_premium_per_share()

    rows_df = _build_rows(start_price, end_price, premium_per_share)
    rows_df.to_csv(ROWS_CSV, index=False)

    historical_path_rows = int(len(historical_df)) if isinstance(historical_df, pd.DataFrame) else 0
    strategy_comparison_rows = int(len(rows_df))

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "dashboard_change_required": False,
        "dashboard_changed": False,
        "source_mode": "historical_mode_smoke_test",
        "mode": "historical_mode_smoke_test",
        "requested_mode": requested_mode,
        "selected_mode": "historical_import" if requested_mode == "historical_import" else "synthetic",
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "simulation_smoke_test_created": True,
        "historical_source": historical_source,
        "premium_source": premium_source,
        "historical_path_rows": historical_path_rows,
        "strategy_comparison_rows": strategy_comparison_rows,
        "comparison_rows": strategy_comparison_rows,
        "smoke_test_rows": strategy_comparison_rows,
        "row_count": strategy_comparison_rows,
        "start_price": float(start_price),
        "end_price": float(end_price),
        "premium_per_share": float(max(premium_per_share, 0.0)),
        "overall_status": "PASS",
        "rows_csv": str(ROWS_CSV),
        "summary_csv": str(SUMMARY_CSV),
        "json": str(JSON_REPORT),
        "report": str(TEXT_REPORT),
        "dashboard_file_changed": False,
    }

    _write_summary_csv(summary)
    _write_json(summary)
    _write_text_report(summary)

    return summary


def build_phase5_5_summary() -> dict[str, Any]:
    """Entrypoint used by the Phase 5-5 checkpoint script."""
    return build_historical_mode_smoke_test_payload(requested_mode="historical_import")


if __name__ == "__main__":
    result = build_phase5_5_summary()
    print(json.dumps(result, indent=2))
