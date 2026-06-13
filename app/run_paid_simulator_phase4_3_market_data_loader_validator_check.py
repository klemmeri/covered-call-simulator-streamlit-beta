"""
run_paid_simulator_phase4_3_market_data_loader_validator_check.py

Checkpoint script for Phase 4-3: Market-data loader and schema validator.

Run from PyCharm with:

    app\run_paid_simulator_phase4_3_market_data_loader_validator_check.py

Expected final status:

    Overall Phase 4-3 checkpoint status: PASS
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
PHASE4_3_DOC = PROJECT_ROOT / "docs" / "phase4_3_market_data_loader_validator.md"
PRIOR_PHASE3_REPORT = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3j_5_completion_handoff_checkpoint_report.txt"

CHECKPOINT_REPORT = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase4_3_market_data_loader_validator_checkpoint_report.txt"
CHECKPOINT_JSON = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase4_3_market_data_loader_validator_checkpoint.json"

EXPECTED_OUTPUTS = {
    "validation_json": PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase4_3_market_data_validation.json",
    "validation_report": PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase4_3_market_data_validation_report.txt",
    "summary_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase4_3_market_data_validation_summary.csv",
    "issues_csv": PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase4_3_market_data_validation_issues.csv",
}


class CheckRecorder:
    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def add(self, status: str, name: str, detail: str = "") -> None:
        self.rows.append({"status": status, "name": name, "detail": detail})
        print(f"{status:<10} {name:<70} {detail}")

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
    lines.append("Phase 4-3 market-data loader and schema-validator checkpoint report")
    lines.append("=" * 88)
    lines.append("")
    for row in recorder.rows:
        lines.append(f"{row['status']:<10} {row['name']:<70} {row['detail']}")
    lines.append("")
    lines.append(f"Overall Phase 4-3 checkpoint status: {overall_status}")
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
    print("Phase 4-3 market-data loader and schema-validator check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print("")

    recorder = CheckRecorder()

    recorder.add("PASS" if DASHBOARD_FILE.exists() else "FAIL", "Dashboard file exists", str(DASHBOARD_FILE))
    recorder.add("PASS" if PHASE4_2_FILE.exists() else "FAIL", "Prior Phase 4-2 scaffold module exists", str(PHASE4_2_FILE))
    recorder.add("PASS" if PHASE4_3_FILE.exists() else "FAIL", "Phase 4-3 loader-validator module exists", str(PHASE4_3_FILE))
    recorder.add("PASS" if PHASE4_3_DOC.exists() else "FAIL", "Phase 4-3 documentation exists", str(PHASE4_3_DOC))

    for label, path in [
        ("Dashboard syntax remains valid", DASHBOARD_FILE),
        ("Phase 4-3 module syntax valid", PHASE4_3_FILE),
    ]:
        if path.exists():
            ok, detail = _syntax_check(path)
            recorder.add("PASS" if ok else "FAIL", label, detail)
        else:
            recorder.add("FAIL", label, f"missing file: {path}")

    validation_summary = None
    try:
        module = _import_module(PHASE4_3_FILE, "phase4_market_data_loader_validator")
        validation_summary = module.build_phase4_3_summary()
        recorder.add("PASS", "Phase 4-3 module imports and validates", type(validation_summary).__name__)
    except Exception as exc:
        recorder.add("FAIL", "Phase 4-3 module imports and validates", f"{exc}")
        traceback.print_exc()

    if isinstance(validation_summary, dict):
        recorder.add(
            "PASS" if validation_summary.get("ready_marker") == "PHASE4_3_MARKET_DATA_LOADER_VALIDATOR_READY" else "FAIL",
            "Loader-validator has ready marker",
            str(validation_summary.get("ready_marker")),
        )
        recorder.add(
            "PASS" if validation_summary.get("release_decision") == "PHASE4_3_MARKET_DATA_LOADER_VALIDATOR_CREATED_NO_DASHBOARD_CHANGE" else "FAIL",
            "Loader-validator has release decision",
            str(validation_summary.get("release_decision")),
        )
        recorder.add(
            "PASS" if validation_summary.get("dashboard_change_required") is False else "FAIL",
            "Loader-validator confirms no dashboard change",
            str(validation_summary.get("dashboard_change_required")),
        )
        recorder.add(
            "PASS" if validation_summary.get("overall_status") == "PASS" else "FAIL",
            "Market-data validation overall status is PASS",
            str(validation_summary.get("overall_status")),
        )

        underlying = validation_summary.get("underlying", {})
        option_chain = validation_summary.get("option_chain", {})
        recorder.add(
            "PASS" if underlying.get("status") == "PASS" else "FAIL",
            "Underlying price sample validates",
            str(underlying.get("status")),
        )
        recorder.add(
            "PASS" if option_chain.get("status") == "PASS" else "FAIL",
            "Option-chain sample validates",
            str(option_chain.get("status")),
        )
        recorder.add(
            "PASS" if int(underlying.get("row_count", 0)) > 0 else "FAIL",
            "Underlying price sample has rows",
            str(underlying.get("row_count")),
        )
        recorder.add(
            "PASS" if int(option_chain.get("row_count", 0)) > 0 else "FAIL",
            "Option-chain sample has rows",
            str(option_chain.get("row_count")),
        )
        recorder.add(
            "PASS" if int(underlying.get("required_column_count", 0)) >= 7 else "FAIL",
            "Underlying required-column count present",
            str(underlying.get("required_column_count")),
        )
        recorder.add(
            "PASS" if int(option_chain.get("required_column_count", 0)) >= 12 else "FAIL",
            "Option-chain required-column count present",
            str(option_chain.get("required_column_count")),
        )
    else:
        recorder.add("FAIL", "Validation summary produced", "summary was not a dict")

    for label, path in EXPECTED_OUTPUTS.items():
        recorder.add("PASS" if path.exists() else "FAIL", f"Output written: {label}", str(path))

    recorder.add("PASS" if PRIOR_PHASE3_REPORT.exists() else "FAIL", "Prior Phase 3 completion report exists", str(PRIOR_PHASE3_REPORT))

    overall_status = "PASS" if recorder.passed else "FAIL"

    _write_checkpoint_files(recorder, overall_status)

    print("")
    print("=" * 100)
    print(f"Overall Phase 4-3 checkpoint status: {overall_status}")
    print("=" * 100)
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if overall_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
