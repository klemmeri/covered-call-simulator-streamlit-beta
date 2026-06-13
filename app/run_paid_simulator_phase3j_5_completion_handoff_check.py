"""
run_paid_simulator_phase3j_5_completion_handoff_check.py

Final Phase 3 completion handoff checkpoint for the Covered Call Simulator.
"""
from __future__ import annotations

import ast
import importlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
APP_DIR = PROJECT_ROOT / "app"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

CHECKPOINT_REPORT = REPORTS_DIR / "phase3j_5_completion_handoff_checkpoint_report.txt"
CHECKPOINT_JSON = REPORTS_DIR / "phase3j_5_completion_handoff_checkpoint.json"
CHECKLIST_CSV = TABLES_DIR / "phase3j_5_completion_handoff_checklist.csv"


def print_header(title: str) -> None:
    print("=" * 100)
    print(title)
    print("=" * 100)


def add_result(results: List[Dict[str, Any]], passed: bool, name: str, detail: str = "") -> None:
    status = "PASS" if passed else "FAIL"
    results.append({"status": status, "name": name, "detail": detail})
    print(f"{status:<10} {name:<70} {detail}")


def syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:  # pragma: no cover
        return False, repr(exc)


def main() -> int:
    title = "Phase 3J-5 Phase 3 completion handoff check"
    print_header(title)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    results: List[Dict[str, Any]] = []

    dashboard_file = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
    module_file = PROJECT_ROOT / "app" / "paid_simulator" / "phase3j_phase3_completion_handoff.py"
    doc_file = PROJECT_ROOT / "docs" / "phase3j_5_phase3_completion_handoff.md"

    add_result(results, dashboard_file.exists(), "Dashboard file exists", str(dashboard_file))
    add_result(results, module_file.exists(), "Phase 3J-5 handoff module exists", str(module_file))
    add_result(results, doc_file.exists(), "Phase 3J-5 documentation exists", str(doc_file))

    if dashboard_file.exists():
        ok, detail = syntax_valid(dashboard_file)
        add_result(results, ok, "Dashboard syntax remains valid", detail)
        dashboard_text = dashboard_file.read_text(encoding="utf-8", errors="ignore")
    else:
        dashboard_text = ""

    if module_file.exists():
        ok, detail = syntax_valid(module_file)
        add_result(results, ok, "Phase 3J-5 module syntax valid", detail)
    else:
        add_result(results, False, "Phase 3J-5 module syntax valid", "module missing")

    try:
        module = importlib.import_module("app.paid_simulator.phase3j_phase3_completion_handoff")
        model = module.render_phase3_completion_handoff(streamlit_module=None)
        add_result(results, isinstance(model, dict), "Fallback render returns dict", type(model).__name__)
    except Exception as exc:
        model = {}
        add_result(results, False, "Phase 3J-5 module imports/renders", repr(exc))

    add_result(
        results,
        model.get("ready_marker") == "PHASE3J_5_PHASE3_COMPLETION_HANDOFF_READY",
        "Completion handoff model has ready marker",
        str(model.get("ready_marker")),
    )
    add_result(
        results,
        model.get("release_decision") == "PHASE3_COMPLETE_READY_FOR_PHASE4_MODELING_DATA_UPGRADES",
        "Completion handoff model has release decision",
        str(model.get("release_decision")),
    )
    add_result(
        results,
        model.get("dashboard_change_required") is False,
        "Completion handoff confirms no dashboard change",
        str(model.get("dashboard_change_required")),
    )

    completed = model.get("completed_phases", [])
    add_result(results, len(completed) >= 6, "Completion handoff lists completed Phase 3 stages", str(len(completed)))
    for phase in ["Phase 3E", "Phase 3F", "Phase 3G", "Phase 3H", "Phase 3I", "Phase 3J"]:
        found = any(item.get("phase") == phase and item.get("status") == "complete" for item in completed if isinstance(item, dict))
        add_result(results, found, f"Completed stage present: {phase}", phase)

    workstreams = model.get("phase4_recommended_workstreams", [])
    add_result(results, len(workstreams) >= 4, "Phase 4 recommended workstreams present", str(len(workstreams)))
    for term in ["Real market data", "Option model", "Strategy decision", "Backtest", "Pro dashboard"]:
        found = term.lower() in json.dumps(workstreams).lower()
        add_result(results, found, f"Phase 4 workstream present: {term}", term)

    for marker in [
        "PHASE3E_7C_DEVELOPER_TAB_READY",
        "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY",
        "PHASE3H_7_PUBLIC_CUSTOMER",
    ]:
        add_result(results, marker in dashboard_text, f"Prior dashboard marker/evidence present: {marker}", marker)

    prior_reports = model.get("required_prior_reports", [])
    for filename in prior_reports:
        path = REPORTS_DIR / filename
        add_result(results, path.exists(), f"Prior report exists: {filename}", str(path))

    try:
        paths = module.write_phase3_completion_handoff_report(PROJECT_ROOT)
        add_result(results, paths["report"].exists(), "Completion handoff report written", str(paths["report"]))
        add_result(results, paths["decision"].exists(), "Completion release decision written", str(paths["decision"]))
        add_result(results, paths["checklist"].exists(), "Completion checklist CSV written", str(paths["checklist"]))
    except Exception as exc:
        add_result(results, False, "Completion handoff artifacts written", repr(exc))

    overall_pass = all(item["status"] == "PASS" for item in results)

    lines = [title, "=" * 100, f"Project root: {PROJECT_ROOT}", ""]
    for item in results:
        lines.append(f"{item['status']:<10} {item['name']:<70} {item['detail']}")
    lines.extend(["", "=" * 100, f"Overall Phase 3J-5 checkpoint status: {'PASS' if overall_pass else 'FAIL'}"])
    CHECKPOINT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    CHECKPOINT_JSON.write_text(json.dumps({"overall_pass": overall_pass, "results": results}, indent=2), encoding="utf-8")
    CHECKLIST_CSV.write_text(
        "status,name,detail\n" + "\n".join(
            f"{item['status']},{item['name'].replace(',', ';')},{str(item['detail']).replace(',', ';')}" for item in results
        ) + "\n",
        encoding="utf-8",
    )

    print()
    print("=" * 100)
    print(f"Overall Phase 3J-5 checkpoint status: {'PASS' if overall_pass else 'FAIL'}")
    print("=" * 100)
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")
    print(f"Saved checklist CSV:     {CHECKLIST_CSV}")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
