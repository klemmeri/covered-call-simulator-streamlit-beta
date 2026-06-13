"""
run_paid_simulator_phase3b_checkpoint_check.py

Checkpoint checker for Phase 3B of the Covered Call Simulator paid dashboard.

Phase 3B adds the scenario-overlay layer for the Phase 3 interactive covered-call
payoff prototype. This checker verifies that the Phase 3B model, viewer,
pipeline, dashboard tab, integration readiness output, generated reports, and
supporting documentation are present.

This checker is intentionally conservative. A missing interactive payoff
snapshot is treated as an optional review item because that file is created only
after a user saves/exports a setup from the interactive payoff viewer.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import csv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_APP_DIR = APP_DIR / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CHECK_REPORT = REPORTS_DIR / "phase3b_checkpoint_report.txt"


@dataclass
class CheckItem:
    section: str
    label: str
    path: Path | None = None
    status: str = "REVIEW"
    detail: str = ""
    optional: bool = False


def rel_path(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def path_check(section: str, label: str, path: Path, optional: bool = False) -> CheckItem:
    exists = path.exists()
    if exists:
        status = "FOUND" if not optional else "FOUND"
        detail = str(path)
    else:
        status = "OPTIONAL" if optional else "MISSING"
        detail = str(path)
    return CheckItem(section=section, label=label, path=path, status=status, detail=detail, optional=optional)


def marker_check(section: str, label: str, path: Path, markers: list[str]) -> list[CheckItem]:
    items: list[CheckItem] = []
    if not path.exists():
        for marker in markers:
            items.append(CheckItem(section, f"{label} marker '{marker}'", path, "MISSING", str(path)))
        return items

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        for marker in markers:
            items.append(CheckItem(section, f"{label} marker '{marker}'", path, "REVIEW", f"Could not read file: {exc}"))
        return items

    lower_text = text.lower()
    for marker in markers:
        status = "PASS" if marker.lower() in lower_text else "REVIEW"
        detail = marker if status == "PASS" else f"Marker not found in {rel_path(path)}"
        items.append(CheckItem(section, f"{label} marker '{marker}'", path, status, detail))
    return items


def csv_row_check(section: str, label: str, path: Path, optional: bool = False) -> CheckItem:
    if not path.exists():
        status = "OPTIONAL" if optional else "MISSING"
        return CheckItem(section, label, path, status, str(path), optional=optional)

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
    except Exception as exc:
        return CheckItem(section, label, path, "REVIEW", f"Could not read CSV: {exc}", optional=optional)

    data_rows = max(len(rows) - 1, 0)
    if data_rows > 0:
        return CheckItem(section, label, path, "PASS", f"rows={data_rows}", optional=optional)

    status = "OPTIONAL" if optional else "REVIEW"
    return CheckItem(section, label, path, status, "rows=0", optional=optional)


def build_checks() -> list[CheckItem]:
    checks: list[CheckItem] = []

    # Phase 3A context
    checks.extend([
        path_check("Phase 3A interactive payoff context", "Phase 3 interactive payoff viewer", PAID_APP_DIR / "phase3_interactive_payoff_viewer.py"),
        path_check("Phase 3A interactive payoff context", "Phase 3 viewer launcher", APP_DIR / "run_paid_simulator_phase3_interactive_payoff_viewer.py"),
        path_check("Phase 3A interactive payoff context", "Phase 3 viewer check", APP_DIR / "run_paid_simulator_phase3_interactive_payoff_viewer_check.py"),
        path_check("Phase 3A interactive payoff context", "Phase 3 pipeline check", APP_DIR / "run_paid_simulator_phase3_interactive_payoff_pipeline_check.py"),
        path_check("Phase 3A interactive payoff context", "Phase 3 dashboard-tab check", APP_DIR / "run_paid_simulator_phase3_dashboard_tab_check.py"),
        path_check("Phase 3A interactive payoff context", "Phase 3 integration-readiness check", APP_DIR / "run_paid_simulator_phase3_integration_readiness_check.py"),
        path_check("Phase 3A interactive payoff context", "Phase 3 checkpoint check", APP_DIR / "run_paid_simulator_phase3_checkpoint_check.py"),
    ])

    # Phase 3B files
    checks.extend([
        path_check("Phase 3B source files", "Scenario-overlay model", PAID_APP_DIR / "phase3_scenario_overlay_model.py"),
        path_check("Phase 3B source files", "Scenario-overlay viewer", PAID_APP_DIR / "phase3_scenario_overlay_viewer.py"),
        path_check("Phase 3B source files", "Main dashboard app", PAID_APP_DIR / "config_form_app.py"),
        path_check("Phase 3B source files", "Main dashboard launcher", APP_DIR / "run_paid_simulator_form.py"),
    ])

    checks.extend([
        path_check("Phase 3B runner/check files", "Scenario-overlay model check", APP_DIR / "run_paid_simulator_phase3_scenario_overlay_check.py"),
        path_check("Phase 3B runner/check files", "Scenario-overlay viewer launcher", APP_DIR / "run_paid_simulator_phase3_scenario_overlay_viewer.py"),
        path_check("Phase 3B runner/check files", "Scenario-overlay viewer check", APP_DIR / "run_paid_simulator_phase3_scenario_overlay_viewer_check.py"),
        path_check("Phase 3B runner/check files", "Scenario-overlay pipeline check", APP_DIR / "run_paid_simulator_phase3_scenario_overlay_pipeline_check.py"),
        path_check("Phase 3B runner/check files", "Phase 3B dashboard-tab check", APP_DIR / "run_paid_simulator_phase3b_dashboard_tab_check.py"),
        path_check("Phase 3B runner/check files", "Phase 3B integration-readiness check", APP_DIR / "run_paid_simulator_phase3b_integration_readiness_check.py"),
    ])

    # Phase 3B generated outputs
    checks.extend([
        path_check("Phase 3B generated outputs", "Scenario-overlay CSV", TABLES_DIR / "phase3_scenario_overlay.csv"),
        path_check("Phase 3B generated outputs", "Scenario-overlay HTML", REPORTS_DIR / "phase3_scenario_overlay.html"),
        path_check("Phase 3B generated outputs", "Scenario-overlay text summary", REPORTS_DIR / "phase3_scenario_overlay_summary.txt"),
        path_check("Phase 3B generated outputs", "Scenario-overlay pipeline report", REPORTS_DIR / "phase3b_scenario_overlay_pipeline_report.txt"),
        path_check("Phase 3B generated outputs", "Phase 3B integration-readiness report", REPORTS_DIR / "phase3b_integration_readiness_report.txt"),
        path_check("Optional Phase 3 saved setup outputs", "Interactive payoff snapshot CSV", TABLES_DIR / "phase3_interactive_payoff_snapshot.csv", optional=True),
        path_check("Optional Phase 3 saved setup outputs", "Interactive payoff snapshot HTML", REPORTS_DIR / "phase3_interactive_payoff_snapshot.html", optional=True),
    ])

    # Documentation
    checks.extend([
        path_check("Phase 3B documentation", "Phase 3 interactive payoff viewer", DOCS_DIR / "paid_simulator_phase3_interactive_payoff_viewer.md"),
        path_check("Phase 3B documentation", "Phase 3 interactive payoff pipeline", DOCS_DIR / "paid_simulator_phase3_interactive_payoff_pipeline_check.md"),
        path_check("Phase 3B documentation", "Phase 3 dashboard tab", DOCS_DIR / "paid_simulator_phase3_dashboard_tab.md"),
        path_check("Phase 3B documentation", "Phase 3 checkpoint summary", DOCS_DIR / "paid_simulator_phase3_checkpoint_summary.md"),
        path_check("Phase 3B documentation", "Scenario-overlay model", DOCS_DIR / "paid_simulator_phase3_scenario_overlay_model.md"),
        path_check("Phase 3B documentation", "Scenario-overlay viewer", DOCS_DIR / "paid_simulator_phase3_scenario_overlay_viewer.md"),
        path_check("Phase 3B documentation", "Scenario-overlay pipeline", DOCS_DIR / "paid_simulator_phase3_scenario_overlay_pipeline_check.md"),
        path_check("Phase 3B documentation", "Phase 3B dashboard tab", DOCS_DIR / "paid_simulator_phase3b_dashboard_tab.md"),
        path_check("Phase 3B documentation", "Phase 3B integration readiness", DOCS_DIR / "paid_simulator_phase3b_integration_readiness.md"),
        path_check("Phase 3B documentation", "Phase 3B checkpoint summary", DOCS_DIR / "paid_simulator_phase3b_checkpoint_summary.md"),
    ])

    # CSV row checks
    checks.extend([
        csv_row_check("CSV row checks", "phase3_scenario_overlay.csv", TABLES_DIR / "phase3_scenario_overlay.csv"),
        csv_row_check("CSV row checks", "phase3_interactive_payoff_snapshot.csv", TABLES_DIR / "phase3_interactive_payoff_snapshot.csv", optional=True),
    ])

    # Dashboard markers
    checks.extend(marker_check(
        "Main dashboard Phase 3B tab markers",
        "Dashboard",
        PAID_APP_DIR / "config_form_app.py",
        [
            "Phase 3 interactive payoff",
            "Phase 3B scenario overlay",
            "phase3_scenario_overlay_viewer",
            "run_paid_simulator_phase3_scenario_overlay_pipeline_check.py",
        ],
    ))

    # Summary markers are intentionally flexible.
    checks.extend(marker_check(
        "Scenario-overlay summary markers",
        "Scenario-overlay summary",
        REPORTS_DIR / "phase3_scenario_overlay_summary.txt",
        [
            "scenario",
            "covered",
        ],
    ))

    return checks


def is_blocking_failure(item: CheckItem) -> bool:
    if item.optional:
        return False
    return item.status in {"MISSING", "REVIEW"}


def print_report(checks: list[CheckItem]) -> str:
    lines: list[str] = []
    title = "Phase 3B scenario-overlay checkpoint check"
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def emit(line: str = "") -> None:
        print(line)
        lines.append(line)

    emit("=" * 96)
    emit(title)
    emit("=" * 96)
    emit(f"Generated: {generated}")
    emit(f"Project root: {PROJECT_ROOT}")
    emit("")

    sections: list[str] = []
    for item in checks:
        if item.section not in sections:
            sections.append(item.section)

    for section in sections:
        emit(section)
        emit("-" * 96)
        for item in [x for x in checks if x.section == section]:
            emit(f"{item.status:<10} {item.label:<55} {item.detail}")
        emit("")

    blocking_failures = [item for item in checks if is_blocking_failure(item)]
    optional_reviews = [item for item in checks if item.optional and item.status in {"OPTIONAL", "REVIEW"}]

    emit("=" * 96)
    if blocking_failures:
        final_status = "REVIEW"
        emit("Overall Phase 3B checkpoint status: REVIEW")
        emit("One or more required Phase 3B checkpoint items need attention.")
    elif optional_reviews:
        final_status = "PASS WITH OPTIONAL SNAPSHOT REVIEW"
        emit("Overall Phase 3B checkpoint status: PASS WITH OPTIONAL SNAPSHOT REVIEW")
        emit("Only optional snapshot items require review. This is acceptable if no setup has been saved yet.")
    else:
        final_status = "PASS"
        emit("Overall Phase 3B checkpoint status: PASS")
    emit("=" * 96)
    emit("")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    CHECK_REPORT.write_text("\n".join(lines), encoding="utf-8")
    emit(f"Saved checkpoint report: {CHECK_REPORT}")

    return final_status


def main() -> int:
    checks = build_checks()
    final_status = print_report(checks)
    if final_status == "REVIEW":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
