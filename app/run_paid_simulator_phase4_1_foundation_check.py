"""
run_paid_simulator_phase4_1_foundation_check.py

Phase 4-1 foundation checkpoint for the Covered Call Simulator.
"""

from __future__ import annotations

import ast
import csv
import importlib
import json
from pathlib import Path
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)

DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase4_data_modeling_foundation.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase4_1_data_modeling_foundation.md"

PRIOR_REPORTS = [
    "phase3j_5_completion_handoff_checkpoint_report.txt",
    "phase3j_4_final_production_health_checkpoint_report.txt",
    "phase3i_7_completion_gate_checkpoint_report.txt",
]


def syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:  # pragma: no cover
        return False, repr(exc)


class CheckLog:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(self, ok: bool, label: str, detail: str = "") -> None:
        self.rows.append({"status": "PASS" if ok else "FAIL", "label": label, "detail": detail})

    @property
    def passed(self) -> bool:
        return all(row["status"] == "PASS" for row in self.rows)

    def print_report(self) -> None:
        print("=" * 100)
        print("Phase 4-1 data/modeling foundation check")
        print("=" * 100)
        print(f"Project root: {PROJECT_ROOT}")
        print()
        for row in self.rows:
            print(f"{row['status']:<10} {row['label']:<70} {row['detail']}")
        print()
        print("=" * 100)
        print(f"Overall Phase 4-1 checkpoint status: {'PASS' if self.passed else 'FAIL'}")
        print("=" * 100)

    def write_outputs(self) -> None:
        report_path = REPORT_DIR / "phase4_1_foundation_checkpoint_report.txt"
        json_path = REPORT_DIR / "phase4_1_foundation_checkpoint.json"
        csv_path = TABLE_DIR / "phase4_1_foundation_checklist.csv"
        decision_path = REPORT_DIR / "phase4_1_foundation_release_decision.txt"

        report_lines = [
            "Phase 4-1 data/modeling foundation check",
            f"Project root: {PROJECT_ROOT}",
            "",
        ]
        for row in self.rows:
            report_lines.append(f"{row['status']:<10} {row['label']:<70} {row['detail']}")
        report_lines.extend(["", f"Overall Phase 4-1 checkpoint status: {'PASS' if self.passed else 'FAIL'}"])
        report_path.write_text("\n".join(report_lines), encoding="utf-8")
        json_path.write_text(json.dumps({"passed": self.passed, "checks": self.rows}, indent=2), encoding="utf-8")
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["status", "label", "detail"])
            writer.writeheader()
            writer.writerows(self.rows)
        decision_path.write_text("PHASE4_1_FOUNDATION_CREATED_NO_DASHBOARD_CHANGE\n", encoding="utf-8")


def main() -> int:
    log = CheckLog()

    log.add(DASHBOARD_FILE.exists(), "Dashboard file exists", str(DASHBOARD_FILE))
    log.add(MODULE_FILE.exists(), "Phase 4-1 foundation module exists", str(MODULE_FILE))
    log.add(DOC_FILE.exists(), "Phase 4-1 documentation exists", str(DOC_FILE))

    if DASHBOARD_FILE.exists():
        ok, detail = syntax_valid(DASHBOARD_FILE)
        log.add(ok, "Dashboard syntax remains valid", detail)
    else:
        log.add(False, "Dashboard syntax remains valid", "dashboard missing")

    if MODULE_FILE.exists():
        ok, detail = syntax_valid(MODULE_FILE)
        log.add(ok, "Phase 4-1 module syntax valid", detail)
    else:
        log.add(False, "Phase 4-1 module syntax valid", "module missing")

    try:
        module = importlib.import_module("app.paid_simulator.phase4_data_modeling_foundation")
        model = module.render_phase4_foundation_model(streamlit_module=None)
        log.add(isinstance(model, dict), "Fallback render returns dict", type(model).__name__)
        log.add(model.get("ready_marker") == "PHASE4_1_DATA_MODELING_FOUNDATION_READY", "Foundation model has ready marker", str(model.get("ready_marker")))
        log.add(model.get("release_decision") == "PHASE4_1_FOUNDATION_CREATED_NO_DASHBOARD_CHANGE", "Foundation model has release decision", str(model.get("release_decision")))
        log.add(model.get("dashboard_change") is False, "Foundation confirms no dashboard change", str(model.get("dashboard_change")))
        log.add(len(model.get("upgrade_areas", [])) >= 4, "At least four Phase 4 upgrade areas", str(len(model.get("upgrade_areas", []))))
        log.add(len(model.get("guardrails", [])) >= 5, "At least five Phase 4 guardrails", str(len(model.get("guardrails", []))))
        text = json.dumps(model).lower()
        for term in ["real ticker data", "option-chain", "volatility", "premium", "strategy-comparison"]:
            log.add(term in text, f"Phase 4 concept present: {term}", term)
    except Exception as exc:
        log.add(False, "Phase 4-1 module imports and renders", repr(exc))

    dashboard_text = DASHBOARD_FILE.read_text(encoding="utf-8", errors="ignore") if DASHBOARD_FILE.exists() else ""
    for marker in ["PHASE3E_7C_DEVELOPER_TAB_READY", "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY", "PHASE3H_7_PUBLIC_CUSTOMER", "PHASE3J"]:
        log.add(marker in dashboard_text or any((REPORT_DIR / name).exists() for name in PRIOR_REPORTS), f"Prior phase evidence present: {marker}", marker)

    for name in PRIOR_REPORTS:
        path = REPORT_DIR / name
        log.add(path.exists(), f"Prior report exists: {name}", str(path))

    log.write_outputs()
    log.print_report()
    return 0 if log.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
