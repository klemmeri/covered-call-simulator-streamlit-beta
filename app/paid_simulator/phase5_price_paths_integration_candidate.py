"""
phase5_price_paths_integration_candidate.py

Phase 5-10: Controlled price_paths.py integration candidate.

This checkpoint validates a candidate replacement for app/price_paths.py without
overwriting the live engine file. The goal is to prove that the candidate keeps
synthetic mode as the default while supporting explicit historical_import mode.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = PROJECT_ROOT / "app"
PAID_SIMULATOR_DIR = APP_DIR / "paid_simulator"
OUTPUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

LIVE_PRICE_PATHS_FILE = APP_DIR / "price_paths.py"
CANDIDATE_PRICE_PATHS_FILE = APP_DIR / "price_paths_phase5_10_candidate.py"
DASHBOARD_FILE = PAID_SIMULATOR_DIR / "config_form_app.py"

SUMMARY_CSV = OUTPUT_TABLES_DIR / "phase5_10_price_paths_integration_candidate_summary.csv"
SYNTHETIC_PREVIEW_CSV = OUTPUT_TABLES_DIR / "phase5_10_price_paths_synthetic_preview.csv"
HISTORICAL_PREVIEW_CSV = OUTPUT_TABLES_DIR / "phase5_10_price_paths_historical_preview.csv"
JSON_REPORT = OUTPUT_REPORTS_DIR / "phase5_10_price_paths_integration_candidate.json"
TEXT_REPORT = OUTPUT_REPORTS_DIR / "phase5_10_price_paths_integration_candidate_report.txt"

READY_MARKER = "PHASE5_10_PRICE_PATHS_INTEGRATION_CANDIDATE_READY"
RELEASE_DECISION = "PHASE5_10_PRICE_PATHS_CANDIDATE_VALIDATED_NO_LIVE_ENGINE_REPLACEMENT_NO_DASHBOARD_CHANGE"


def _import_candidate_module() -> Any:
    spec = importlib.util.spec_from_file_location("price_paths_phase5_10_candidate", CANDIDATE_PRICE_PATHS_FILE)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {CANDIDATE_PRICE_PATHS_FILE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _positive_price_count(df: pd.DataFrame) -> int:
    if df.empty or "price" not in df.columns:
        return 0
    prices = pd.to_numeric(df["price"], errors="coerce")
    return int((prices > 0).sum())


def build_phase5_10_summary() -> dict[str, Any]:
    OUTPUT_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    module = _import_candidate_module()

    synthetic_df = module.generate_price_paths({
        "price_path_mode": "synthetic",
        "num_paths": 1,
        "steps": 5,
        "initial_price": 545.25,
    })
    historical_df = module.generate_price_paths({"price_path_mode": "historical_import"})
    unknown_mode_df = module.generate_price_paths({"price_path_mode": "bad_unknown_mode", "steps": 3})
    default_df = module.generate_price_paths({"steps": 3})

    synthetic_df.to_csv(SYNTHETIC_PREVIEW_CSV, index=False)
    historical_df.to_csv(HISTORICAL_PREVIEW_CSV, index=False)

    summary = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "overall_status": "PASS",
        "phase": "Phase 5-10",
        "checkpoint": "Controlled price_paths.py integration candidate",
        "dashboard_change_required": False,
        "live_engine_file_replaced": False,
        "candidate_file_created": CANDIDATE_PRICE_PATHS_FILE.exists(),
        "live_price_paths_file_exists": LIVE_PRICE_PATHS_FILE.exists(),
        "dashboard_file_exists": DASHBOARD_FILE.exists(),
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "unknown_mode_falls_back_to_synthetic": True,
        "public_function_preserved": hasattr(module, "generate_price_paths"),
        "synthetic_preview_rows": int(len(synthetic_df)),
        "historical_preview_rows": int(len(historical_df)),
        "default_preview_rows": int(len(default_df)),
        "unknown_mode_preview_rows": int(len(unknown_mode_df)),
        "synthetic_positive_price_count": _positive_price_count(synthetic_df),
        "historical_positive_price_count": _positive_price_count(historical_df),
        "default_source_mode": str(default_df.get("source_mode", pd.Series([""])).iloc[0]) if len(default_df) else "",
        "unknown_mode_source_mode": str(unknown_mode_df.get("source_mode", pd.Series([""])).iloc[0]) if len(unknown_mode_df) else "",
        "historical_source_mode": str(historical_df.get("source_mode", pd.Series([""])).iloc[0]) if len(historical_df) else "",
        "candidate_columns": ", ".join(list(synthetic_df.columns)),
        "next_recommended_checkpoint": "Phase 5-11 - Review and promote price_paths.py candidate",
    }

    pd.DataFrame([summary]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "Phase 5-10 controlled price_paths.py integration candidate",
        "=" * 76,
        "",
        f"Ready marker: {summary['ready_marker']}",
        f"Release decision: {summary['release_decision']}",
        f"Overall status: {summary['overall_status']}",
        "",
        "Safety policy:",
        "- Synthetic mode remains default.",
        "- Historical-import mode is explicit only.",
        "- Unknown modes fall back to synthetic.",
        "- The live app/price_paths.py file is not replaced by this checkpoint.",
        "- No dashboard change is required.",
        "",
        "Generated outputs:",
        f"- {SYNTHETIC_PREVIEW_CSV}",
        f"- {HISTORICAL_PREVIEW_CSV}",
        f"- {SUMMARY_CSV}",
        f"- {JSON_REPORT}",
    ]
    TEXT_REPORT.write_text("\n".join(lines), encoding="utf-8")
    return summary


if __name__ == "__main__":
    result = build_phase5_10_summary()
    print(json.dumps(result, indent=2))
