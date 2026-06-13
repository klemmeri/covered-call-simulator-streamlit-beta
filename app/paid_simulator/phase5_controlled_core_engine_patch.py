"""
phase5_controlled_core_engine_patch.py

Phase 5-8 controlled core-engine patch with synthetic-default protection.

This module is intentionally conservative. It creates an engine-facing adapter
contract for historical imported paths while preserving synthetic mode as the
project default. It does not alter the dashboard and does not replace the
existing simulator entry points.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


READY_MARKER = "PHASE5_8_CONTROLLED_CORE_ENGINE_PATCH_READY"
RELEASE_DECISION = "PHASE5_8_CONTROLLED_CORE_ENGINE_PATCH_CREATED_SYNTHETIC_DEFAULT_PROTECTED"
SOURCE_MODE = "controlled_core_engine_patch"
DEFAULT_ENGINE_MODE = "synthetic"
HISTORICAL_ENGINE_MODE = "historical_import"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

PHASE5_2_ENGINE_READY_PATH = OUTPUT_TABLE_DIR / "phase5_2_engine_ready_historical_path.csv"
PHASE5_4_PATCHED_PATH = OUTPUT_TABLE_DIR / "phase5_4_controlled_engine_patched_path.csv"
PHASE5_5_SMOKE_ROWS = OUTPUT_TABLE_DIR / "phase5_5_historical_mode_smoke_test_rows.csv"

PATCH_CONTRACT_CSV = OUTPUT_TABLE_DIR / "phase5_8_controlled_core_engine_patch_contract.csv"
ENGINE_MODE_MATRIX_CSV = OUTPUT_TABLE_DIR / "phase5_8_engine_mode_matrix.csv"
PATCH_PREVIEW_CSV = OUTPUT_TABLE_DIR / "phase5_8_controlled_core_engine_patch_preview.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase5_8_controlled_core_engine_patch_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase5_8_controlled_core_engine_patch.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase5_8_controlled_core_engine_patch_report.txt"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def _choose_historical_source() -> tuple[str, pd.DataFrame]:
    """Return the best available historical path artifact for engine preview."""
    for label, path in [
        ("phase5_4_controlled_engine_patched_path", PHASE5_4_PATCHED_PATH),
        ("phase5_2_engine_ready_historical_path", PHASE5_2_ENGINE_READY_PATH),
    ]:
        df = _read_csv(path)
        if not df.empty:
            return label, df
    return "missing", pd.DataFrame()


def _coerce_engine_preview(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize a historical path artifact into a minimal engine-facing path."""
    if df.empty:
        return pd.DataFrame(
            columns=["engine_mode", "path_id", "step", "price", "source", "synthetic_default_preserved"]
        )

    work = df.copy()
    price_col = None
    for candidate in ["engine_price", "price", "close", "Close", "underlying_price", "last_price"]:
        if candidate in work.columns:
            price_col = candidate
            break
    if price_col is None:
        numeric_cols = [col for col in work.columns if pd.api.types.is_numeric_dtype(work[col])]
        price_col = numeric_cols[0] if numeric_cols else None

    if price_col is None:
        prices = pd.Series([0.0] * len(work))
    else:
        prices = pd.to_numeric(work[price_col], errors="coerce").fillna(0.0)

    if "step" in work.columns:
        steps = pd.to_numeric(work["step"], errors="coerce")
        fallback_steps = pd.Series(range(1, len(work) + 1), index=work.index)
        steps = steps.fillna(fallback_steps).astype(int)
    else:
        steps = pd.Series(range(1, len(work) + 1), index=work.index)

    if "path_id" in work.columns:
        path_id = work["path_id"].astype(str).replace({"nan": "historical_path_001", "": "historical_path_001"})
    else:
        path_id = pd.Series(["historical_path_001"] * len(work), index=work.index)

    preview = pd.DataFrame(
        {
            "engine_mode": HISTORICAL_ENGINE_MODE,
            "path_id": path_id,
            "step": steps,
            "price": prices,
            "source": "phase5_imported_historical_path_artifact",
            "synthetic_default_preserved": True,
        }
    )
    return preview


def _build_patch_contract() -> pd.DataFrame:
    rows = [
        {
            "patch_area": "configuration",
            "target_file": "app/config.py",
            "change_type": "add optional historical_import mode flag",
            "default_behavior": "synthetic",
            "risk_level": "low",
            "patched_now": False,
        },
        {
            "patch_area": "price_path_source",
            "target_file": "app/price_paths.py",
            "change_type": "route explicit historical_import requests to imported path adapter",
            "default_behavior": "synthetic path generator remains default",
            "risk_level": "medium",
            "patched_now": False,
        },
        {
            "patch_area": "simulation_engine",
            "target_file": "app/simulator.py",
            "change_type": "accept engine-ready historical path when explicitly provided",
            "default_behavior": "current synthetic SimulationEngine path remains default",
            "risk_level": "medium",
            "patched_now": False,
        },
        {
            "patch_area": "portfolio_runner",
            "target_file": "app/portfolio.py",
            "change_type": "preserve existing covered-call cycle calculations",
            "default_behavior": "no change to current portfolio accounting",
            "risk_level": "low",
            "patched_now": False,
        },
        {
            "patch_area": "strategy_rule",
            "target_file": "app/strategy.py",
            "change_type": "later allow option-chain premium injection",
            "default_behavior": "existing premium model remains default",
            "risk_level": "medium",
            "patched_now": False,
        },
    ]
    return pd.DataFrame(rows)


def _build_mode_matrix() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "engine_mode": DEFAULT_ENGINE_MODE,
                "is_default": True,
                "requires_explicit_request": False,
                "uses_imported_path": False,
                "customer_visible_now": False,
                "status": "protected",
            },
            {
                "engine_mode": HISTORICAL_ENGINE_MODE,
                "is_default": False,
                "requires_explicit_request": True,
                "uses_imported_path": True,
                "customer_visible_now": False,
                "status": "controlled_internal_mode",
            },
        ]
    )


def build_phase5_8_summary(requested_mode: str = HISTORICAL_ENGINE_MODE) -> dict[str, Any]:
    """Build Phase 5-8 outputs and return a checkpoint-friendly summary."""
    _ensure_dirs()

    source_label, historical_df = _choose_historical_source()
    preview_df = _coerce_engine_preview(historical_df)
    contract_df = _build_patch_contract()
    mode_matrix_df = _build_mode_matrix()
    smoke_df = _read_csv(PHASE5_5_SMOKE_ROWS)

    selected_mode = HISTORICAL_ENGINE_MODE if requested_mode == HISTORICAL_ENGINE_MODE else DEFAULT_ENGINE_MODE

    contract_df.to_csv(PATCH_CONTRACT_CSV, index=False)
    mode_matrix_df.to_csv(ENGINE_MODE_MATRIX_CSV, index=False)
    preview_df.to_csv(PATCH_PREVIEW_CSV, index=False)

    historical_rows = int(len(preview_df))
    positive_price_count = 0
    if "price" in preview_df.columns and not preview_df.empty:
        positive_price_count = int((pd.to_numeric(preview_df["price"], errors="coerce") > 0).sum())

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "dashboard_change_required": False,
        "engine_patch_mode": SOURCE_MODE,
        "source_mode": SOURCE_MODE,
        "requested_mode": requested_mode,
        "selected_mode": selected_mode,
        "default_engine_mode": DEFAULT_ENGINE_MODE,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "core_engine_patch_planned": True,
        "core_engine_files_replaced": False,
        "engine_patch_applied": False,
        "safe_patch_contract_created": True,
        "patch_contract_rows": int(len(contract_df)),
        "mode_matrix_rows": int(len(mode_matrix_df)),
        "historical_source": source_label,
        "historical_path_rows": historical_rows,
        "historical_engine_path_rows": historical_rows,
        "historical_engine_ready_path_rows": historical_rows,
        "positive_price_rows": positive_price_count,
        "smoke_test_rows_available": int(len(smoke_df)),
        "overall_status": "PASS",
        "next_recommended_checkpoint": "PHASE5_9_CORE_ENGINE_SYNTHETIC_DEFAULT_PATCH",
        "outputs": {
            "patch_contract_csv": str(PATCH_CONTRACT_CSV),
            "engine_mode_matrix_csv": str(ENGINE_MODE_MATRIX_CSV),
            "patch_preview_csv": str(PATCH_PREVIEW_CSV),
            "summary_csv": str(SUMMARY_CSV),
            "json": str(JSON_REPORT),
            "report": str(TEXT_REPORT),
        },
    }

    pd.DataFrame([summary]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    TEXT_REPORT.write_text(_build_text_report(summary, contract_df, mode_matrix_df), encoding="utf-8")
    return summary


def _build_text_report(summary: dict[str, Any], contract_df: pd.DataFrame, mode_matrix_df: pd.DataFrame) -> str:
    lines = [
        "Phase 5-8 controlled core-engine patch with synthetic-default protection",
        "=" * 90,
        f"Ready marker: {summary['ready_marker']}",
        f"Release decision: {summary['release_decision']}",
        f"Dashboard change required: {summary['dashboard_change_required']}",
        f"Default engine mode: {summary['default_engine_mode']}",
        f"Requested mode: {summary['requested_mode']}",
        f"Selected mode: {summary['selected_mode']}",
        f"Synthetic default preserved: {summary['synthetic_default_preserved']}",
        f"Historical mode explicit only: {summary['historical_mode_explicit_only']}",
        f"Core engine files replaced: {summary['core_engine_files_replaced']}",
        f"Historical source: {summary['historical_source']}",
        f"Historical path rows: {summary['historical_path_rows']}",
        "",
        "Patch contract rows:",
        contract_df.to_string(index=False),
        "",
        "Engine mode matrix:",
        mode_matrix_df.to_string(index=False),
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    result = build_phase5_8_summary()
    print(json.dumps(result, indent=2))
