"""
run_paid_simulator_phase4_2_market_data_input_check.py

Checkpoint for Phase 4-2 market-data input scaffold.
"""

from __future__ import annotations

import ast
import importlib
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"


class CheckReport:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str]] = []

    def add(self, passed: bool, name: str, detail: str = "") -> None:
        self.rows.append(("PASS" if passed else "FAIL", name, detail))

    @property
    def passed(self) -> bool:
        return all(status == "PASS" for status, _, _ in self.rows)

    def print_report(self) -> None:
        print("=" * 100)
        print("Phase 4-2 market-data input scaffold check")
        print("=" * 100)
        print(f"Project root: {PROJECT_ROOT}")
        print()
        for status, name, detail in self.rows:
            print(f"{status:<10} {name:<70} {detail}")
        print()
        print("=" * 100)
        print(f"Overall Phase 4-2 checkpoint status: {'PASS' if self.passed else 'FAIL'}")
        print("=" * 100)

    def write_outputs(self) -> None:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        TABLE_DIR.mkdir(parents=True, exist_ok=True)
        report_path = REPORT_DIR / "phase4_2_market_data_input_checkpoint_report.txt"
        json_path = REPORT_DIR / "phase4_2_market_data_input_checkpoint.json"
        lines = [
            "Phase 4-2 market-data input scaffold check",
            "=" * 100,
            f"Project root: {PROJECT_ROOT}",
            "",
        ]
        lines.extend(f"{status:<10} {name:<70} {detail}" for status, name, detail in self.rows)
        lines.extend(["", "=" * 100, f"Overall Phase 4-2 checkpoint status: {'PASS' if self.passed else 'FAIL'}"])
        report_path.write_text("\n".join(lines), encoding="utf-8")
        json_path.write_text(json.dumps({"passed": self.passed, "rows": self.rows}, indent=2), encoding="utf-8")
        print(f"Saved checkpoint report: {report_path}")
        print(f"Saved checkpoint JSON:   {json_path}")


def syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:
        return False, repr(exc)


def main() -> int:
    report = CheckReport()

    dashboard_path = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
    module_path = PROJECT_ROOT / "app" / "paid_simulator" / "phase4_market_data_input_scaffold.py"
    doc_path = PROJECT_ROOT / "docs" / "phase4_2_data_input_scaffold.md"

    report.add(dashboard_path.exists(), "Dashboard file exists", str(dashboard_path))
    report.add(module_path.exists(), "Phase 4-2 scaffold module exists", str(module_path))
    report.add(doc_path.exists(), "Phase 4-2 documentation exists", str(doc_path))

    if dashboard_path.exists():
        ok, detail = syntax_valid(dashboard_path)
        report.add(ok, "Dashboard syntax remains valid", detail)

    if module_path.exists():
        ok, detail = syntax_valid(module_path)
        report.add(ok, "Phase 4-2 module syntax valid", detail)

    try:
        module = importlib.import_module("app.paid_simulator.phase4_market_data_input_scaffold")
        model = module.render_market_data_input_scaffold()
        report.add(True, "Phase 4-2 module imports and renders", "dict")
        report.add(model.get("ready_marker") == "PHASE4_2_MARKET_DATA_INPUT_SCAFFOLD_READY", "Scaffold model has ready marker", str(model.get("ready_marker")))
        report.add(model.get("release_decision") == "PHASE4_2_MARKET_DATA_INPUT_SCAFFOLD_CREATED_NO_DASHBOARD_CHANGE", "Scaffold model has release decision", str(model.get("release_decision")))
        report.add(model.get("dashboard_changed") is False, "Scaffold confirms no dashboard change", str(model.get("dashboard_changed")))
        report.add(len(model.get("ticker_price_columns", [])) >= 6, "Underlying price schema has core columns", str(len(model.get("ticker_price_columns", []))))
        report.add(len(model.get("option_chain_columns", [])) >= 8, "Option-chain schema has core columns", str(len(model.get("option_chain_columns", []))))
        rules_text = " ".join(model.get("validation_rules", [])).lower()
        for term in ["required", "dates", "non-negative", "ask", "bid", "delta", "iv"]:
            report.add(term in rules_text, f"Validation rule present: {term}", term)
        outputs = module.write_scaffold_outputs(PROJECT_ROOT)
        for name, path_string in outputs.items():
            path = Path(path_string)
            report.add(path.exists(), f"Output written: {name}", str(path))
    except Exception as exc:
        report.add(False, "Phase 4-2 module imports/renders/writes", repr(exc))

    # Check that Phase 3 completion evidence remains available.
    prior = REPORT_DIR / "phase3j_5_completion_handoff_checkpoint_report.txt"
    report.add(prior.exists(), "Prior Phase 3 completion report exists", str(prior))

    report.print_report()
    report.write_outputs()
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
