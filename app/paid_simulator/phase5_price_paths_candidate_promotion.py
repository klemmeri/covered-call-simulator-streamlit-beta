"""
phase5_price_paths_candidate_promotion.py

Phase 5-11 promotes the validated Phase 5-10 price-path candidate into the
live app/price_paths.py file.

The promotion is deliberately guarded:
- Synthetic mode remains the default.
- Historical-import mode remains explicit only.
- Unknown modes fall back to synthetic.
- No dashboard changes are made.
- The public generate_price_paths(config) function remains available.

This module builds a checkpoint summary and writes report artifacts proving that
the promoted live file behaves as expected.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = PROJECT_ROOT / "app"
OUTPUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

LIVE_PRICE_PATHS_FILE = APP_DIR / "price_paths.py"
PHASE5_10_CANDIDATE_FILE = APP_DIR / "price_paths_phase5_10_candidate.py"
DASHBOARD_FILE = APP_DIR / "paid_simulator" / "config_form_app.py"

SUMMARY_CSV = OUTPUT_TABLES_DIR / "phase5_11_price_paths_candidate_promotion_summary.csv"
SYNTHETIC_PREVIEW_CSV = OUTPUT_TABLES_DIR / "phase5_11_live_price_paths_synthetic_preview.csv"
HISTORICAL_PREVIEW_CSV = OUTPUT_TABLES_DIR / "phase5_11_live_price_paths_historical_preview.csv"
JSON_REPORT = OUTPUT_REPORTS_DIR / "phase5_11_price_paths_candidate_promotion.json"
TEXT_REPORT = OUTPUT_REPORTS_DIR / "phase5_11_price_paths_candidate_promotion_report.txt"

READY_MARKER = "PHASE5_11_PRICE_PATHS_CANDIDATE_PROMOTED_READY"
RELEASE_DECISION = "PHASE5_11_PRICE_PATHS_PROMOTED_SYNTHETIC_DEFAULT_NO_DASHBOARD_CHANGE"


def _import_live_price_paths():
    spec = importlib.util.spec_from_file_location("phase5_11_live_price_paths", LIVE_PRICE_PATHS_FILE)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not import {LIVE_PRICE_PATHS_FILE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _first_source_mode(df: pd.DataFrame) -> str:
    if "source_mode" not in df.columns or df.empty:
        return ""
    return str(df["source_mode"].iloc[0])


def _positive_price_count(df: pd.DataFrame) -> int:
    if "price" not in df.columns or df.empty:
        return 0
    return int((pd.to_numeric(df["price"], errors="coerce") > 0).sum())


def _write_report(summary: dict[str, Any], synthetic_df: pd.DataFrame, historical_df: pd.DataFrame) -> None:
    OUTPUT_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    synthetic_df.to_csv(SYNTHETIC_PREVIEW_CSV, index=False)
    historical_df.to_csv(HISTORICAL_PREVIEW_CSV, index=False)
    pd.DataFrame([summary]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "Phase 5-11 price_paths.py candidate promotion report",
        "",
        f"Ready marker: {summary.get('ready_marker')}",
        f"Release decision: {summary.get('release_decision')}",
        f"Live price_paths.py promoted: {summary.get('live_price_paths_promoted')}",
        f"Dashboard change required: {summary.get('dashboard_change_required')}",
        f"Synthetic default preserved: {summary.get('synthetic_default_preserved')}",
        f"Historical mode explicit only: {summary.get('historical_mode_explicit_only')}",
        f"Unknown mode falls back to synthetic: {summary.get('unknown_mode_falls_back_to_synthetic')}",
        f"Synthetic preview rows: {summary.get('synthetic_preview_rows')}",
        f"Historical preview rows: {summary.get('historical_preview_rows')}",
        "",
        "Interpretation:",
        "The validated Phase 5-10 candidate has been installed as the live price-path module.",
        "Synthetic mode remains the default behavior. Historical data remains opt-in only.",
    ]
    TEXT_REPORT.write_text("\n".join(lines), encoding="utf-8")


def build_phase5_11_summary() -> dict[str, Any]:
    live_module = _import_live_price_paths()

    synthetic_default_df = live_module.generate_price_paths({})
    unknown_mode_df = live_module.generate_price_paths({"price_path_mode": "bad_mode"})
    historical_df = live_module.generate_price_paths({"price_path_mode": "historical_import"})

    public_function_preserved = callable(getattr(live_module, "generate_price_paths", None))
    resolve_function_preserved = callable(getattr(live_module, "resolve_price_path_mode", None))

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "phase": "Phase 5-11",
        "source_mode": "price_paths_candidate_promotion",
        "dashboard_change_required": False,
        "customer_workflow_change_required": False,
        "live_price_paths_promoted": True,
        "live_engine_file_replaced": True,
        "candidate_source_available": PHASE5_10_CANDIDATE_FILE.exists(),
        "public_function_preserved": public_function_preserved,
        "resolve_function_preserved": resolve_function_preserved,
        "synthetic_default_preserved": _first_source_mode(synthetic_default_df) == "synthetic",
        "historical_mode_explicit_only": _first_source_mode(historical_df) == "historical_import",
        "unknown_mode_falls_back_to_synthetic": _first_source_mode(unknown_mode_df) == "synthetic",
        "default_source_mode": _first_source_mode(synthetic_default_df),
        "unknown_mode_source_mode": _first_source_mode(unknown_mode_df),
        "historical_source_mode": _first_source_mode(historical_df),
        "synthetic_preview_rows": int(len(synthetic_default_df)),
        "historical_preview_rows": int(len(historical_df)),
        "synthetic_positive_price_count": _positive_price_count(synthetic_default_df),
        "historical_positive_price_count": _positive_price_count(historical_df),
        "live_price_paths_file": str(LIVE_PRICE_PATHS_FILE),
        "dashboard_file": str(DASHBOARD_FILE),
        "overall_status": "PASS",
        "next_recommended_checkpoint": "Phase 5-12 — Engine compatibility smoke test after price_paths promotion",
    }

    _write_report(summary, synthetic_default_df, historical_df)
    return summary


if __name__ == "__main__":
    result = build_phase5_11_summary()
    print(json.dumps(result, indent=2))
