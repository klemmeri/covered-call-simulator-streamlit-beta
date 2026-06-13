"""
run_paid_simulator_phase3f_5_access_gate_check.py

Checkpoint script for Phase 3F-5: Controlled Customer Preview Access Gate.
"""

from __future__ import annotations

import ast
import csv
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Dict, List


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_DIR = APP_DIR / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)

results: List[Dict[str, Any]] = []


def add_result(status: bool, label: str, detail: Any = "") -> None:
    results.append({"status": "PASS" if status else "FAIL", "label": label, "detail": str(detail)})


def print_section(title: str) -> None:
    print("\n" + title)
    print("-" * 100)


def syntax_valid(path: Path) -> bool:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True
    except Exception as exc:
        add_result(False, f"Syntax valid: {path.name}", repr(exc))
        return False


def load_module(module_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    print("=" * 100)
    print("Phase 3F-5 controlled customer-preview access-gate check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")

    expected_files = [
        PAID_DIR / "phase3f_customer_preview_access_gate.py",
        APP_DIR / "run_paid_simulator_phase3f_5_access_gate_check.py",
        PROJECT_ROOT / "docs" / "phase3f_5_customer_preview_access_gate.md",
    ]

    print_section("Expected files")
    for path in expected_files:
        add_result(path.exists(), path.name, path)

    config_path = PAID_DIR / "config_form_app.py"
    route_path = PAID_DIR / "phase3f_customer_preview_route.py"
    shell_path = PAID_DIR / "phase3f_customer_preview_shell.py"
    gate_path = PAID_DIR / "phase3f_customer_preview_access_gate.py"

    print_section("Syntax and import checks")
    for path in [config_path, route_path, shell_path, gate_path]:
        if path.exists():
            ok = syntax_valid(path)
            if ok:
                add_result(True, f"Syntax valid: {path.name}", "syntax valid")
        else:
            add_result(False, f"Required file exists: {path.name}", path)

    try:
        gate_module = load_module(gate_path, "phase3f_customer_preview_access_gate_dynamic")
        model = gate_module.build_phase3f_customer_preview_access_gate()
        data = model.to_dict()
        fallback = gate_module.render_phase3f_customer_preview_access_gate(streamlit_module=None)
        add_result(True, "Access-gate module imports", "imported")
        add_result(data.get("marker") == "PHASE3F_5_ACCESS_GATE_READY", "Access-gate ready marker present", data.get("marker"))
        add_result(data.get("ordinary_customer_enabled") is False, "Ordinary Customer view remains disabled", data.get("ordinary_customer_enabled"))
        add_result(data.get("preview_customer_enabled") is True, "Protected preview mode is available", data.get("preview_customer_enabled"))
        add_result(data.get("public_release_enabled") is False, "Public release remains disabled", data.get("public_release_enabled"))
        add_result(len(data.get("sections", [])) >= 4, "Access gate has review sections", len(data.get("sections", [])))
        add_result(len(data.get("guardrails", [])) >= 4, "Access gate has guardrails", len(data.get("guardrails", [])))
        add_result(isinstance(fallback, dict), "Fallback render returns dictionary", type(fallback).__name__)
    except Exception as exc:
        add_result(False, "Access-gate module imports and renders", repr(exc))
        data = {}

    print_section("Dashboard boundary checks")
    dashboard_text = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    add_result("PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY" in dashboard_text, "Phase 3F-3 dashboard marker still present", "marker search")
    add_result("PHASE3E_7C_DEVELOPER_TAB_READY" in dashboard_text, "Phase 3E dashboard marker still present", "marker search")
    add_result("Phase 3D" in dashboard_text or "phase3d" in dashboard_text.lower(), "Phase 3D markers still present", "marker search")
    add_result("Customer" in dashboard_text, "Customer-view markers still present", "marker search")
    add_result("PHASE3F_5_ORDINARY_CUSTOMER_ENABLED = True" not in dashboard_text, "Phase 3F-5 not exposed in ordinary Customer view", "customer protected")

    print_section("Writing checkpoint outputs")
    report_path = REPORT_DIR / "phase3f_5_access_gate_checkpoint_report.txt"
    json_path = REPORT_DIR / "phase3f_5_access_gate_checkpoint.json"
    csv_path = TABLE_DIR / "phase3f_5_access_gate_checklist.csv"

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["status", "label", "detail"])
        writer.writeheader()
        writer.writerows(results)

    payload = {
        "checkpoint": "Phase 3F-5 controlled customer-preview access gate",
        "project_root": str(PROJECT_ROOT),
        "results": results,
        "model": data,
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "Phase 3F-5 controlled customer-preview access-gate check",
        f"Project root: {PROJECT_ROOT}",
        "",
    ]
    for item in results:
        lines.append(f"{item['status']:<10} {item['label']:<70} {item['detail']}")
    report_path.write_text("\n".join(lines), encoding="utf-8")

    for item in results:
        print(f"{item['status']:<10} {item['label']:<70} {item['detail']}")

    failed = [item for item in results if item["status"] != "PASS"]
    print("\n" + "=" * 100)
    if failed:
        print("Overall Phase 3F-5 checkpoint status: FAIL")
        print("=" * 100)
        print(f"Saved checkpoint report: {report_path}")
        print(f"Saved checkpoint JSON:   {json_path}")
        print(f"Saved checklist CSV:     {csv_path}")
        return 1

    print("Overall Phase 3F-5 checkpoint status: PASS")
    print("=" * 100)
    print(f"Saved checkpoint report: {report_path}")
    print(f"Saved checkpoint JSON:   {json_path}")
    print(f"Saved checklist CSV:     {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
