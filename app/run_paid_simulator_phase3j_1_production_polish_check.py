"""
run_paid_simulator_phase3j_1_production_polish_check.py

Checkpoint script for Phase 3J-1 production polish backlog.
"""

from __future__ import annotations

import ast
import importlib
import json
import sys
from pathlib import Path


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

CHECKPOINT_REPORT = REPORTS_DIR / "phase3j_1_production_polish_checkpoint_report.txt"
CHECKPOINT_JSON = REPORTS_DIR / "phase3j_1_production_polish_checkpoint.json"
CHECKLIST_CSV = TABLES_DIR / "phase3j_1_production_polish_checklist.csv"

results: list[dict[str, str | bool]] = []


def record(name: str, passed: bool, detail: str = "") -> None:
    results.append({"name": name, "passed": passed, "detail": detail})
    status = "PASS" if passed else "FAIL"
    print(f"{status:<10} {name:<70} {detail}")


def syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:
        return False, repr(exc)


def file_contains(path: Path, text: str) -> bool:
    if not path.exists():
        return False
    return text in path.read_text(encoding="utf-8", errors="ignore")


def main() -> int:
    print("=" * 100)
    print("Phase 3J-1 production polish backlog check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    dashboard_path = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
    module_path = PROJECT_ROOT / "app" / "paid_simulator" / "phase3j_production_polish_backlog.py"
    doc_path = PROJECT_ROOT / "docs" / "phase3j_1_production_polish_backlog.md"

    record("Dashboard file exists", dashboard_path.exists(), str(dashboard_path))
    record("Phase 3J-1 module exists", module_path.exists(), str(module_path))
    record("Phase 3J-1 documentation exists", doc_path.exists(), str(doc_path))

    if dashboard_path.exists():
        ok, detail = syntax_valid(dashboard_path)
        record("Dashboard syntax remains valid", ok, detail)
    if module_path.exists():
        ok, detail = syntax_valid(module_path)
        record("Phase 3J-1 module syntax valid", ok, detail)

    try:
        module = importlib.import_module("app.paid_simulator.phase3j_production_polish_backlog")
        model = module.render_phase3j_production_polish_backlog(streamlit_module=None)
        record("Phase 3J-1 module imports and renders", isinstance(model, dict), "dict" if isinstance(model, dict) else type(model).__name__)
    except Exception as exc:
        model = {}
        record("Phase 3J-1 module imports and renders", False, repr(exc))

    record("Production polish model has ready marker", model.get("marker") == "PHASE3J_1_PRODUCTION_POLISH_BACKLOG_READY", str(model.get("marker")))
    record("Production polish model has release decision", model.get("release_decision") == "PHASE3J_1_PRODUCTION_POLISH_BACKLOG_CREATED_NO_DASHBOARD_CHANGE", str(model.get("release_decision")))
    record("Production polish model does not modify dashboard", model.get("dashboard_modified") is False, str(model.get("dashboard_modified")))
    record("At least six backlog items present", len(model.get("backlog_items", [])) >= 6, str(len(model.get("backlog_items", []))))
    record("At least five guardrails present", len(model.get("guardrails", [])) >= 5, str(len(model.get("guardrails", []))))

    if dashboard_path.exists():
        record("Phase 3H activation evidence remains present", file_contains(dashboard_path, "PHASE3H") and file_contains(dashboard_path, "PUBLIC_CUSTOMER"), "Phase 3H/public customer marker search")
        record("Phase 3I customer workflow evidence remains present", (REPORTS_DIR / "phase3i_7_completion_gate_checkpoint_report.txt").exists(), str(REPORTS_DIR / "phase3i_7_completion_gate_checkpoint_report.txt"))
        record("Phase 3E marker remains present", file_contains(dashboard_path, "PHASE3E_7C_DEVELOPER_TAB_READY"), "PHASE3E_7C_DEVELOPER_TAB_READY")
        record("Phase 3F marker remains present", file_contains(dashboard_path, "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY"), "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY")

    try:
        paths = module.write_phase3j_outputs(PROJECT_ROOT) if 'module' in locals() else {}
        record("Production polish report written", Path(paths.get("report", "")).exists(), paths.get("report", ""))
        record("Production polish CSV written", Path(paths.get("csv", "")).exists(), paths.get("csv", ""))
        record("Production polish release decision written", Path(paths.get("decision", "")).exists(), paths.get("decision", ""))
    except Exception as exc:
        record("Production polish outputs written", False, repr(exc))

    all_passed = all(bool(item["passed"]) for item in results)
    status = "PASS" if all_passed else "FAIL"

    report_lines = [
        "Phase 3J-1 production polish backlog check",
        "=" * 100,
        f"Project root: {PROJECT_ROOT}",
        "",
    ]
    for item in results:
        report_lines.append(f"{'PASS' if item['passed'] else 'FAIL'}\t{item['name']}\t{item['detail']}")
    report_lines.extend(["", f"Overall Phase 3J-1 checkpoint status: {status}"])
    CHECKPOINT_REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    CHECKPOINT_JSON.write_text(json.dumps({"status": status, "results": results}, indent=2), encoding="utf-8")
    CHECKLIST_CSV.write_text(
        "name,passed,detail\n" + "\n".join(
            '"{}",{},"{}"'.format(
                str(item["name"]).replace('"', '""'),
                item["passed"],
                str(item["detail"]).replace('"', '""'),
            )
            for item in results
        ) + "\n",
        encoding="utf-8",
    )

    print()
    print("=" * 100)
    print(f"Overall Phase 3J-1 checkpoint status: {status}")
    print("=" * 100)
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")
    print(f"Saved checklist CSV:     {CHECKLIST_CSV}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
