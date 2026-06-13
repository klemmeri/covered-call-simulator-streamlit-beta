"""
run_paid_simulator_phase4_4_historical_price_path_adapter_check.py

Checkpoint script for Phase 4-4: Historical price path input adapter.

Run from PyCharm with:

    app\run_paid_simulator_phase4_4_historical_price_path_adapter_check.py

Expected final status:

    Overall Phase 4-4 checkpoint status: PASS
"""

from __future__ import annotations

from pathlib import Path
import ast
import importlib.util
import json
import sys
import traceback


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
PHASE4_2_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase4_market_data_input_scaffold.py"
PHASE4_3_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase4_market_data_loader_validator.py"
PHASE4_4_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase4_historical_price_path_adapter.py"
PHASE4_4_DOC = PROJECT_ROOT / "docs" / "phase4_4_historical_price_path_adapter.md"

CHECKPOINT_REPORT = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase4_4_historical_price_path_adapter_checkpoint_report.txt"
CHECKPOINT_JSON = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase4_4_historical_price_path_adapter_checkpoint.json"

EXPECTED_OUTPUTS = {
    "path_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase4_4_historical_price_path.csv",
    "normalized_prices_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase4_4_normalized_underlying_prices.csv",
    "summary_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase4_4_historical_price_path_summary.csv",
    "json": PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase4_4_historical_price_path_adapter.json",
    "report": PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase4_4_historical_price_path_adapter_report.txt",
}


class CheckRecorder:
    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def add(self, status: str, name: str, detail: str = "") -> None:
        self.rows.append({"status": status, "name": name, "detail": detail})
        print(f"{status:<10} {name:<76} {detail}")

    @property
    def passed(self) -> bool:
        return all(row["status"] == "PASS" for row in self.rows)


def _syntax_check(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:
        return False, f"syntax invalid: {exc}"


def _import_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_checkpoint_files(recorder: CheckRecorder, overall_status: str) -> None:
    CHECKPOINT_REPORT.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("Phase 4-4 historical price path adapter checkpoint report")
    lines.append("=" * 92)
    lines.append("")
    for row in recorder.rows:
        lines.append(f"{row['status']:<10} {row['name']:<76} {row['detail']}")
    lines.append("")
    lines.append(f"Overall Phase 4-4 checkpoint status: {overall_status}")
    CHECKPOINT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    CHECKPOINT_JSON.write_text(
        json.dumps(
            {
                "overall_status": overall_status,
                "checks": recorder.rows,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> int:
    print("=" * 100)
    print("Phase 4-4 historical price path input adapter check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print("")

    recorder = CheckRecorder()

    recorder.add("PASS" if DASHBOARD_FILE.exists() else "FAIL", "Dashboard file exists", str(DASHBOARD_FILE))
    recorder.add("PASS" if PHASE4_2_FILE.exists() else "FAIL", "Prior Phase 4-2 scaffold module exists", str(PHASE4_2_FILE))
    recorder.add("PASS" if PHASE4_3_FILE.exists() else "FAIL", "Prior Phase 4-3 loader-validator module exists", str(PHASE4_3_FILE))
    recorder.add("PASS" if PHASE4_4_FILE.exists() else "FAIL", "Phase 4-4 historical-path adapter module exists", str(PHASE4_4_FILE))
    recorder.add("PASS" if PHASE4_4_DOC.exists() else "FAIL", "Phase 4-4 documentation exists", str(PHASE4_4_DOC))

    for label, path in [
        ("Dashboard syntax remains valid", DASHBOARD_FILE),
        ("Phase 4-4 module syntax valid", PHASE4_4_FILE),
    ]:
        if path.exists():
            ok, detail = _syntax_check(path)
            recorder.add("PASS" if ok else "FAIL", label, detail)
        else:
            recorder.add("FAIL", label, f"missing file: {path}")

    summary = None
    try:
        module = _import_module(PHASE4_4_FILE, "phase4_historical_price_path_adapter")
        summary = module.build_phase4_4_summary()
        recorder.add("PASS", "Phase 4-4 module imports and builds historical path", type(summary).__name__)
    except Exception as exc:
        recorder.add("FAIL", "Phase 4-4 module imports and builds historical path", f"{exc}")
        traceback.print_exc()

    if isinstance(summary, dict):
        recorder.add(
            "PASS" if summary.get("ready_marker") == "PHASE4_4_HISTORICAL_PRICE_PATH_ADAPTER_READY" else "FAIL",
            "Historical-path adapter has ready marker",
            str(summary.get("ready_marker")),
        )
        recorder.add(
            "PASS" if summary.get("release_decision") == "PHASE4_4_HISTORICAL_PRICE_PATH_ADAPTER_CREATED_NO_DASHBOARD_CHANGE" else "FAIL",
            "Historical-path adapter has release decision",
            str(summary.get("release_decision")),
        )
        recorder.add(
            "PASS" if summary.get("dashboard_change_required") is False else "FAIL",
            "Historical-path adapter confirms no dashboard change",
            str(summary.get("dashboard_change_required")),
        )
        recorder.add(
            "PASS" if summary.get("overall_status") == "PASS" else "FAIL",
            "Historical-path adapter overall status is PASS",
            str(summary.get("overall_status")),
        )
        recorder.add(
            "PASS" if summary.get("source_mode") == "historical_import" else "FAIL",
            "Historical-path adapter uses historical-import mode",
            str(summary.get("source_mode")),
        )
        recorder.add(
            "PASS" if int(summary.get("row_count", 0)) > 0 else "FAIL",
            "Underlying price input has rows",
            str(summary.get("row_count")),
        )
        recorder.add(
            "PASS" if int(summary.get("path_row_count", 0)) > 0 else "FAIL",
            "Historical path output has rows",
            str(summary.get("path_row_count")),
        )
        recorder.add(
            "PASS" if str(summary.get("path_id", "")).startswith("historical_") else "FAIL",
            "Historical path ID is present",
            str(summary.get("path_id")),
        )
        recorder.add(
            "PASS" if float(summary.get("first_price", 0.0)) > 0 else "FAIL",
            "Historical path first price is positive",
            str(summary.get("first_price")),
        )
        recorder.add(
            "PASS" if float(summary.get("last_price", 0.0)) > 0 else "FAIL",
            "Historical path last price is positive",
            str(summary.get("last_price")),
        )
    else:
        recorder.add("FAIL", "Historical-path summary produced", "summary was not a dict")

    for label, path in EXPECTED_OUTPUTS.items():
        recorder.add("PASS" if path.exists() else "FAIL", f"Output written: {label}", str(path))

    overall_status = "PASS" if recorder.passed else "FAIL"
    _write_checkpoint_files(recorder, overall_status)

    print("")
    print("=" * 100)
    print(f"Overall Phase 4-4 checkpoint status: {overall_status}")
    print("=" * 100)
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if overall_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
