"""
run_paid_simulator_phase3g_4_route_readiness_check.py

Phase 3G-4 public Customer-view route-readiness checkpoint.

Run from PyCharm or command line:
    python app/run_paid_simulator_phase3g_4_route_readiness_check.py
"""

from __future__ import annotations

import ast
import csv
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_DIR = APP_DIR / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
BACKUP_DIR = PROJECT_ROOT / "outputs" / "backups" / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

RESULTS: list[dict[str, Any]] = []


def add_result(status: str, label: str, detail: Any = "") -> None:
    RESULTS.append({"status": status, "label": label, "detail": str(detail)})
    print(f"{status:<10} {label:<72} {detail}")


def check(condition: bool, label: str, detail: Any = "") -> bool:
    add_result("PASS" if condition else "FAIL", label, detail)
    return condition


def syntax_valid(path: Path) -> bool:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True
    except Exception as exc:
        add_result("FAIL", f"Syntax check failed for {path.name}", repr(exc))
        return False


def import_from_path(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    print("=" * 100)
    print("Phase 3G-4 public Customer-view route-readiness check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    expected_files = [
        PAID_DIR / "phase3g_public_customer_route_readiness.py",
        APP_DIR / "install_phase3g_4_public_route_readiness.py",
        APP_DIR / "run_paid_simulator_phase3g_4_route_readiness_check.py",
        DOCS_DIR / "phase3g_4_public_customer_route_readiness.md",
        PAID_DIR / "config_form_app.py",
    ]

    for path in expected_files:
        check(path.exists(), path.name, path)

    dashboard_path = PAID_DIR / "config_form_app.py"
    module_path = PAID_DIR / "phase3g_public_customer_route_readiness.py"

    if dashboard_path.exists():
        check(syntax_valid(dashboard_path), "Dashboard syntax valid", "syntax valid")
    if module_path.exists():
        check(syntax_valid(module_path), "Phase 3G-4 module syntax valid", "syntax valid")

    data: dict[str, Any] = {}
    try:
        module = import_from_path("phase3g4_route_readiness_check_module", module_path)
        model = module.build_phase3g_4_public_route_readiness_model()
        data = model.to_dict()
        render_data = module.render_phase3g_4_public_route_readiness(streamlit_module=None)
        check(data.get("marker") == "PHASE3G_4_PUBLIC_ROUTE_READY", "Model has Phase 3G-4 ready marker", data.get("marker"))
        check(data.get("public_customer_enabled") is False, "Public Customer view remains disabled", data.get("public_customer_enabled"))
        check(data.get("protected_preview_required") is True, "Protected preview remains required", data.get("protected_preview_required"))
        check(data.get("requires_explicit_release") is True, "Explicit release still required", data.get("requires_explicit_release"))
        check(len(data.get("customer_sections", [])) >= 4, "Customer route sections present", len(data.get("customer_sections", [])))
        check(len(data.get("guardrails", [])) >= 4, "Guardrails present", len(data.get("guardrails", [])))
        check(isinstance(render_data, dict), "Fallback render returns dictionary", type(render_data).__name__)
    except Exception as exc:
        check(False, "Phase 3G-4 module imports and renders", repr(exc))

    dashboard_text = dashboard_path.read_text(encoding="utf-8") if dashboard_path.exists() else ""
    lower_dashboard = dashboard_text.lower()
    check("PHASE3G_4_PUBLIC_ROUTE_READY" in dashboard_text, "Dashboard has Phase 3G-4 readiness marker", "PHASE3G_4_PUBLIC_ROUTE_READY")
    check("_render_phase3g_public_customer_route_readiness" in dashboard_text, "Dashboard has Phase 3G-4 helper function", "_render_phase3g_public_customer_route_readiness")
    check("PHASE3G_4_PUBLIC_CUSTOMER_ENABLED = True" not in dashboard_text, "Dashboard does not enable Phase 3G-4 public Customer view", "customer protected")
    check("PHASE3G_PUBLIC_CUSTOMER_ENABLED = True" not in dashboard_text, "Dashboard does not enable generic Phase 3G public Customer view", "customer protected")
    check("phase 3d" in lower_dashboard or "phase3d" in lower_dashboard, "Phase 3D markers still present", "marker search")
    check("phase3e" in lower_dashboard or "phase 3e" in lower_dashboard, "Phase 3E markers still present", "marker search")
    check("phase3f" in lower_dashboard or "phase 3f" in lower_dashboard, "Phase 3F markers still present", "marker search")
    check("customer" in lower_dashboard, "Customer-view markers still present", "marker search")

    backups = list(BACKUP_DIR.glob("config_form_app_before_phase3g_4_*.py")) if BACKUP_DIR.exists() else []
    check(len(backups) >= 1, "Timestamped Phase 3G-4 dashboard backup exists", backups[-1] if backups else "none")

    labels = " ".join(data.get("customer_labels", [])).lower() if isinstance(data, dict) else ""
    for label in ["current price", "breakeven", "max profit", "downside cushion", "assignment zone", "warning"]:
        check(label in labels, f"Customer-facing label present: {label}", label)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    report_path = REPORT_DIR / "phase3g_4_route_readiness_checkpoint_report.txt"
    json_path = REPORT_DIR / "phase3g_4_route_readiness_checkpoint.json"
    csv_path = TABLE_DIR / "phase3g_4_route_readiness_checklist.csv"

    report_lines = [
        "Phase 3G-4 public Customer-view route-readiness check",
        f"Project root: {PROJECT_ROOT}",
        "",
    ]
    report_lines.extend(f"{row['status']:<10} {row['label']:<72} {row['detail']}" for row in RESULTS)
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    json_path.write_text(json.dumps({"results": RESULTS, "model": data}, indent=2), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["status", "label", "detail"])
        writer.writeheader()
        writer.writerows(RESULTS)

    failed = [row for row in RESULTS if row["status"] != "PASS"]

    print()
    print("=" * 100)
    if failed:
        print("Overall Phase 3G-4 checkpoint status: FAIL")
    else:
        print("Overall Phase 3G-4 checkpoint status: PASS")
    print("=" * 100)
    print(f"Saved checkpoint report: {report_path}")
    print(f"Saved checkpoint JSON:   {json_path}")
    print(f"Saved checklist CSV:     {csv_path}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
