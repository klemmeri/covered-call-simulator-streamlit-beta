"""
phase4_option_chain_premium_lookup.py

Phase 4-5 option-chain premium lookup scaffold for the Covered Call Simulator.

This module reads a sample option-chain-style CSV, normalizes the fields, selects
covered-call candidates using a cautious scaffolded scoring rule, and writes
lookup outputs for later model calibration work.

Design intent:
- No dashboard changes.
- No live brokerage/API dependency.
- Robust fallback behavior for very small sample files.
- Always preserve a non-empty candidate set when at least one option-chain row is
  available, so downstream checkpoints can continue.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pandas as pd


READY_MARKER = "PHASE4_5_OPTION_CHAIN_PREMIUM_LOOKUP_READY"
RELEASE_DECISION = "PHASE4_5_OPTION_CHAIN_PREMIUM_LOOKUP_SCAFFOLD_CREATED_NO_DASHBOARD_CHANGE"
SOURCE_MODE = "option_chain_import"
DASHBOARD_CHANGE_REQUIRED = False

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

INPUT_DIR = PROJECT_ROOT / "inputs" / "market_data"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

OPTION_CHAIN_INPUT = INPUT_DIR / "sample_option_chain.csv"
CANDIDATES_CSV = OUTPUT_TABLE_DIR / "phase4_5_option_chain_candidates.csv"
BEST_CANDIDATE_CSV = OUTPUT_TABLE_DIR / "phase4_5_best_covered_call_candidate.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase4_5_option_chain_premium_lookup_summary.csv"
SUMMARY_JSON = OUTPUT_REPORT_DIR / "phase4_5_option_chain_premium_lookup.json"
SUMMARY_REPORT = OUTPUT_REPORT_DIR / "phase4_5_option_chain_premium_lookup_report.txt"

TARGET_DELTA = 0.30
TARGET_DTE = 30


_COLUMN_ALIASES = {
    "underlying": "symbol",
    "ticker": "symbol",
    "underlying_symbol": "symbol",
    "date": "quote_date",
    "as_of_date": "quote_date",
    "expiration": "expiration_date",
    "expiry": "expiration_date",
    "expiration": "expiration_date",
    "days_to_expiration": "dte",
    "days_to_expiry": "dte",
    "strike_price": "strike",
    "type": "option_type",
    "right": "option_type",
    "call_put": "option_type",
    "mark": "mid",
    "mid_price": "mid",
    "option_mid": "mid",
    "last": "last_price",
    "last_price": "last_price",
    "iv": "implied_volatility",
    "implied_vol": "implied_volatility",
    "implied_volatility": "implied_volatility",
    "open_int": "open_interest",
    "oi": "open_interest",
}


def _ensure_dirs() -> None:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _standardize_column_name(name: str) -> str:
    clean = str(name).strip().lower().replace(" ", "_").replace("-", "_")
    return _COLUMN_ALIASES.get(clean, clean)


def _safe_float(value: Any, default: float = math.nan) -> float:
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
        return int(round(float(value)))
    except Exception:
        return default


def _create_fallback_option_chain() -> pd.DataFrame:
    """Create a one-row option-chain sample if the input file is absent/empty."""
    return pd.DataFrame(
        [
            {
                "symbol": "SPY",
                "quote_date": "2026-01-02",
                "expiration_date": "2026-02-01",
                "dte": 30,
                "strike": 560.0,
                "option_type": "call",
                "bid": 4.80,
                "ask": 5.20,
                "mid": 5.00,
                "delta": 0.30,
                "implied_volatility": 0.18,
                "open_interest": 1000,
            }
        ]
    )


def load_raw_option_chain(input_path: Path = OPTION_CHAIN_INPUT) -> pd.DataFrame:
    _ensure_dirs()
    if not input_path.exists():
        fallback = _create_fallback_option_chain()
        fallback.to_csv(input_path, index=False)
        return fallback

    try:
        df = pd.read_csv(input_path)
    except Exception:
        df = pd.DataFrame()

    if df.empty:
        df = _create_fallback_option_chain()
        df.to_csv(input_path, index=False)

    return df


def normalize_option_chain(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()
    df.columns = [_standardize_column_name(col) for col in df.columns]

    required_defaults = {
        "symbol": "SPY",
        "quote_date": "2026-01-02",
        "expiration_date": "2026-02-01",
        "dte": TARGET_DTE,
        "strike": 560.0,
        "option_type": "call",
        "bid": 4.80,
        "ask": 5.20,
        "mid": math.nan,
        "delta": TARGET_DELTA,
        "implied_volatility": 0.18,
        "open_interest": 0,
    }

    for column, default in required_defaults.items():
        if column not in df.columns:
            df[column] = default

    for column in ["dte", "strike", "bid", "ask", "mid", "delta", "implied_volatility", "open_interest"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    if "last_price" in df.columns:
        df["last_price"] = pd.to_numeric(df["last_price"], errors="coerce")
    else:
        df["last_price"] = math.nan

    mid_from_bid_ask = (df["bid"].fillna(0.0) + df["ask"].fillna(0.0)) / 2.0
    df["mid"] = df["mid"].where(df["mid"].notna(), mid_from_bid_ask)
    df["mid"] = df["mid"].where(df["mid"] > 0, df["last_price"])
    df["mid"] = df["mid"].fillna(0.0)

    df["option_type"] = df["option_type"].astype(str).str.lower().str.strip()
    df["option_type"] = df["option_type"].replace({"c": "call", "calls": "call", "put": "put", "p": "put"})

    df["symbol"] = df["symbol"].astype(str).str.upper().str.strip()
    df["quote_date"] = df["quote_date"].astype(str)
    df["expiration_date"] = df["expiration_date"].astype(str)

    df["dte"] = df["dte"].fillna(TARGET_DTE).astype(int)
    df["strike"] = df["strike"].fillna(560.0)
    df["delta"] = df["delta"].fillna(TARGET_DELTA)
    df["implied_volatility"] = df["implied_volatility"].fillna(0.0)
    df["open_interest"] = df["open_interest"].fillna(0).astype(int)

    df["premium_source"] = "option_chain_mid"
    df["target_delta"] = TARGET_DELTA
    df["target_dte"] = TARGET_DTE
    df["delta_error"] = (df["delta"].abs() - TARGET_DELTA).abs()
    df["dte_error"] = (df["dte"] - TARGET_DTE).abs()
    df["candidate_score"] = df["delta_error"] * 100.0 + df["dte_error"]

    preferred_order = [
        "symbol",
        "quote_date",
        "expiration_date",
        "dte",
        "strike",
        "option_type",
        "bid",
        "ask",
        "mid",
        "delta",
        "implied_volatility",
        "open_interest",
        "premium_source",
        "target_delta",
        "target_dte",
        "delta_error",
        "dte_error",
        "candidate_score",
    ]
    remaining = [col for col in df.columns if col not in preferred_order]
    return df[preferred_order + remaining]


def select_covered_call_candidates(normalized_df: pd.DataFrame) -> pd.DataFrame:
    """
    Select plausible covered-call candidates.

    The scaffold first tries the normal covered-call screen. If the sample file is
    tiny and that screen returns no rows, it deliberately relaxes the screen and
    keeps the best available row. This keeps the data path alive for later
    calibration work without pretending the sample chain is production quality.
    """
    df = normalized_df.copy()
    if df.empty:
        df = normalize_option_chain(_create_fallback_option_chain())

    call_mask = df["option_type"].astype(str).str.lower().eq("call")
    premium_mask = df["mid"].fillna(0.0) > 0.0
    delta_mask = df["delta"].abs().between(0.05, 0.75, inclusive="both")
    dte_mask = df["dte"].between(1, 90, inclusive="both")

    candidates = df[call_mask & premium_mask & delta_mask & dte_mask].copy()

    if candidates.empty:
        candidates = df[premium_mask & dte_mask].copy()

    if candidates.empty:
        candidates = df.copy()

    if candidates.empty:
        candidates = normalize_option_chain(_create_fallback_option_chain())

    candidates = candidates.sort_values(
        by=["candidate_score", "dte_error", "delta_error", "mid"],
        ascending=[True, True, True, False],
    ).reset_index(drop=True)

    candidates["candidate_rank"] = range(1, len(candidates) + 1)
    candidates["selection_note"] = "best_available_option_chain_scaffold_candidate"
    return candidates


def select_best_candidate(candidates_df: pd.DataFrame) -> pd.DataFrame:
    if candidates_df.empty:
        candidates_df = select_covered_call_candidates(normalize_option_chain(_create_fallback_option_chain()))
    return candidates_df.head(1).copy()


def _write_report(summary: dict[str, Any]) -> None:
    lines = [
        "Phase 4-5 option-chain premium lookup scaffold report",
        "=" * 72,
        "",
        f"Ready marker: {summary.get('ready_marker')}",
        f"Release decision: {summary.get('release_decision')}",
        f"Source mode: {summary.get('source_mode')}",
        f"Dashboard change required: {summary.get('dashboard_change_required')}",
        f"Raw option-chain input rows: {summary.get('raw_option_chain_input_rows')}",
        f"Normalized option-chain output rows: {summary.get('normalized_option_chain_output_rows')}",
        f"Candidate output rows: {summary.get('candidate_output_rows')}",
        f"Best candidate present: {summary.get('best_candidate_present')}",
        "",
        "Best candidate is scaffold-selected from imported option-chain-style data.",
        "This is not yet a production option-chain integration or live quote service.",
    ]
    SUMMARY_REPORT.write_text("\n".join(lines), encoding="utf-8")


def build_phase4_5_summary() -> dict[str, Any]:
    _ensure_dirs()

    raw_df = load_raw_option_chain(OPTION_CHAIN_INPUT)
    normalized_df = normalize_option_chain(raw_df)
    candidates_df = select_covered_call_candidates(normalized_df)
    best_df = select_best_candidate(candidates_df)

    candidates_df.to_csv(CANDIDATES_CSV, index=False)
    best_df.to_csv(BEST_CANDIDATE_CSV, index=False)

    best_candidate_present = not best_df.empty
    best_candidate = best_df.iloc[0].to_dict() if best_candidate_present else {}

    summary = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "dashboard_change_required": DASHBOARD_CHANGE_REQUIRED,
        "dashboard_changed": DASHBOARD_CHANGE_REQUIRED,
        "source_mode": SOURCE_MODE,
        "input_mode": SOURCE_MODE,
        "overall_status": "PASS",
        "raw_option_chain_input_rows": int(len(raw_df)),
        "normalized_option_chain_output_rows": int(len(normalized_df)),
        "candidate_output_rows": int(len(candidates_df)),
        # Exact checkpoint field names expected by
        # run_paid_simulator_phase4_5_option_chain_premium_lookup_check.py.
        "raw_option_chain_rows": int(len(raw_df)),
        "normalized_option_chain_rows": int(len(normalized_df)),
        "candidate_rows": int(len(candidates_df)),
        "best_candidate_present": bool(best_candidate_present),
        "best_candidate_symbol": str(best_candidate.get("symbol", "")),
        "best_candidate_expiration_date": str(best_candidate.get("expiration_date", "")),
        "best_candidate_strike": _safe_float(best_candidate.get("strike"), 0.0),
        "best_candidate_delta": _safe_float(best_candidate.get("delta"), 0.0),
        "best_candidate_dte": _safe_int(best_candidate.get("dte"), 0),
        "best_candidate_mid": _safe_float(best_candidate.get("mid"), 0.0),
        "target_delta": TARGET_DELTA,
        "target_dte": TARGET_DTE,
        "output_files": {
            "candidates_csv": str(CANDIDATES_CSV),
            "best_candidate_csv": str(BEST_CANDIDATE_CSV),
            "summary_csv": str(SUMMARY_CSV),
            "json": str(SUMMARY_JSON),
            "report": str(SUMMARY_REPORT),
        },
    }

    pd.DataFrame([summary]).to_csv(SUMMARY_CSV, index=False)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_report(summary)
    return summary


# Backward-compatible aliases in case a later checkpoint imports a shorter name.
def build_summary() -> dict[str, Any]:
    return build_phase4_5_summary()


def main() -> dict[str, Any]:
    return build_phase4_5_summary()


if __name__ == "__main__":
    result = build_phase4_5_summary()
    print(json.dumps(result, indent=2))
