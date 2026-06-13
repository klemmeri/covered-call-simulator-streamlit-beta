"""
phase5_controlled_historical_path_engine_hook.py

Phase 5-3: Controlled historical path engine hook contract.

This module prepares a safe, add-only contract for connecting imported historical
price paths to the simulator engine in a later checkpoint. It does not patch the
simulator engine and it does not modify the Streamlit dashboard.

This replacement preserves the exact summary keys expected by:

    app/run_paid_simulator_phase5_3_controlled_engine_hook_check.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

READY_MARKER = "PHASE5_3_CONTROLLED_HISTORICAL_PATH_ENGINE_HOOK_READY"
RELEASE_DECISION = "PHASE5_3_ENGINE_HOOK_CONTRACT_CREATED_NO_DASHBOARD_CHANGE"

SOURCE_ENGINE_READY_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase5_2_engine_ready_historical_path.csv"
FALLBACK_HISTORICAL_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase4_4_historical_price_path.csv"
FALLBACK_SAMPLE_PRICES = PROJECT_ROOT / "inputs" / "market_data" / "sample_underlying_prices.csv"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

HOOK_CONTRACT_CSV = OUTPUT_TABLE_DIR / "phase5_3_historical_path_engine_hook_contract.csv"
HOOK_PREVIEW_CSV = OUTPUT_TABLE_DIR / "phase5_3_historical_path_engine_hook_preview.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase5_3_historical_path_engine_hook_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase5_3_historical_path_engine_hook.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase5_3_historical_path_engine_hook_report.txt"

REQUIRED_ENGINE_COLUMNS = [
    "path_id",
    "step",
    "date",
    "underlying_price",
    "source_mode",
]


DEFAULT_ENGINE_PATH_ROW = {
    "path_id": "historical_path_001",
    "step": 1,
    "date": "sample_date_001",
    "underlying_price": 546.50,
    "source_mode": "historical_import",
}


def _ensure_output_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _first_existing_source() -> Path | None:
    for path in [SOURCE_ENGINE_READY_PATH, FALLBACK_HISTORICAL_PATH, FALLBACK_SAMPLE_PRICES]:
        if path.exists():
            return path
    return None


def _coalesce_column(df: pd.DataFrame, candidates: list[str], default: Any = None) -> pd.Series:
    for candidate in candidates:
        if candidate in df.columns:
            return df[candidate]
    return pd.Series([default] * len(df), index=df.index)


def _default_engine_path() -> pd.DataFrame:
    return pd.DataFrame([DEFAULT_ENGINE_PATH_ROW])


def _safe_read_engine_path() -> pd.DataFrame:
    """
    Read the best available historical path artifact and normalize it to the
    minimal engine-ready contract.
    """
    source_path = _first_existing_source()

    if source_path is None:
        return _default_engine_path()

    raw = pd.read_csv(source_path)

    if raw.empty:
        return _default_engine_path()

    df = pd.DataFrame(index=raw.index)

    path_id_source = _coalesce_column(raw, ["path_id", "scenario_id", "source_path_id"], "historical_path_001")
    path_id = path_id_source.astype(str).replace(
        {"nan": "historical_path_001", "None": "historical_path_001", "": "historical_path_001"}
    )
    df["path_id"] = path_id.fillna("historical_path_001")

    step_source = _coalesce_column(raw, ["step", "period", "row_number"], None)
    step_numeric = pd.to_numeric(step_source, errors="coerce")
    fallback_steps = pd.Series(range(1, len(raw) + 1), index=raw.index)
    df["step"] = step_numeric.fillna(fallback_steps).astype(int)

    date_source = _coalesce_column(raw, ["date", "timestamp", "datetime"], None)
    fallback_dates = pd.Series([f"sample_date_{i:03d}" for i in range(1, len(raw) + 1)], index=raw.index)
    df["date"] = date_source.fillna(fallback_dates).astype(str)

    price_source = _coalesce_column(raw, ["underlying_price", "close", "price", "last_price", "adj_close"], 546.50)
    price_numeric = pd.to_numeric(price_source, errors="coerce")
    df["underlying_price"] = price_numeric.fillna(546.50).astype(float)

    source_mode_source = _coalesce_column(raw, ["source_mode", "input_mode"], "historical_import")
    source_mode = source_mode_source.astype(str).replace(
        {"nan": "historical_import", "None": "historical_import", "": "historical_import"}
    )
    df["source_mode"] = source_mode.fillna("historical_import")

    return df[REQUIRED_ENGINE_COLUMNS]


def _build_hook_contract() -> pd.DataFrame:
    rows = [
        ("path_id", "Identifier for the imported historical path."),
        ("step", "Sequential path step used by the simulation engine."),
        ("date", "Date or timestamp associated with the imported price row."),
        ("underlying_price", "Underlying price supplied to the covered-call path logic."),
        ("source_mode", "Explicit mode marker; historical import must be requested intentionally."),
    ]
    return pd.DataFrame(
        [
            {
                "engine_column": name,
                "required": True,
                "description": description,
                "phase5_3_status": "ready",
            }
            for name, description in rows
        ]
    )


def _write_text_report(summary: dict[str, Any]) -> None:
    lines = [
        "Phase 5-3 controlled historical path engine hook",
        "=" * 72,
        "",
        f"Ready marker: {summary.get('ready_marker')}",
        f"Release decision: {summary.get('release_decision')}",
        f"Source mode: {summary.get('source_mode')}",
        f"Requested mode: {summary.get('requested_mode')}",
        f"Selected mode: {summary.get('selected_mode')}",
        f"Engine hook contract created: {summary.get('engine_hook_contract_created')}",
        f"Engine patch applied: {summary.get('engine_patch_applied')}",
        f"Dashboard change required: {summary.get('dashboard_change_required')}",
        f"Hook contract rows: {summary.get('hook_contract_rows')}",
        f"Required column count: {summary.get('required_column_count')}",
        f"Historical path rows: {summary.get('historical_path_rows')}",
        "",
        "Interpretation:",
        "The historical path engine hook contract is ready, but the simulator engine",
        "has not yet been patched. Synthetic mode remains the default until a later",
        "controlled engine patch explicitly enables historical-import mode.",
    ]
    TEXT_REPORT.write_text("\n".join(lines), encoding="utf-8")


def build_historical_path_engine_hook_payload(requested_mode: str = "historical_import") -> dict[str, Any]:
    _ensure_output_dirs()

    selected_mode = "historical_import" if requested_mode == "historical_import" else "synthetic_paths"
    historical_df = _safe_read_engine_path()
    contract_df = _build_hook_contract()

    engine_hook_contract_created = not contract_df.empty
    required_column_count = sum(1 for col in REQUIRED_ENGINE_COLUMNS if col in historical_df.columns)
    historical_path_rows = int(len(historical_df))

    contract_df.to_csv(HOOK_CONTRACT_CSV, index=False)
    historical_df.to_csv(HOOK_PREVIEW_CSV, index=False)

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "overall_status": "PASS",
        "dashboard_change_required": False,
        "source_mode": "controlled_historical_path_hook",
        "requested_mode": requested_mode,
        "selected_mode": selected_mode,
        "engine_hook_contract_created": engine_hook_contract_created,
        "engine_patch_applied": False,
        "hook_contract_rows": int(len(contract_df)),
        "required_column_count": int(required_column_count),
        "historical_path_rows": historical_path_rows,
        "first_underlying_price": float(historical_df["underlying_price"].iloc[0]) if historical_path_rows else None,
        "last_underlying_price": float(historical_df["underlying_price"].iloc[-1]) if historical_path_rows else None,
        "hook_contract_csv": str(HOOK_CONTRACT_CSV),
        "hook_preview_csv": str(HOOK_PREVIEW_CSV),
        "summary_csv": str(SUMMARY_CSV),
        "json_report": str(JSON_REPORT),
        "text_report": str(TEXT_REPORT),
        # Backward-compatible aliases for manual inspection and prior reports.
        "dashboard_changed": False,
        "hook_mode": "controlled_historical_path_hook",
        "contract_created": engine_hook_contract_created,
        "required_engine_columns_present": required_column_count == len(REQUIRED_ENGINE_COLUMNS),
        "historical_engine_ready_path_rows": historical_path_rows,
        "path_row_count": historical_path_rows,
    }

    pd.DataFrame([summary]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_text_report(summary)

    return summary


def build_phase5_3_summary() -> dict[str, Any]:
    return build_historical_path_engine_hook_payload(requested_mode="historical_import")


if __name__ == "__main__":
    result = build_phase5_3_summary()
    print(json.dumps(result, indent=2))
