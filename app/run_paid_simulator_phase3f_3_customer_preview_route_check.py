"""
run_paid_simulator_phase3f_3_customer_preview_route_check.py

Checkpoint check for Phase 3F-3 Customer Preview Dashboard Route.
"""

from __future__ import annotations

import ast
import csv
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DASHBOARD_PATH = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
ROUTE_PATH = PROJECT_ROOT / "app" / "paid_simulator" / "phase3f_customer_preview_route.py"
SHELL_PATH = PROJECT_ROOT / "app" / "paid_simulator" / "phase3f_customer_preview_shell.py"
INSTALLER_PATH = PROJECT_ROOT / "app" / "install_phase3f_3_customer_preview_route.py"
DOC_PATH = PROJECT_ROOT / "docs" / "phase3f_3_customer_preview_route.md"

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
BACKUP_DIR = PROJECT_ROOT / "outputs" / "backups" / "paid_simulator"
REPORT_PATH = REPORT_DIR / "phase3f_3_customer_preview_route_checkpoint_report.txt"
JSON_PATH = REPORT_DIR / "phase3f_3_customer_preview_route_checkpoint.json"
CSV_PATH = TABLE_DIR / "phase3f_3_customer_preview_route_checklist.csv"

READY_MARKER = "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY"
HELPER_NAME = "_render_phase3f_customer_preview_route"
CUSTOMER_ENABLED_MARKER = "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_CUSTOMER_ENABLED = True"


class CheckRecorder:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(self, passed: bool, check: str, detail: str) -> None:
        self.rows.append({"status": "PASS" if passed else "FAIL", "check": check, "detail": detail})

    @property
    def passed(self) -> bool:
        return all(row["status"] == "PASS" for row in self.rows)

    def print_rows(self) -> None:
        for row in self.rows:
            print(f"{row['status']:<10} {row['check']:<70} {row['detail']}")


def _syntax_ok(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:
        return False, repr(exc)


def _import_from_path(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_checks() -> CheckRecorder:
    rec = CheckRecorder()

    expected_files = [
        ("install_phase3f_3_customer_preview_route.py", INSTALLER_PATH),
        ("run_paid_simulator_phase3f_3_customer_preview_route_check.py", Path(__file__).resolve()),
        ("phase3f_customer_preview_route.py", ROUTE_PATH),
        ("phase3f_customer_preview_shell.py", SHELL_PATH),
        ("phase3f_3_customer_preview_route.md", DOC_PATH),
    ]
    for label, path in expected_files:
        rec.add(path.exists(), label, str(path))

    if DASHBOARD_PATH.exists():
        ok, detail = _syntax_ok(DASHBOARD_PATH)
        rec.add(ok, "Dashboard syntax valid", detail)
        dashboard_text = DASHBOARD_PATH.read_text(encoding="utf-8")
    else:
        rec.add(False, "Dashboard file exists", str(DASHBOARD_PATH))
        dashboard_text = ""

    if ROUTE_PATH.exists():
        ok, detail = _syntax_ok(ROUTE_PATH)
        rec.add(ok, "Preview route module syntax valid", detail)
        try:
            route_module = _import_from_path("phase3f_customer_preview_route_check_import", ROUTE_PATH)
            model = route_module.build_customer_preview_route_model().to_dict()
            fallback = route_module.render_customer_preview_route(streamlit_module=None)
            rec.add(model.get("marker") == READY_MARKER, "Route model has ready marker", str(model.get("marker")))
            rec.add(model.get("customer_enabled") is False, "Route model keeps customer disabled", str(model.get("customer_enabled")))
            rec.add(len(model.get("sections", [])) >= 4, "Route model has customer-preview sections", str(len(model.get("sections", []))))
            rec.add(len(model.get("guardrails", [])) >= 3, "Route model has guardrails", str(len(model.get("guardrails", []))))
            rec.add(isinstance(fallback, dict), "Route fallback render returns model", type(fallback).__name__)
        except Exception as exc:
            rec.add(False, "Preview route module imports and renders", repr(exc))

    rec.add(READY_MARKER in dashboard_text, "Dashboard has Phase 3F-3 readiness marker", READY_MARKER)
    rec.add(HELPER_NAME in dashboard_text, "Dashboard has Phase 3F-3 helper function", HELPER_NAME)
    rec.add(CUSTOMER_ENABLED_MARKER not in dashboard_text, "Ordinary Customer view not Phase 3F-3 enabled", "customer protected")
    rec.add("PHASE3E_7C_DEVELOPER_TAB_READY" in dashboard_text, "Phase 3E Developer marker still present", "Phase 3E marker search")
    rec.add("Phase 3D" in dashboard_text or "phase3d" in dashboard_text.lower(), "Phase 3D markers still present", "Phase 3D marker search")
    rec.add("Customer" in dashboard_text or "customer" in dashboard_text.lower(), "Customer-view markers still present", "Customer marker search")

    backups = sorted(BACKUP_DIR.glob("config_form_app_before_phase3f_3_*.py")) if BACKUP_DIR.exists() else []
    rec.add(bool(backups), "Timestamped Phase 3F-3 dashboard backup exists", str(backups[-1]) if backups else "missing")

    return rec


def write_outputs(rec: CheckRecorder) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["status", "check", "detail"])
        writer.writeheader()
        writer.writerows(rec.rows)

    summary = {
        "checkpoint": "Phase 3F-3 customer preview route",
        "overall_status": "PASS" if rec.passed else "FAIL",
        "checks": rec.rows,
    }
    JSON_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "Phase 3F-3 guarded customer preview route checkpoint",
        "=" * 72,
        f"Project root: {PROJECT_ROOT}",
        "",
    ]
    lines.extend(f"{row['status']:<10} {row['check']:<70} {row['detail']}" for row in rec.rows)
    lines.append("")
    lines.append(f"Overall Phase 3F-3 checkpoint status: {'PASS' if rec.passed else 'FAIL'}")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    print("=" * 100)
    print("Phase 3F-3 guarded customer preview route check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = run_checks()
    rec.print_rows()
    write_outputs(rec)

    print()
    print("=" * 100)
    print(f"Overall Phase 3F-3 checkpoint status: {'PASS' if rec.passed else 'FAIL'}")
    print("=" * 100)
    print(f"Saved checkpoint report: {REPORT_PATH}")
    print(f"Saved checkpoint JSON:   {JSON_PATH}")
    print(f"Saved checklist CSV:     {CSV_PATH}")

    return 0 if rec.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
