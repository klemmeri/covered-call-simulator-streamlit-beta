"""
Phase 3F-2 customer preview shell checkpoint.

Run from PyCharm or command line:
    python app/run_paid_simulator_phase3f_2_customer_preview_shell_check.py
"""

from __future__ import annotations

import ast
import csv
import importlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, List, Tuple


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
APP_DIR = PROJECT_ROOT / "app"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


Result = Tuple[str, str, str]


def line(char: str = "=", width: int = 100) -> str:
    return char * width


def add(results: List[Result], ok: bool, label: str, detail: str = "") -> None:
    results.append(("PASS" if ok else "FAIL", label, detail))


def has_valid_python(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "valid Python syntax"
    except Exception as exc:  # pragma: no cover - diagnostic path
        return False, repr(exc)


def contains(path: Path, text: str) -> bool:
    if not path.exists():
        return False
    return text in path.read_text(encoding="utf-8", errors="ignore")


def main() -> int:
    results: List[Result] = []

    dashboard_file = APP_DIR / "paid_simulator" / "config_form_app.py"
    preview_file = APP_DIR / "paid_simulator" / "phase3f_customer_preview_shell.py"
    doc_file = PROJECT_ROOT / "docs" / "phase3f_2_customer_preview_shell.md"

    print(line())
    print("Phase 3F-2 protected customer preview shell check")
    print(line())
    print(f"Project root: {PROJECT_ROOT}")
    print()

    print("Expected files")
    print(line("-"))
    for label, path in [
        ("phase3f_customer_preview_shell.py", preview_file),
        ("run_paid_simulator_phase3f_2_customer_preview_shell_check.py", CURRENT_FILE),
        ("phase3f_2_customer_preview_shell.md", doc_file),
        ("config_form_app.py", dashboard_file),
    ]:
        add(results, path.exists(), label, str(path))

    if preview_file.exists():
        ok, detail = has_valid_python(preview_file)
        add(results, ok, "Preview shell has valid Python syntax", detail)

    if dashboard_file.exists():
        ok, detail = has_valid_python(dashboard_file)
        add(results, ok, "Dashboard still has valid Python syntax", detail)

    print("\nImport and model checks")
    print(line("-"))
    model: Any = None
    try:
        module = importlib.import_module("app.paid_simulator.phase3f_customer_preview_shell")
        model = module.build_customer_preview_shell()
        fallback = module.render_customer_preview_shell(streamlit_module=None)
        add(results, True, "Preview shell imports", "module imported")
        add(results, model.title == module.PHASE3F_PREVIEW_TITLE, "Preview title exported and used", model.title)
        add(results, model.marker == module.PHASE3F_PREVIEW_MARKER, "Preview readiness marker present", model.marker)
        add(results, model.protection_marker == module.CUSTOMER_PREVIEW_NOT_PUBLIC_MARKER, "Preview not-public marker present", model.protection_marker)
        add(results, fallback.title == model.title, "Fallback render returns model", fallback.title)
    except Exception as exc:
        add(results, False, "Preview shell imports and builds", repr(exc))

    if model is not None:
        labels = "\n".join(model.setup_labels).lower()
        metrics = "\n".join(m.label for m in model.payoff_metrics).lower()
        warnings = "\n".join(model.warnings).lower()
        actions = "\n".join(a.label for a in model.actions).lower()
        notes = "\n".join(model.release_gate_notes).lower()

        add(results, "current price" in labels, "Current price setup label present", "current price")
        add(results, "call strike" in labels, "Call strike setup label present", "call strike")
        add(results, "premium" in labels, "Premium setup label present", "premium")
        add(results, "breakeven" in metrics, "Breakeven metric present", "breakeven")
        add(results, "max profit" in metrics, "Max profit metric present", "max profit")
        add(results, "downside cushion" in metrics, "Downside cushion metric present", "downside cushion")
        add(results, "assignment zone" in metrics, "Assignment zone metric present", "assignment zone")
        add(results, "downside risk" in warnings or "risk" in warnings, "Risk warning language present", "risk")
        add(results, "assignment" in warnings, "Assignment warning language present", "assignment")
        add(results, "save setup" in actions, "Save setup action present", "save setup")
        add(results, "reload" in actions, "Reload action present", "reload")
        add(results, "refresh" in actions, "Refresh action present", "refresh")
        add(results, "export" in actions, "Export action present", "export")
        add(results, "not yet public" in notes or "not public" in notes, "Release gate says not public", "not public")

    print("\nDashboard boundary checks")
    print(line("-"))
    if dashboard_file.exists():
        dashboard_text = dashboard_file.read_text(encoding="utf-8", errors="ignore")
        add(results, "PHASE3E_7C_DEVELOPER_TAB_READY" in dashboard_text, "Phase 3E Developer marker still present", "PHASE3E_7C_DEVELOPER_TAB_READY")
        add(results, "_render_phase3e_customer_payoff_workbench_tab" in dashboard_text, "Phase 3E helper still present", "helper")
        add(results, "Phase 3D" in dashboard_text or "phase3d" in dashboard_text.lower(), "Phase 3D markers still present", "Phase 3D marker search")
        add(results, "Customer" in dashboard_text or "customer" in dashboard_text.lower(), "Customer-view markers still present", "Customer marker search")
        add(results, "PHASE3F_CUSTOMER_PUBLIC_ENABLED" not in dashboard_text, "Phase 3F not public-enabled in dashboard", "customer protected")
        add(results, "render_customer_preview_shell" not in dashboard_text, "Preview shell not blindly injected into dashboard", "safe standalone preview")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    report_path = REPORT_DIR / "phase3f_2_customer_preview_shell_checkpoint_report.txt"
    json_path = REPORT_DIR / "phase3f_2_customer_preview_shell_checkpoint.json"
    csv_path = TABLE_DIR / "phase3f_2_customer_preview_shell_checklist.csv"

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["status", "check", "detail"])
        writer.writerows(results)

    summary = {
        "checkpoint": "Phase 3F-2",
        "name": "Protected customer preview shell",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "project_root": str(PROJECT_ROOT),
        "pass_count": sum(1 for status, _, _ in results if status == "PASS"),
        "fail_count": sum(1 for status, _, _ in results if status == "FAIL"),
        "results": [
            {"status": status, "check": label, "detail": detail}
            for status, label, detail in results
        ],
    }
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    with report_path.open("w", encoding="utf-8") as f:
        f.write("Phase 3F-2 protected customer preview shell checkpoint\n")
        f.write(f"Project root: {PROJECT_ROOT}\n\n")
        for status, label, detail in results:
            f.write(f"{status:10} {label:65} {detail}\n")
        f.write("\n")
        f.write(f"Overall Phase 3F-2 checkpoint status: {'PASS' if summary['fail_count'] == 0 else 'FAIL'}\n")

    for status, label, detail in results:
        print(f"{status:10} {label:65} {detail}")

    print("\n" + line())
    overall = "PASS" if summary["fail_count"] == 0 else "FAIL"
    print(f"Overall Phase 3F-2 checkpoint status: {overall}")
    print(line())
    print(f"Saved checkpoint report: {report_path}")
    print(f"Saved checkpoint JSON:   {json_path}")
    print(f"Saved checklist CSV:     {csv_path}")

    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
