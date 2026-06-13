"""
run_paid_simulator_phase3g_3_pre_activation_check.py

Phase 3G-3 public Customer-view pre-activation verification checkpoint.

Run from PyCharm or command line:
    python app/run_paid_simulator_phase3g_3_pre_activation_check.py
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
DOCS_DIR = PROJECT_ROOT / "docs"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

RESULTS: list[dict[str, Any]] = []


def add_result(status: str, label: str, detail: Any = "") -> None:
    RESULTS.append({"status": status, "label": label, "detail": str(detail)})
    print(f"{status:<10} {label:<70} {detail}")


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
    print("Phase 3G-3 public Customer-view pre-activation verification check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    expected_files = [
        PAID_DIR / "phase3g_public_customer_pre_activation_verification.py",
        APP_DIR / "run_paid_simulator_phase3g_3_pre_activation_check.py",
        DOCS_DIR / "phase3g_3_public_customer_pre_activation_verification.md",
        PAID_DIR / "config_form_app.py",
    ]

    for path in expected_files:
        check(path.exists(), path.name, path)

    dashboard_path = PAID_DIR / "config_form_app.py"
    module_path = PAID_DIR / "phase3g_public_customer_pre_activation_verification.py"

    if dashboard_path.exists():
        check(syntax_valid(dashboard_path), "Dashboard syntax valid", "syntax valid")
    if module_path.exists():
        check(syntax_valid(module_path), "Phase 3G-3 module syntax valid", "syntax valid")

    try:
        module = import_from_path("phase3g3_pre_activation_check_module", module_path)
        model = module.build_phase3g_3_pre_activation_model()
        data = model.to_dict()
        render_data = module.render_phase3g_3_pre_activation_verification(streamlit_module=None)
        check(data.get("marker") == "PHASE3G_3_PRE_ACTIVATION_READY", "Model has Phase 3G-3 ready marker", data.get("marker"))
        check(data.get("public_customer_enabled") is False, "Public Customer view remains disabled", data.get("public_customer_enabled"))
        check(data.get("protected_preview_required") is True, "Protected preview remains required", data.get("protected_preview_required"))
        check(len(data.get("release_requirements", [])) >= 6, "Release requirements present", len(data.get("release_requirements", [])))
        check(len(data.get("guardrails", [])) >= 4, "Guardrails present", len(data.get("guardrails", [])))
        check(isinstance(render_data, dict), "Fallback render returns dictionary", type(render_data).__name__)
    except Exception as exc:
        check(False, "Phase 3G-3 module imports and renders", repr(exc))
        data = {}

    dashboard_text = dashboard_path.read_text(encoding="utf-8") if dashboard_path.exists() else ""
    lower_dashboard = dashboard_text.lower()
    check("phase 3d" in lower_dashboard or "phase3d" in lower_dashboard, "Phase 3D markers still present", "marker search")
    check("phase3e" in lower_dashboard or "phase 3e" in lower_dashboard, "Phase 3E markers still present", "marker search")
    check("phase3f" in lower_dashboard or "phase 3f" in lower_dashboard, "Phase 3F markers still present", "marker search")
    check("customer" in lower_dashboard, "Customer-view markers still present", "marker search")
    check("PHASE3G_PUBLIC_CUSTOMER_ENABLED = True" not in dashboard_text, "Public Customer view not enabled in dashboard", "customer protected")

    # Prior report checks are intentionally broad: the exact filenames evolved
    # during Phase 3E/3F repairs, so the gate checks for phase families.
    prior_reports = list(REPORT_DIR.glob("phase3e_*")) + list(REPORT_DIR.glob("phase3f_*")) + list(REPORT_DIR.glob("phase3g_1*")) + list(REPORT_DIR.glob("phase3g_2*"))
    check(len(prior_reports) >= 3, "Prior Phase 3E/3F/3G reports available", len(prior_reports))

    labels = " ".join(data.get("customer_labels", [])).lower() if isinstance(data, dict) else ""
    for label in ["current price", "breakeven", "max profit", "downside cushion", "assignment zone", "warning"]:
        check(label in labels, f"Customer-facing label present: {label}", label)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    report_path = REPORT_DIR / "phase3g_3_pre_activation_checkpoint_report.txt"
    json_path = REPORT_DIR / "phase3g_3_pre_activation_checkpoint.json"
    csv_path = TABLE_DIR / "phase3g_3_pre_activation_checklist.csv"

    report_lines = [
        "Phase 3G-3 public Customer-view pre-activation verification check",
        f"Project root: {PROJECT_ROOT}",
        "",
    ]
    report_lines.extend(f"{row['status']:<10} {row['label']:<70} {row['detail']}" for row in RESULTS)
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
        print("Overall Phase 3G-3 checkpoint status: FAIL")
    else:
        print("Overall Phase 3G-3 checkpoint status: PASS")
    print("=" * 100)
    print(f"Saved checkpoint report: {report_path}")
    print(f"Saved checkpoint JSON:   {json_path}")
    print(f"Saved checklist CSV:     {csv_path}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
