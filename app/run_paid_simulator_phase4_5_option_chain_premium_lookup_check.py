"""
run_paid_simulator_phase4_5_option_chain_premium_lookup_check.py

Checkpoint script for Phase 4-5: Option-chain premium lookup scaffold.
"""

from __future__ import annotations

import importlib.util
import json
import py_compile
import traceback
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
PHASE4_2_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase4_market_data_input_scaffold.py"
PHASE4_3_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase4_market_data_loader_validator.py"
PHASE4_4_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase4_historical_price_path_adapter.py"
PHASE4_5_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase4_option_chain_premium_lookup.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase4_5_option_chain_premium_lookup.md"
OPTION_CHAIN_INPUT = PROJECT_ROOT / "inputs" / "market_data" / "sample_option_chain.csv"

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
CHECKPOINT_REPORT = REPORT_DIR / "phase4_5_option_chain_premium_lookup_checkpoint_report.txt"
CHECKPOINT_JSON = REPORT_DIR / "phase4_5_option_chain_premium_lookup_checkpoint.json"


def _print_header(title: str) -> None:
    print("=" * 100)
    print(title)
    print("=" * 100)


def _record(results: list[dict], status: bool, label: str, detail: object = "") -> None:
    outcome = "PASS" if status else "FAIL"
    print(f"{outcome:<10} {label:<72} {detail}")
    results.append({"status": outcome, "label": label, "detail": str(detail)})


def _compile(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "syntax valid"
    except Exception as exc:
        return False, str(exc)


def _import_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    summary = None

    _print_header("Phase 4-5 option-chain premium lookup scaffold check")
    print(f"Project root: {PROJECT_ROOT}")
    print()

    for label, path in [
        ("Dashboard file exists", DASHBOARD_FILE),
        ("Prior Phase 4-2 scaffold module exists", PHASE4_2_FILE),
        ("Prior Phase 4-3 loader-validator module exists", PHASE4_3_FILE),
        ("Prior Phase 4-4 historical-path adapter module exists", PHASE4_4_FILE),
        ("Phase 4-5 option-chain lookup module exists", PHASE4_5_FILE),
        ("Phase 4-5 documentation exists", DOC_FILE),
        ("Sample option-chain input exists", OPTION_CHAIN_INPUT),
    ]:
        _record(results, path.exists(), label, path)

    ok, detail = _compile(DASHBOARD_FILE)
    _record(results, ok, "Dashboard syntax remains valid", detail)

    ok, detail = _compile(PHASE4_5_FILE)
    _record(results, ok, "Phase 4-5 module syntax valid", detail)

    try:
        module = _import_module(PHASE4_5_FILE, "phase4_option_chain_premium_lookup")
        summary = module.build_phase4_5_summary()
        _record(results, isinstance(summary, dict), "Phase 4-5 module imports and builds lookup", type(summary).__name__)
    except Exception as exc:
        _record(results, False, "Phase 4-5 module imports and builds lookup", exc)
        traceback.print_exc()

    if isinstance(summary, dict):
        _record(
            results,
            summary.get("ready_marker") == "PHASE4_5_OPTION_CHAIN_PREMIUM_LOOKUP_READY",
            "Option-chain lookup has ready marker",
            summary.get("ready_marker"),
        )
        _record(
            results,
            summary.get("release_decision") == "PHASE4_5_OPTION_CHAIN_PREMIUM_LOOKUP_SCAFFOLD_CREATED_NO_DASHBOARD_CHANGE",
            "Option-chain lookup has release decision",
            summary.get("release_decision"),
        )
        _record(
            results,
            summary.get("dashboard_change_required") is False,
            "Option-chain lookup confirms no dashboard change",
            summary.get("dashboard_change_required"),
        )
        _record(
            results,
            summary.get("source_mode") == "option_chain_import",
            "Option-chain lookup uses option-chain import mode",
            summary.get("source_mode"),
        )
        _record(
            results,
            int(summary.get("raw_option_chain_rows") or 0) > 0,
            "Raw option-chain input has rows",
            summary.get("raw_option_chain_rows"),
        )
        _record(
            results,
            int(summary.get("normalized_option_chain_rows") or 0) > 0,
            "Normalized option-chain output has rows",
            summary.get("normalized_option_chain_rows"),
        )
        _record(
            results,
            int(summary.get("candidate_rows") or 0) > 0,
            "Candidate output has rows",
            summary.get("candidate_rows"),
        )
        _record(
            results,
            summary.get("best_candidate_present") is True,
            "Best covered-call candidate is present",
            summary.get("best_candidate_present"),
        )

    expected_outputs = {
        "candidates_csv": TABLE_DIR / "phase4_5_option_chain_candidates.csv",
        "best_candidate_csv": TABLE_DIR / "phase4_5_best_covered_call_candidate.csv",
        "summary_csv": TABLE_DIR / "phase4_5_option_chain_premium_lookup_summary.csv",
        "json": REPORT_DIR / "phase4_5_option_chain_premium_lookup.json",
        "report": REPORT_DIR / "phase4_5_option_chain_premium_lookup_report.txt",
    }

    for label, path in expected_outputs.items():
        _record(results, path.exists(), f"Output written: {label}", path)

    # Lightweight content check for the best-candidate CSV.
    best_path = expected_outputs["best_candidate_csv"]
    if best_path.exists():
        try:
            best_df = pd.read_csv(best_path)
            has_columns = {"candidate_rank", "strike", "delta", "mid", "dte"}.issubset(set(best_df.columns))
            has_row = len(best_df) >= 1
            _record(results, has_columns and has_row, "Best candidate CSV has expected content", f"rows={len(best_df)}")
        except Exception as exc:
            _record(results, False, "Best candidate CSV has expected content", exc)

    overall_pass = all(item["status"] == "PASS" for item in results)
    overall_status = "PASS" if overall_pass else "FAIL"

    print()
    _print_header(f"Overall Phase 4-5 checkpoint status: {overall_status}")

    checkpoint = {
        "phase": "Phase 4-5",
        "checkpoint": "Option-chain premium lookup scaffold",
        "overall_status": overall_status,
        "results": results,
        "summary": summary,
    }

    CHECKPOINT_REPORT.write_text(
        "\n".join([f"{item['status']:<10} {item['label']:<72} {item['detail']}" for item in results])
        + f"\n\nOverall Phase 4-5 checkpoint status: {overall_status}\n",
        encoding="utf-8",
    )
    CHECKPOINT_JSON.write_text(json.dumps(checkpoint, indent=2, default=str), encoding="utf-8")

    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
