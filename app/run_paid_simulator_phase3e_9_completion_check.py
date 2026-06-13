"""
run_paid_simulator_phase3e_9_completion_check.py

Phase 3E-9 completion and guardrail validation for the Covered Call Simulator.

This checkpoint is intentionally conservative. It does not modify dashboard code.
It verifies that the customer-ready payoff workflow built during Phase 3E is
present, importable, protected from the Customer view, and documented.
"""

from __future__ import annotations

import csv
import importlib
import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_SIM_DIR = APP_DIR / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class CheckResult:
    section: str
    name: str
    status: str
    detail: str


def print_header(title: str) -> None:
    print("=" * 100)
    print(title)
    print("=" * 100)


def print_section(title: str) -> None:
    print("\n" + title)
    print("-" * 100)


def add(results: list[CheckResult], section: str, name: str, passed: bool, detail: str) -> None:
    status = "PASS" if passed else "FAIL"
    results.append(CheckResult(section=section, name=name, status=status, detail=detail))
    print(f"{status:<10} {name:<65} {detail}")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def import_module(module_name: str) -> tuple[bool, str, Any | None]:
    try:
        module = importlib.import_module(module_name)
        return True, "imported", module
    except Exception as exc:  # noqa: BLE001 - checkpoint must report exact failure
        return False, repr(exc), None


def write_reports(results: list[CheckResult]) -> tuple[Path, Path, Path]:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pass_count = sum(1 for item in results if item.status == "PASS")
    fail_count = sum(1 for item in results if item.status == "FAIL")
    overall = "PASS" if fail_count == 0 else "FAIL"

    txt_path = REPORT_DIR / "phase3e_9_completion_checkpoint_report.txt"
    json_path = REPORT_DIR / "phase3e_9_completion_checkpoint.json"
    csv_path = TABLE_DIR / "phase3e_9_completion_checklist.csv"

    lines = [
        "Phase 3E-9 completion and guardrail validation report",
        f"Generated: {timestamp}",
        f"Project root: {PROJECT_ROOT}",
        "",
        f"Overall status: {overall}",
        f"Passed checks: {pass_count}",
        f"Failed checks: {fail_count}",
        "",
        "Results:",
    ]
    for item in results:
        lines.append(f"[{item.status}] {item.section} | {item.name} | {item.detail}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload = {
        "generated": timestamp,
        "project_root": str(PROJECT_ROOT),
        "overall_status": overall,
        "passed_checks": pass_count,
        "failed_checks": fail_count,
        "results": [asdict(item) for item in results],
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["section", "name", "status", "detail"])
        writer.writeheader()
        for item in results:
            writer.writerow(asdict(item))

    return txt_path, json_path, csv_path


def main() -> int:
    results: list[CheckResult] = []

    print_header("Phase 3E-9 completion and guardrail validation check")
    print(f"Project root: {PROJECT_ROOT}")

    print_section("Expected Phase 3E files")
    expected_files = [
        PAID_SIM_DIR / "phase3e_customer_payoff_workflow.py",
        PAID_SIM_DIR / "phase3e_customer_setup_io.py",
        PAID_SIM_DIR / "phase3e_customer_payoff_labels.py",
        PAID_SIM_DIR / "phase3e_customer_scenario_overlay.py",
        PAID_SIM_DIR / "phase3e_customer_payoff_workbench.py",
        PAID_SIM_DIR / "phase3e_customer_workbench_view_model.py",
        PAID_SIM_DIR / "phase3e_customer_workbench_dashboard.py",
        PAID_SIM_DIR / "phase3e_customer_workbench_streamlit_panel.py",
        PAID_SIM_DIR / "config_form_app.py",
        APP_DIR / "run_paid_simulator_phase3e_8_visual_verification_check.py",
    ]
    for path in expected_files:
        add(results, "Expected files", path.name, path.exists(), str(path))

    print_section("Documentation files")
    expected_docs = [
        DOCS_DIR / "phase3e_customer_payoff_workflow.md",
        DOCS_DIR / "phase3e_customer_setup_io.md",
        DOCS_DIR / "phase3e_customer_payoff_labels.md",
        DOCS_DIR / "phase3e_customer_scenario_overlay.md",
        DOCS_DIR / "phase3e_customer_payoff_workbench.md",
        DOCS_DIR / "phase3e_customer_workbench_view_model.md",
        DOCS_DIR / "phase3e_dashboard_integration.md",
        DOCS_DIR / "phase3e_7b_customer_workbench_panel.md",
        DOCS_DIR / "phase3e_7c_dashboard_tab_integration.md",
        DOCS_DIR / "phase3e_8_browser_visual_verification.md",
    ]
    for path in expected_docs:
        add(results, "Documentation", path.name, path.exists(), str(path))

    print_section("Import checks")
    modules_to_import = [
        "app.paid_simulator.phase3e_customer_payoff_workflow",
        "app.paid_simulator.phase3e_customer_setup_io",
        "app.paid_simulator.phase3e_customer_payoff_labels",
        "app.paid_simulator.phase3e_customer_scenario_overlay",
        "app.paid_simulator.phase3e_customer_payoff_workbench",
        "app.paid_simulator.phase3e_customer_workbench_view_model",
        "app.paid_simulator.phase3e_customer_workbench_dashboard",
        "app.paid_simulator.phase3e_customer_workbench_streamlit_panel",
        "app.paid_simulator.config_form_app",
    ]
    imported: dict[str, Any] = {}
    for module_name in modules_to_import:
        ok, detail, module = import_module(module_name)
        add(results, "Imports", module_name, ok, detail)
        if ok:
            imported[module_name] = module

    print_section("Dashboard guardrails")
    dashboard_path = PAID_SIM_DIR / "config_form_app.py"
    dashboard_text = read_text(dashboard_path)
    add(results, "Dashboard guardrails", "Phase 3E readiness marker present", "PHASE3E_7C_DEVELOPER_TAB_READY" in dashboard_text, "PHASE3E_7C_DEVELOPER_TAB_READY")
    add(results, "Dashboard guardrails", "Phase 3E helper function present", "_render_phase3e_customer_payoff_workbench_tab" in dashboard_text, "_render_phase3e_customer_payoff_workbench_tab")
    add(results, "Dashboard guardrails", "Panel renderer reference present", "render_phase3e_customer_workbench_panel" in dashboard_text, "panel renderer")
    add(results, "Dashboard guardrails", "Phase 3D markers still present", "Phase 3D" in dashboard_text or "phase3d" in dashboard_text.lower(), "Phase 3D marker search")
    add(results, "Dashboard guardrails", "Customer-view markers still present", "Customer" in dashboard_text or "customer" in dashboard_text.lower(), "Customer marker search")
    add(results, "Dashboard guardrails", "Customer view not marked as Phase 3E enabled", "CUSTOMER_VIEW_PHASE3E_ENABLED = True" not in dashboard_text, "customer protected")

    print_section("Panel behavior and customer-facing labels")
    panel_module = imported.get("app.paid_simulator.phase3e_customer_workbench_streamlit_panel")
    if panel_module is None:
        add(results, "Panel behavior", "Panel module available", False, "not imported")
    else:
        title = getattr(panel_module, "PHASE3E_PANEL_TITLE", "")
        add(results, "Panel behavior", "Panel title exported", bool(title), str(title))

        has_model_builder = hasattr(panel_module, "build_panel_render_model")
        has_renderer = hasattr(panel_module, "render_phase3e_customer_workbench_panel")
        add(results, "Panel behavior", "build_panel_render_model available", has_model_builder, "function present")
        add(results, "Panel behavior", "render_phase3e_customer_workbench_panel available", has_renderer, "function present")

        if has_model_builder:
            try:
                model = panel_module.build_panel_render_model()
                model_text = json.dumps(model, default=str).lower()
                add(results, "Panel behavior", "Panel model builds", True, "model built")
                required_phrases = [
                    "current price",
                    "strike",
                    "premium",
                    "breakeven",
                    "max profit",
                    "downside cushion",
                    "assignment zone",
                    "warning",
                    "risk",
                    "save",
                    "reload",
                    "refresh",
                    "export",
                ]
                for phrase in required_phrases:
                    add(results, "Panel labels", f"Label present: {phrase}", phrase in model_text, phrase)
            except Exception as exc:  # noqa: BLE001
                add(results, "Panel behavior", "Panel model builds", False, repr(exc))

        if has_renderer:
            try:
                returned = panel_module.render_phase3e_customer_workbench_panel(streamlit_module=None)
                add(results, "Panel behavior", "Fallback render works", returned is not None, "returned render model")
            except Exception as exc:  # noqa: BLE001
                add(results, "Panel behavior", "Fallback render works", False, repr(exc))

    print_section("Previous checkpoint artifacts")
    previous_outputs = [
        REPORT_DIR / "phase3e_7c_dashboard_tab_checkpoint_report.txt",
        REPORT_DIR / "phase3e_7c_dashboard_tab_checkpoint.json",
        REPORT_DIR / "phase3e_8_visual_verification_checkpoint_report.txt",
        REPORT_DIR / "phase3e_8_browser_visual_checklist.md",
        REPORT_DIR / "phase3e_8_visual_verification.json",
    ]
    for path in previous_outputs:
        add(results, "Previous outputs", path.name, path.exists(), str(path))

    report_path, json_path, csv_path = write_reports(results)

    fail_count = sum(1 for item in results if item.status == "FAIL")
    print("\n" + "=" * 100)
    if fail_count == 0:
        print("Overall Phase 3E-9 checkpoint status: PASS")
    else:
        print("Overall Phase 3E-9 checkpoint status: FAIL")
    print("=" * 100)
    print(f"Saved checkpoint report: {report_path}")
    print(f"Saved checkpoint JSON:   {json_path}")
    print(f"Saved checklist CSV:     {csv_path}")

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
