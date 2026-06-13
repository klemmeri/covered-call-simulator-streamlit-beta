"""
run_paid_simulator_phase5_11_price_paths_promotion_check.py

Checkpoint runner for Phase 5-11 price_paths.py candidate promotion.
"""

from __future__ import annotations

import importlib.util
import json
import py_compile
import sys
import traceback
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_SIMULATOR_DIR = APP_DIR / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

DASHBOARD_FILE = PAID_SIMULATOR_DIR / "config_form_app.py"
LIVE_PRICE_PATHS_FILE = APP_DIR / "price_paths.py"
MODULE_FILE = PAID_SIMULATOR_DIR / "phase5_price_paths_candidate_promotion.py"
DOC_FILE = DOCS_DIR / "phase5_11_price_paths_candidate_promotion.md"

SUMMARY_CSV = OUTPUT_TABLES_DIR / "phase5_11_price_paths_candidate_promotion_summary.csv"
SYNTHETIC_PREVIEW_CSV = OUTPUT_TABLES_DIR / "phase5_11_live_price_paths_synthetic_preview.csv"
HISTORICAL_PREVIEW_CSV = OUTPUT_TABLES_DIR / "phase5_11_live_price_paths_historical_preview.csv"
JSON_REPORT = OUTPUT_REPORTS_DIR / "phase5_11_price_paths_candidate_promotion.json"
TEXT_REPORT = OUTPUT_REPORTS_DIR / "phase5_11_price_paths_candidate_promotion_report.txt"
CHECKPOINT_REPORT = OUTPUT_REPORTS_DIR / "phase5_11_price_paths_candidate_promotion_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORTS_DIR / "phase5_11_price_paths_candidate_promotion_checkpoint.json"


def _print_header(title: str) -> None:
    print("=" * 100)
    print(title)
    print("=" * 100)


def _record(results: list[dict], passed: bool, label: str, detail: object = "") -> None:
    status = "PASS" if passed else "FAIL"
    print(f"{status:<10} {label:<70} {detail}")
    results.append({"status": status, "label": label, "detail": str(detail)})


def _compile(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "syntax valid"
    except Exception as exc:
        return False, str(exc)


def _import_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    OUTPUT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    _print_header("Phase 5-11 price_paths.py candidate promotion check")
    print(f"Project root: {PROJECT_ROOT}")
    print()

    results: list[dict] = []
    summary = None

    _record(results, DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    _record(results, LIVE_PRICE_PATHS_FILE.exists(), "Live price_paths.py file exists", LIVE_PRICE_PATHS_FILE)
    _record(results, MODULE_FILE.exists(), "Phase 5-11 promotion module exists", MODULE_FILE)
    _record(results, DOC_FILE.exists(), "Phase 5-11 documentation exists", DOC_FILE)

    for label, path in [
        ("Dashboard syntax remains valid", DASHBOARD_FILE),
        ("Promoted live price_paths.py syntax valid", LIVE_PRICE_PATHS_FILE),
        ("Phase 5-11 module syntax valid", MODULE_FILE),
    ]:
        if path.exists():
            ok, detail = _compile(path)
            _record(results, ok, label, detail)
        else:
            _record(results, False, label, "file missing")

    try:
        module = _import_module(MODULE_FILE, "phase5_price_paths_candidate_promotion")
        summary = module.build_phase5_11_summary()
        _record(results, isinstance(summary, dict), "Phase 5-11 module imports and builds promotion report", type(summary).__name__)
    except Exception as exc:
        _record(results, False, "Phase 5-11 module imports and builds promotion report", exc)
        traceback.print_exc()

    if isinstance(summary, dict):
        _record(results, summary.get("ready_marker") == "PHASE5_11_PRICE_PATHS_CANDIDATE_PROMOTED_READY", "Promotion has ready marker", summary.get("ready_marker"))
        _record(results, summary.get("release_decision") == "PHASE5_11_PRICE_PATHS_PROMOTED_SYNTHETIC_DEFAULT_NO_DASHBOARD_CHANGE", "Promotion has release decision", summary.get("release_decision"))
        _record(results, summary.get("dashboard_change_required") is False, "Promotion confirms no dashboard change", summary.get("dashboard_change_required"))
        _record(results, summary.get("customer_workflow_change_required") is False, "Promotion confirms no customer workflow change", summary.get("customer_workflow_change_required"))
        _record(results, summary.get("live_price_paths_promoted") is True, "Live price_paths.py promoted", summary.get("live_price_paths_promoted"))
        _record(results, summary.get("live_engine_file_replaced") is True, "Live engine file replaced intentionally", summary.get("live_engine_file_replaced"))
        _record(results, summary.get("public_function_preserved") is True, "generate_price_paths function preserved", summary.get("public_function_preserved"))
        _record(results, summary.get("synthetic_default_preserved") is True, "Synthetic default remains preserved", summary.get("synthetic_default_preserved"))
        _record(results, summary.get("historical_mode_explicit_only") is True, "Historical mode remains explicit only", summary.get("historical_mode_explicit_only"))
        _record(results, summary.get("unknown_mode_falls_back_to_synthetic") is True, "Unknown mode falls back to synthetic", summary.get("unknown_mode_falls_back_to_synthetic"))
        _record(results, summary.get("default_source_mode") == "synthetic", "Default source mode is synthetic", summary.get("default_source_mode"))
        _record(results, summary.get("historical_source_mode") == "historical_import", "Historical source mode is historical_import", summary.get("historical_source_mode"))
        _record(results, int(summary.get("synthetic_preview_rows", 0)) > 0, "Synthetic preview has rows", summary.get("synthetic_preview_rows"))
        _record(results, int(summary.get("historical_preview_rows", 0)) > 0, "Historical preview has rows", summary.get("historical_preview_rows"))
        _record(results, int(summary.get("synthetic_positive_price_count", 0)) > 0, "Synthetic preview has positive prices", summary.get("synthetic_positive_price_count"))
        _record(results, int(summary.get("historical_positive_price_count", 0)) > 0, "Historical preview has positive prices", summary.get("historical_positive_price_count"))

    for label, path in [
        ("Output written: synthetic_preview_csv", SYNTHETIC_PREVIEW_CSV),
        ("Output written: historical_preview_csv", HISTORICAL_PREVIEW_CSV),
        ("Output written: summary_csv", SUMMARY_CSV),
        ("Output written: json", JSON_REPORT),
        ("Output written: report", TEXT_REPORT),
    ]:
        _record(results, path.exists(), label, path)

    if SYNTHETIC_PREVIEW_CSV.exists():
        try:
            df = pd.read_csv(SYNTHETIC_PREVIEW_CSV)
            _record(results, len(df) > 0 and "price" in df.columns, "Synthetic preview CSV has expected content", f"rows={len(df)}")
        except Exception as exc:
            _record(results, False, "Synthetic preview CSV has expected content", exc)

    all_passed = all(row["status"] == "PASS" for row in results)
    print()
    _print_header(f"Overall Phase 5-11 checkpoint status: {'PASS' if all_passed else 'FAIL'}")

    CHECKPOINT_REPORT.write_text(
        "\n".join([f"{row['status']:<10} {row['label']:<70} {row['detail']}" for row in results]),
        encoding="utf-8",
    )
    CHECKPOINT_JSON.write_text(json.dumps({"overall_status": "PASS" if all_passed else "FAIL", "checks": results}, indent=2), encoding="utf-8")
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
