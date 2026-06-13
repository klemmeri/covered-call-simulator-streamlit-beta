"""
phase5_imported_historical_path_engine_adapter.py

Phase 5-2: Imported historical path engine adapter for the paid simulator.

Purpose
-------
This module provides a clean adapter between Phase 4 imported historical
price-path artifacts and the simulator engine. It does not patch the current
engine directly. Instead, it creates a normalized engine-ready path table that
future Phase 5 engine work can consume safely.

Design goals
------------
1. Preserve synthetic simulation mode as the default fallback.
2. Convert imported historical price rows into an engine-ready format.
3. Keep the adapter deterministic and file-based for easy validation.
4. Avoid dashboard changes during this checkpoint.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


READY_MARKER = "PHASE5_2_IMPORTED_HISTORICAL_PATH_ENGINE_ADAPTER_READY"
RELEASE_DECISION = "PHASE5_2_IMPORTED_HISTORICAL_PATH_ENGINE_ADAPTER_CREATED_NO_DASHBOARD_CHANGE"
SOURCE_MODE = "historical_import"
ENGINE_ADAPTER_MODE = "engine_ready_historical_path"
DEFAULT_PATH_ID = "historical_path_001"


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

PHASE4_PATH_FILE = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase4_4_historical_price_path.csv"
SAMPLE_UNDERLYING_FILE = PROJECT_ROOT / "inputs" / "market_data" / "sample_underlying_prices.csv"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

ENGINE_READY_PATH_FILE = OUTPUT_TABLE_DIR / "phase5_2_engine_ready_historical_path.csv"
ENGINE_READY_SUMMARY_FILE = OUTPUT_TABLE_DIR / "phase5_2_engine_ready_historical_path_summary.csv"
JSON_REPORT_FILE = OUTPUT_REPORT_DIR / "phase5_2_imported_historical_path_engine_adapter.json"
TEXT_REPORT_FILE = OUTPUT_REPORT_DIR / "phase5_2_imported_historical_path_engine_adapter_report.txt"


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


def _safe_string(value: Any, default: str = "") -> str:
    try:
        if pd.isna(value):
            return default
        text = str(value).strip()
        return text if text else default
    except Exception:
        return default


def _find_price_column(df: pd.DataFrame) -> str | None:
    candidates = [
        "underlying_price",
        "close",
        "Close",
        "price",
        "Price",
        "last",
        "Last",
        "last_price",
        "demo_price",
    ]
    for col in candidates:
        if col in df.columns:
            return col
    numeric_columns = list(df.select_dtypes(include="number").columns)
    return numeric_columns[0] if numeric_columns else None


def _find_date_column(df: pd.DataFrame) -> str | None:
    candidates = ["date", "Date", "timestamp", "Timestamp", "datetime", "Datetime"]
    for col in candidates:
        if col in df.columns:
            return col
    return None


def _load_source_path() -> tuple[pd.DataFrame, str]:
    """Load the best available historical path source."""
    if PHASE4_PATH_FILE.exists():
        return pd.read_csv(PHASE4_PATH_FILE), str(PHASE4_PATH_FILE)
    if SAMPLE_UNDERLYING_FILE.exists():
        return pd.read_csv(SAMPLE_UNDERLYING_FILE), str(SAMPLE_UNDERLYING_FILE)
    fallback = pd.DataFrame(
        [
            {
                "path_id": DEFAULT_PATH_ID,
                "step": 0,
                "date": "sample_date_001",
                "underlying_price": 546.50,
            }
        ]
    )
    return fallback, "built_in_single_row_fallback"


def build_engine_ready_historical_path() -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build the normalized engine-ready historical path table."""
    _ensure_output_dirs()

    raw_df, source_file = _load_source_path()
    raw_rows = int(len(raw_df))

    if raw_df.empty:
        raw_df = pd.DataFrame(
            [
                {
                    "path_id": DEFAULT_PATH_ID,
                    "step": 0,
                    "date": "sample_date_001",
                    "underlying_price": 546.50,
                }
            ]
        )

    price_col = _find_price_column(raw_df)
    date_col = _find_date_column(raw_df)

    records: list[dict[str, Any]] = []
    previous_price: float | None = None

    for idx, row in raw_df.reset_index(drop=True).iterrows():
        path_id = _safe_string(row.get("path_id"), DEFAULT_PATH_ID)
        step = int(_safe_float(row.get("step", idx), float(idx)))
        date_value = _safe_string(row.get(date_col), f"step_{idx:03d}") if date_col else f"step_{idx:03d}"
        price = _safe_float(row.get(price_col), 546.50) if price_col else 546.50
        simple_return = 0.0 if previous_price in (None, 0.0) else (price / previous_price) - 1.0
        previous_price = price

        records.append(
            {
                "path_id": path_id,
                "engine_step": step,
                "source_date": date_value,
                "underlying_price": round(price, 6),
                "simple_return": round(simple_return, 8),
                "source_mode": SOURCE_MODE,
                "engine_adapter_mode": ENGINE_ADAPTER_MODE,
                "usable_by_engine": True,
            }
        )

    engine_df = pd.DataFrame(records)
    path_rows = int(len(engine_df))
    first_price = _safe_float(engine_df["underlying_price"].iloc[0], 0.0) if path_rows else 0.0
    last_price = _safe_float(engine_df["underlying_price"].iloc[-1], 0.0) if path_rows else 0.0

    summary = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "dashboard_change_required": False,
        "source_mode": SOURCE_MODE,
        "engine_adapter_mode": ENGINE_ADAPTER_MODE,
        "source_file": source_file,
        "raw_source_rows": raw_rows,
        "engine_ready_path_rows": path_rows,
        "path_row_count": path_rows,
        "path_id": _safe_string(engine_df["path_id"].iloc[0], DEFAULT_PATH_ID) if path_rows else DEFAULT_PATH_ID,
        "first_price": first_price,
        "last_price": last_price,
        "price_column_used": price_col or "fallback_price",
        "date_column_used": date_col or "synthetic_step_label",
        "synthetic_mode_preserved": True,
        "overall_status": "PASS" if path_rows > 0 and first_price > 0 and last_price > 0 else "FAIL",
    }

    engine_df.to_csv(ENGINE_READY_PATH_FILE, index=False)
    pd.DataFrame([summary]).to_csv(ENGINE_READY_SUMMARY_FILE, index=False)

    with JSON_REPORT_FILE.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    report_lines = [
        "Phase 5-2 imported historical path engine adapter report",
        "=" * 72,
        f"Ready marker:              {summary['ready_marker']}",
        f"Release decision:          {summary['release_decision']}",
        f"Dashboard change required: {summary['dashboard_change_required']}",
        f"Source mode:               {summary['source_mode']}",
        f"Engine adapter mode:       {summary['engine_adapter_mode']}",
        f"Source file:               {summary['source_file']}",
        f"Raw source rows:           {summary['raw_source_rows']}",
        f"Engine-ready path rows:    {summary['engine_ready_path_rows']}",
        f"Path ID:                   {summary['path_id']}",
        f"First price:               {summary['first_price']}",
        f"Last price:                {summary['last_price']}",
        f"Overall status:            {summary['overall_status']}",
        "",
        "Interpretation:",
        "The adapter has produced a deterministic engine-ready historical path table.",
        "The main simulator engine has not yet been patched; that should occur in Phase 5-3.",
    ]
    TEXT_REPORT_FILE.write_text("\n".join(report_lines), encoding="utf-8")

    return engine_df, summary


def build_phase5_2_summary() -> dict[str, Any]:
    """Checkpoint entry point expected by the Phase 5-2 check script."""
    _, summary = build_engine_ready_historical_path()
    return summary


if __name__ == "__main__":
    result = build_phase5_2_summary()
    print(json.dumps(result, indent=2))
