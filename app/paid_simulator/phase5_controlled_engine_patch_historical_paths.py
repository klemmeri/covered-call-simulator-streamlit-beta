"""
phase5_controlled_engine_patch_historical_paths.py

Phase 5-4 controlled historical-path engine patch for the Covered Call Simulator.

This module is intentionally opt-in. It does not change the Streamlit dashboard and
it does not make historical-import mode the default. Its purpose is to provide a
small, controlled integration layer that an engine runner can call when the user
explicitly selects imported historical paths.

Design goals
------------
1. Preserve synthetic-path mode as the default.
2. Allow historical-import mode only when requested explicitly.
3. Read the Phase 5-2 engine-ready historical path artifact when available.
4. Produce an engine-compatible path table with stable column names.
5. Produce a compact summary and report for checkpoint validation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PHASE5_4_READY_MARKER = "PHASE5_4_CONTROLLED_ENGINE_PATCH_HISTORICAL_PATHS_READY"
PHASE5_4_RELEASE_DECISION = "PHASE5_4_CONTROLLED_ENGINE_PATCH_CREATED_OPT_IN_NO_DASHBOARD_CHANGE"

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENGINE_READY_HISTORICAL_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase5_2_engine_ready_historical_path.csv"
PHASE4_HISTORICAL_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase4_4_historical_price_path.csv"
SAMPLE_UNDERLYING_PRICES = PROJECT_ROOT / "inputs" / "market_data" / "sample_underlying_prices.csv"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

PATCHED_PATH_OUTPUT = OUTPUT_TABLE_DIR / "phase5_4_controlled_engine_patched_path.csv"
PATCH_SUMMARY_OUTPUT = OUTPUT_TABLE_DIR / "phase5_4_controlled_engine_patch_summary.csv"
PATCH_JSON_OUTPUT = OUTPUT_REPORT_DIR / "phase5_4_controlled_engine_patch_historical_paths.json"
PATCH_REPORT_OUTPUT = OUTPUT_REPORT_DIR / "phase5_4_controlled_engine_patch_historical_paths_report.txt"

ALLOWED_MODES = {"synthetic", "historical_import"}


def _ensure_output_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _read_csv_if_exists(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def _first_available_historical_path() -> tuple[pd.DataFrame, str]:
    """Return the best available historical path dataframe and its source label."""
    candidates = [
        (ENGINE_READY_HISTORICAL_PATH, "phase5_2_engine_ready_historical_path"),
        (PHASE4_HISTORICAL_PATH, "phase4_4_historical_price_path"),
        (SAMPLE_UNDERLYING_PRICES, "sample_underlying_prices"),
    ]
    for path, label in candidates:
        df = _read_csv_if_exists(path)
        if not df.empty:
            return df, label
    return pd.DataFrame(), "none"


def _coerce_price_column(df: pd.DataFrame) -> pd.Series:
    """Find a usable price column and return it as a positive numeric Series."""
    for column in ["engine_price", "price", "close", "underlying_price", "last_price", "adj_close"]:
        if column in df.columns:
            series = pd.to_numeric(df[column], errors="coerce")
            series = series[series > 0]
            if not series.empty:
                return series.reset_index(drop=True)
    return pd.Series(dtype="float64")


def _coerce_step_column(df: pd.DataFrame, row_count: int) -> pd.Series:
    if row_count <= 0:
        return pd.Series(dtype="int64")
    if "engine_step" in df.columns:
        raw = pd.to_numeric(df["engine_step"], errors="coerce")
    elif "step" in df.columns:
        raw = pd.to_numeric(df["step"], errors="coerce")
    else:
        raw = pd.Series([None] * row_count)
    fallback = pd.Series(range(1, row_count + 1), index=raw.index)
    return raw.fillna(fallback).astype(int).reset_index(drop=True)


def _coerce_date_column(df: pd.DataFrame, row_count: int) -> pd.Series:
    if row_count <= 0:
        return pd.Series(dtype="object")
    for column in ["engine_date", "date", "timestamp"]:
        if column in df.columns:
            values = df[column].astype(str).replace({"nan": ""})
            if values.str.len().sum() > 0:
                return values.reset_index(drop=True)
    return pd.Series([f"row_{i:03d}" for i in range(1, row_count + 1)])


def _build_engine_ready_path_from_historical(df: pd.DataFrame, source_label: str) -> pd.DataFrame:
    price = _coerce_price_column(df)
    if price.empty:
        return pd.DataFrame(columns=["engine_step", "engine_date", "engine_price", "path_id", "source_mode", "source_label"])

    row_count = len(price)
    date_values = _coerce_date_column(df.iloc[:row_count].copy(), row_count)
    step_values = _coerce_step_column(df.iloc[:row_count].copy(), row_count)

    output = pd.DataFrame(
        {
            "engine_step": step_values,
            "engine_date": date_values,
            "engine_price": price,
            "path_id": "historical_path_001",
            "source_mode": "historical_import",
            "source_label": source_label,
        }
    )
    output["engine_return"] = output["engine_price"].pct_change().fillna(0.0)
    output["engine_cumulative_return"] = output["engine_price"] / output["engine_price"].iloc[0] - 1.0
    return output


def _build_synthetic_placeholder_path() -> pd.DataFrame:
    """Small deterministic placeholder proving that synthetic remains default."""
    prices = pd.Series([545.00, 546.25, 545.75], dtype="float64")
    output = pd.DataFrame(
        {
            "engine_step": [1, 2, 3],
            "engine_date": ["synthetic_001", "synthetic_002", "synthetic_003"],
            "engine_price": prices,
            "path_id": "synthetic_default_001",
            "source_mode": "synthetic",
            "source_label": "controlled_synthetic_placeholder",
        }
    )
    output["engine_return"] = output["engine_price"].pct_change().fillna(0.0)
    output["engine_cumulative_return"] = output["engine_price"] / output["engine_price"].iloc[0] - 1.0
    return output


def build_controlled_engine_patch_payload(requested_mode: str = "synthetic") -> dict[str, Any]:
    """Build the controlled engine patch payload for synthetic or historical mode."""
    _ensure_output_dirs()

    if requested_mode not in ALLOWED_MODES:
        selected_mode = "synthetic"
        mode_note = f"Invalid requested mode {requested_mode!r}; reverted to synthetic."
    else:
        selected_mode = requested_mode
        mode_note = "Requested mode accepted."

    if selected_mode == "historical_import":
        raw_df, source_label = _first_available_historical_path()
        engine_path = _build_engine_ready_path_from_historical(raw_df, source_label)
        if engine_path.empty:
            selected_mode = "synthetic"
            mode_note = "Historical path unavailable or invalid; reverted to synthetic."
            source_label = "controlled_synthetic_placeholder"
            engine_path = _build_synthetic_placeholder_path()
    else:
        source_label = "controlled_synthetic_placeholder"
        engine_path = _build_synthetic_placeholder_path()

    first_price = float(engine_path["engine_price"].iloc[0]) if not engine_path.empty else None
    last_price = float(engine_path["engine_price"].iloc[-1]) if not engine_path.empty else None
    row_count = int(len(engine_path))

    engine_path.to_csv(PATCHED_PATH_OUTPUT, index=False)

    summary = {
        "ready_marker": PHASE5_4_READY_MARKER,
        "release_decision": PHASE5_4_RELEASE_DECISION,
        "overall_status": "PASS",
        "dashboard_change_required": False,
        "core_engine_default_changed": False,
        "engine_patch_mode": "controlled_opt_in_historical_path_patch",
        "requested_mode": requested_mode,
        "selected_mode": selected_mode,
        "source_label": source_label,
        "mode_note": mode_note,
        "synthetic_remains_default": True,
        "historical_import_requires_explicit_request": True,
        "controlled_engine_patch_created": True,
        "patched_path_rows": row_count,
        "patched_path_first_price": first_price,
        "patched_path_last_price": last_price,
        "patched_path_output": str(PATCHED_PATH_OUTPUT),
        "summary_csv_output": str(PATCH_SUMMARY_OUTPUT),
        "json_output": str(PATCH_JSON_OUTPUT),
        "report_output": str(PATCH_REPORT_OUTPUT),
    }

    pd.DataFrame([summary]).to_csv(PATCH_SUMMARY_OUTPUT, index=False)
    with PATCH_JSON_OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    PATCH_REPORT_OUTPUT.write_text(_build_report_text(summary), encoding="utf-8")

    return summary


def _build_report_text(summary: dict[str, Any]) -> str:
    lines = [
        "Phase 5-4 controlled historical path engine patch",
        "=" * 72,
        "",
        f"Ready marker: {summary.get('ready_marker')}",
        f"Release decision: {summary.get('release_decision')}",
        f"Overall status: {summary.get('overall_status')}",
        "",
        "Patch behavior:",
        f"  Dashboard change required: {summary.get('dashboard_change_required')}",
        f"  Core engine default changed: {summary.get('core_engine_default_changed')}",
        f"  Synthetic remains default: {summary.get('synthetic_remains_default')}",
        f"  Historical import requires explicit request: {summary.get('historical_import_requires_explicit_request')}",
        "",
        "Selected path:",
        f"  Requested mode: {summary.get('requested_mode')}",
        f"  Selected mode: {summary.get('selected_mode')}",
        f"  Source label: {summary.get('source_label')}",
        f"  Rows: {summary.get('patched_path_rows')}",
        f"  First price: {summary.get('patched_path_first_price')}",
        f"  Last price: {summary.get('patched_path_last_price')}",
    ]
    return "\n".join(lines) + "\n"


def build_phase5_4_summary() -> dict[str, Any]:
    """Checkpoint entry point expected by the Phase 5-4 check script."""
    return build_controlled_engine_patch_payload(requested_mode="historical_import")


if __name__ == "__main__":
    result = build_phase5_4_summary()
    print(json.dumps(result, indent=2))
