"""
phase3f_customer_promotion_gate.py

Phase 3F-1 release-gate helper for the Covered Call Simulator paid dashboard.

Purpose
-------
Phase 3E built the customer payoff workbench and connected it to the Developer
view under guardrails. Phase 3F begins the controlled promotion process.

This module does not modify the dashboard. It only inspects the current project
state and produces a promotion-readiness model.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import ast
import json
from typing import Iterable


PHASE3F_GATE_TITLE = "Phase 3F-1 customer promotion release gate"
PHASE3F_GATE_VERSION = "3F-1"
PHASE3F_CUSTOMER_PROMOTION_READY_MARKER = "PHASE3F_CUSTOMER_PROMOTION_GATE_READY"

REQUIRED_PHASE3E_FILES = [
    Path("app/paid_simulator/phase3e_customer_payoff_workflow.py"),
    Path("app/paid_simulator/phase3e_customer_setup_io.py"),
    Path("app/paid_simulator/phase3e_customer_payoff_labels.py"),
    Path("app/paid_simulator/phase3e_customer_scenario_overlay.py"),
    Path("app/paid_simulator/phase3e_customer_payoff_workbench.py"),
    Path("app/paid_simulator/phase3e_customer_workbench_view_model.py"),
    Path("app/paid_simulator/phase3e_customer_workbench_dashboard.py"),
    Path("app/paid_simulator/phase3e_customer_workbench_streamlit_panel.py"),
]

REQUIRED_PHASE3E_REPORTS = [
    Path("outputs/reports/paid_simulator/phase3e_7c_dashboard_tab_checkpoint_report.txt"),
    Path("outputs/reports/paid_simulator/phase3e_8_visual_verification_checkpoint_report.txt"),
    Path("outputs/reports/paid_simulator/phase3e_9_completion_checkpoint_report.txt"),
]

CUSTOMER_READY_LABELS = [
    "current price",
    "strike",
    "premium",
    "breakeven",
    "max profit",
    "downside cushion",
    "assignment zone",
]

RISK_LANGUAGE_MARKERS = [
    "warning",
    "risk",
]

DEVELOPER_MARKERS = [
    "PHASE3E_7C_DEVELOPER_TAB_READY",
    "_render_phase3e_customer_payoff_workbench_tab",
]

CUSTOMER_BLOCKED_MARKERS = [
    "PHASE3E_CUSTOMER_VIEW_ENABLED = True",
    "PHASE3F_CUSTOMER_VIEW_ENABLED = True",
    "Customer view Phase 3E enabled",
]


@dataclass
class GateCheck:
    name: str
    status: str
    detail: str

    @property
    def passed(self) -> bool:
        return self.status.upper() == "PASS"


@dataclass
class PromotionGateResult:
    title: str
    version: str
    project_root: str
    checks: list[GateCheck]
    recommendation: str
    next_action: str

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["passed"] = self.passed
        return payload


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def _check_file_exists(project_root: Path, rel_path: Path) -> GateCheck:
    full_path = project_root / rel_path
    if full_path.exists():
        return GateCheck(str(rel_path), "PASS", str(full_path))
    return GateCheck(str(rel_path), "FAIL", "missing")


def _check_python_syntax(project_root: Path, rel_path: Path) -> GateCheck:
    full_path = project_root / rel_path
    if not full_path.exists():
        return GateCheck(f"syntax: {rel_path}", "FAIL", "file missing")
    try:
        ast.parse(_read_text(full_path), filename=str(full_path))
    except SyntaxError as exc:
        return GateCheck(f"syntax: {rel_path}", "FAIL", repr(exc))
    return GateCheck(f"syntax: {rel_path}", "PASS", "valid Python syntax")


def _check_text_contains(project_root: Path, rel_path: Path, markers: Iterable[str], label: str) -> GateCheck:
    full_path = project_root / rel_path
    if not full_path.exists():
        return GateCheck(label, "FAIL", f"missing {rel_path}")
    text = _read_text(full_path).lower()
    missing = [marker for marker in markers if marker.lower() not in text]
    if missing:
        return GateCheck(label, "FAIL", "missing: " + ", ".join(missing))
    return GateCheck(label, "PASS", "all markers found")


def _check_text_absent(project_root: Path, rel_path: Path, markers: Iterable[str], label: str) -> GateCheck:
    full_path = project_root / rel_path
    if not full_path.exists():
        return GateCheck(label, "FAIL", f"missing {rel_path}")
    text = _read_text(full_path)
    present = [marker for marker in markers if marker in text]
    if present:
        return GateCheck(label, "FAIL", "unexpected markers: " + ", ".join(present))
    return GateCheck(label, "PASS", "customer view remains protected")


def build_phase3f_customer_promotion_gate(project_root: Path | str) -> PromotionGateResult:
    root = Path(project_root).resolve()
    checks: list[GateCheck] = []

    config_form = Path("app/paid_simulator/config_form_app.py")
    panel_file = Path("app/paid_simulator/phase3e_customer_workbench_streamlit_panel.py")

    checks.append(_check_file_exists(root, config_form))
    checks.append(_check_python_syntax(root, config_form))

    for rel_path in REQUIRED_PHASE3E_FILES:
        checks.append(_check_file_exists(root, rel_path))
        if rel_path.suffix == ".py":
            checks.append(_check_python_syntax(root, rel_path))

    for rel_path in REQUIRED_PHASE3E_REPORTS:
        checks.append(_check_file_exists(root, rel_path))

    checks.append(_check_text_contains(root, config_form, DEVELOPER_MARKERS, "Developer-view Phase 3E integration markers present"))
    checks.append(_check_text_absent(root, config_form, CUSTOMER_BLOCKED_MARKERS, "Customer view not prematurely enabled"))
    checks.append(_check_text_contains(root, panel_file, CUSTOMER_READY_LABELS, "Customer-facing payoff labels present"))
    checks.append(_check_text_contains(root, panel_file, RISK_LANGUAGE_MARKERS, "Risk/warning language present"))

    passed = all(check.passed for check in checks)
    if passed:
        recommendation = "PASS: Phase 3E may advance to controlled Phase 3F customer-facing design work."
        next_action = "Build a customer-view preview shell before exposing the workbench in the main Customer view."
    else:
        recommendation = "HOLD: repair failing guardrail checks before customer-facing promotion."
        next_action = "Fix the failing checks reported by Phase 3F-1 before proceeding."

    return PromotionGateResult(
        title=PHASE3F_GATE_TITLE,
        version=PHASE3F_GATE_VERSION,
        project_root=str(root),
        checks=checks,
        recommendation=recommendation,
        next_action=next_action,
    )


def write_phase3f_customer_promotion_outputs(result: PromotionGateResult, project_root: Path | str) -> dict[str, Path]:
    root = Path(project_root).resolve()
    reports_dir = root / "outputs" / "reports" / "paid_simulator"
    tables_dir = root / "outputs" / "tables" / "paid_simulator"
    reports_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    report_path = reports_dir / "phase3f_1_customer_promotion_gate_report.txt"
    json_path = reports_dir / "phase3f_1_customer_promotion_gate.json"
    csv_path = tables_dir / "phase3f_1_customer_promotion_gate_checklist.csv"

    lines = [
        "=" * 100,
        result.title,
        "=" * 100,
        f"Project root: {result.project_root}",
        f"Version: {result.version}",
        "",
        "Checks",
        "-" * 100,
    ]
    for check in result.checks:
        lines.append(f"{check.status:<10} {check.name:<70} {check.detail}")
    lines.extend([
        "",
        "Recommendation",
        "-" * 100,
        result.recommendation,
        "",
        "Next action",
        "-" * 100,
        result.next_action,
        "",
        f"Overall Phase 3F-1 checkpoint status: {'PASS' if result.passed else 'FAIL'}",
    ])
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    json_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")

    csv_lines = ["status,name,detail"]
    for check in result.checks:
        safe_name = check.name.replace('"', '""')
        safe_detail = check.detail.replace('"', '""')
        csv_lines.append(f'"{check.status}","{safe_name}","{safe_detail}"')
    csv_path.write_text("\n".join(csv_lines) + "\n", encoding="utf-8")

    return {
        "report": report_path,
        "json": json_path,
        "csv": csv_path,
    }
