"""
run_paid_simulator_phase3j_3_final_browser_check.py

Phase 3J-3 final customer browser checklist checkpoint.

Repair version: removes the invalid json.dumps(..., lower=...) call and writes
JSON using only valid standard-library arguments.
"""

from __future__ import annotations

import ast
import csv
import importlib
import json
import sys
from pathlib import Path
from typing import Any


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"

DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase3j_final_customer_browser_checklist.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase3j_3_final_customer_browser_checklist.md"

CHECKPOINT_REPORT = REPORT_DIR / "phase3j_3_final_browser_check_checkpoint_report.txt"
CHECKPOINT_JSON = REPORT_DIR / "phase3j_3_final_browser_check_checkpoint.json"
CHECKLIST_CSV = TABLE_DIR / "phase3j_3_final_browser_check_checklist.csv"
BROWSER_CHECKLIST_MD = REPORT_DIR / "phase3j_3_final_customer_browser_checklist.md"

EXPECTED_READY_MARKER = "PHASE3J_3_FINAL_CUSTOMER_BROWSER_CHECKLIST_READY"
EXPECTED_RELEASE_DECISION = "PHASE3J_3_FINAL_CUSTOMER_BROWSER_CHECKLIST_CREATED_NO_DASHBOARD_CHANGE"

PRIOR_MARKERS = [
    "PHASE3E_7C_DEVELOPER_TAB_READY",
    "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY",
    "PHASE3H_7_PUBLIC_CUSTOMER",
]

PRIOR_REPORTS = [
    "phase3h_8_post_activation_completion_checkpoint_report.txt",
    "phase3i_7_completion_gate_checkpoint_report.txt",
    "phase3j_1_production_polish_checkpoint_report.txt",
    "phase3j_2_ui_wording_polish_checkpoint_report.txt",
]


def record(results: list[dict[str, Any]], passed: bool, item: str, detail: str = "") -> None:
    results.append({"status": "PASS" if passed else "FAIL", "item": item, "detail": detail})


def syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:  # pragma: no cover - checkpoint diagnostic
        return False, repr(exc)


def model_to_dict(model: Any) -> dict[str, Any]:
    if isinstance(model, dict):
        return model
    if hasattr(model, "to_dict"):
        return model.to_dict()
    if hasattr(model, "__dict__"):
        return dict(model.__dict__)
    raise TypeError(f"Unsupported model type: {type(model).__name__}")


def print_report(results: list[dict[str, Any]]) -> None:
    print("=" * 100)
    print("Phase 3J-3 final customer browser checklist check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()
    for row in results:
        print(f"{row['status']:<10} {row['item']:<70} {row['detail']}")
    print()
    print("=" * 100)
    overall = all(row["status"] == "PASS" for row in results)
    print(f"Overall Phase 3J-3 checkpoint status: {'PASS' if overall else 'FAIL'}")
    print("=" * 100)


def write_outputs(results: list[dict[str, Any]], model: dict[str, Any] | None) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    overall = all(row["status"] == "PASS" for row in results)

    report_lines = [
        "Phase 3J-3 final customer browser checklist check",
        f"Project root: {PROJECT_ROOT}",
        "",
    ]
    for row in results:
        report_lines.append(f"{row['status']:<10} {row['item']:<70} {row['detail']}")
    report_lines.extend(["", f"Overall Phase 3J-3 checkpoint status: {'PASS' if overall else 'FAIL'}"])
    CHECKPOINT_REPORT.write_text("\n".join(report_lines), encoding="utf-8")

    payload = {
        "overall_status": "PASS" if overall else "FAIL",
        "project_root": str(PROJECT_ROOT),
        "results": results,
        "model": model or {},
    }
    CHECKPOINT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    with CHECKLIST_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["status", "item", "detail"])
        writer.writeheader()
        writer.writerows(results)


def main() -> int:
    results: list[dict[str, Any]] = []
    model: dict[str, Any] | None = None

    record(results, DASHBOARD_FILE.exists(), "Dashboard file exists", str(DASHBOARD_FILE))
    record(results, MODULE_FILE.exists(), "Phase 3J-3 checklist module exists", str(MODULE_FILE))
    record(results, DOC_FILE.exists(), "Phase 3J-3 documentation exists", str(DOC_FILE))

    if DASHBOARD_FILE.exists():
        ok, detail = syntax_valid(DASHBOARD_FILE)
        record(results, ok, "Dashboard syntax remains valid", detail)
        dashboard_text = DASHBOARD_FILE.read_text(encoding="utf-8", errors="ignore")
    else:
        dashboard_text = ""

    if MODULE_FILE.exists():
        ok, detail = syntax_valid(MODULE_FILE)
        record(results, ok, "Phase 3J-3 module syntax valid", detail)
    else:
        record(results, False, "Phase 3J-3 module syntax valid", "module missing")

    try:
        module = importlib.import_module("app.paid_simulator.phase3j_final_customer_browser_checklist")
        rendered = module.render_final_customer_browser_checklist(streamlit_module=None)
        model = model_to_dict(rendered)
        record(results, isinstance(model, dict), "Fallback render returns dict", type(rendered).__name__)
        record(results, model.get("ready_marker") == EXPECTED_READY_MARKER, "Checklist model has ready marker", str(model.get("ready_marker")))
        record(results, model.get("release_decision") == EXPECTED_RELEASE_DECISION, "Checklist model has release decision", str(model.get("release_decision")))
        record(results, model.get("dashboard_changed") is False, "Checklist confirms no dashboard change", str(model.get("dashboard_changed")))
        checks = model.get("browser_checks", [])
        record(results, isinstance(checks, list) and len(checks) >= 8, "At least eight browser checks present", str(len(checks) if isinstance(checks, list) else 0))
        if hasattr(module, "write_browser_checklist_markdown"):
            written_path = module.write_browser_checklist_markdown(BROWSER_CHECKLIST_MD)
            record(results, Path(written_path).exists(), "Browser checklist Markdown written", str(written_path))
        else:
            record(results, False, "Browser checklist Markdown written", "writer missing")
        record(results, True, "Phase 3J-3 module imports/renders", "module imported and rendered")
    except Exception as exc:
        record(results, False, "Phase 3J-3 module imports/renders", repr(exc))

    for marker in PRIOR_MARKERS:
        record(results, marker in dashboard_text, f"Prior activation marker/evidence present: {marker}", marker)

    for report_name in PRIOR_REPORTS:
        path = REPORT_DIR / report_name
        record(results, path.exists(), f"Prior report exists: {report_name}", str(path))

    print_report(results)
    write_outputs(results, model)

    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")
    print(f"Saved checklist CSV:     {CHECKLIST_CSV}")
    if BROWSER_CHECKLIST_MD.exists():
        print(f"Saved browser checklist: {BROWSER_CHECKLIST_MD}")

    return 0 if all(row["status"] == "PASS" for row in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
