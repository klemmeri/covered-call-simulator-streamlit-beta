"""
run_paid_simulator_phase3c_checkpoint_check.py

Phase 3C rich graphical payoff checkpoint check.

This version uses tolerant viewer-source marker checks. In particular,
"Buy-and-hold payoff" may appear in the viewer source as "Buy-and-hold",
"Buy and hold", or as an internal variable such as buy_hold.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Iterable


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_APP_DIR = APP_DIR / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

CHECK_REPORT = REPORT_DIR / "phase3c_checkpoint_report.txt"


class CheckResult:
    def __init__(self, status: str, label: str, detail: str = "") -> None:
        self.status = status
        self.label = label
        self.detail = detail


def line(title: str = "", char: str = "=") -> str:
    if title:
        return title
    return char * 96


def check_file(label: str, path: Path, optional: bool = False) -> CheckResult:
    if path.exists():
        return CheckResult("FOUND", label, str(path))
    if optional:
        return CheckResult("OPTIONAL", label, str(path))
    return CheckResult("MISSING", label, str(path))


def count_csv_rows(path: Path) -> int | None:
    try:
        with path.open("r", newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            rows = list(reader)
        if not rows:
            return 0
        return max(0, len(rows) - 1)
    except Exception:
        return None


def check_csv_rows(label: str, path: Path, optional: bool = False) -> CheckResult:
    if not path.exists():
        return CheckResult("OPTIONAL" if optional else "MISSING", label, "file not available")
    row_count = count_csv_rows(path)
    if row_count is None:
        return CheckResult("OPTIONAL" if optional else "REVIEW", label, "file not readable")
    if row_count > 0:
        return CheckResult("PASS", label, f"rows={row_count}")
    return CheckResult("REVIEW", label, "rows=0")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def check_marker(label: str, path: Path, marker: str) -> CheckResult:
    text = read_text(path)
    if marker in text:
        return CheckResult("PASS", label, marker)
    return CheckResult("REVIEW", label, f"marker not found: {marker}")


def check_any_marker(label: str, path: Path, markers: Iterable[str]) -> CheckResult:
    text = read_text(path)
    text_lower = text.lower()
    for marker in markers:
        if marker.lower() in text_lower:
            return CheckResult("PASS", label, marker)
    return CheckResult("REVIEW", label, "none found: " + ", ".join(markers))


def print_section(lines: list[str], title: str) -> None:
    lines.append("")
    lines.append(title)
    lines.append("-" * 96)


def add_result(lines: list[str], result: CheckResult) -> None:
    lines.append(f"{result.status:<10} {result.label:<58} {result.detail}")


def main() -> int:
    lines: list[str] = []
    lines.append("=" * 96)
    lines.append("Phase 3C rich graphical payoff checkpoint check")
    lines.append("=" * 96)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Project root: {PROJECT_ROOT}")

    required_results: list[CheckResult] = []
    optional_results: list[CheckResult] = []

    def record(result: CheckResult, optional_group: bool = False) -> None:
        add_result(lines, result)
        if optional_group or result.status == "OPTIONAL":
            optional_results.append(result)
        else:
            required_results.append(result)

    print_section(lines, "Required Phase 3 / Phase 3B / Phase 3C source files")
    for label, path in [
        ("Phase 3 interactive payoff viewer", PAID_APP_DIR / "phase3_interactive_payoff_viewer.py"),
        ("Phase 3B scenario-overlay model", PAID_APP_DIR / "phase3_scenario_overlay_model.py"),
        ("Phase 3B scenario-overlay viewer", PAID_APP_DIR / "phase3_scenario_overlay_viewer.py"),
        ("Phase 3C rich payoff viewer", PAID_APP_DIR / "phase3c_rich_payoff_viewer.py"),
        ("Main dashboard app", PAID_APP_DIR / "config_form_app.py"),
        ("Main dashboard launcher", APP_DIR / "run_paid_simulator_form.py"),
    ]:
        record(check_file(label, path))

    print_section(lines, "Required Phase 3C runner/check files")
    for label, path in [
        ("Phase 3C viewer launcher", APP_DIR / "run_paid_simulator_phase3c_rich_payoff_viewer.py"),
        ("Phase 3C viewer check", APP_DIR / "run_paid_simulator_phase3c_rich_payoff_viewer_check.py"),
        ("Phase 3C pipeline check", APP_DIR / "run_paid_simulator_phase3c_rich_payoff_pipeline_check.py"),
        ("Phase 3C dashboard-tab check", APP_DIR / "run_paid_simulator_phase3c_dashboard_tab_check.py"),
        ("Phase 3C integration-readiness check", APP_DIR / "run_paid_simulator_phase3c_integration_readiness_check.py"),
    ]:
        record(check_file(label, path))

    print_section(lines, "Required Phase 3B context outputs")
    for label, path in [
        ("Phase 3B scenario-overlay CSV", TABLE_DIR / "phase3_scenario_overlay.csv"),
        ("Phase 3B scenario-overlay HTML", REPORT_DIR / "phase3_scenario_overlay.html"),
        ("Phase 3B scenario-overlay summary", REPORT_DIR / "phase3_scenario_overlay_summary.txt"),
        ("Phase 3B checkpoint report", REPORT_DIR / "phase3b_checkpoint_report.txt"),
    ]:
        record(check_file(label, path))

    print_section(lines, "Required Phase 3C reports")
    for label, path in [
        ("Phase 3C pipeline report", REPORT_DIR / "phase3c_rich_payoff_pipeline_report.txt"),
        ("Phase 3C integration-readiness report", REPORT_DIR / "phase3c_integration_readiness_report.txt"),
    ]:
        record(check_file(label, path))

    print_section(lines, "Optional Phase 3C saved snapshot outputs")
    for label, path in [
        ("Phase 3C rich payoff snapshot CSV", TABLE_DIR / "phase3c_rich_payoff_snapshot.csv"),
        ("Phase 3C rich payoff snapshot HTML", REPORT_DIR / "phase3c_rich_payoff_snapshot.html"),
    ]:
        record(check_file(label, path, optional=True), optional_group=True)

    print_section(lines, "Phase 3 / Phase 3B / Phase 3C documentation")
    for label, path in [
        ("Phase 3 interactive payoff viewer", DOCS_DIR / "paid_simulator_phase3_interactive_payoff_viewer.md"),
        ("Phase 3 checkpoint summary", DOCS_DIR / "paid_simulator_phase3_checkpoint_summary.md"),
        ("Phase 3B scenario-overlay model", DOCS_DIR / "paid_simulator_phase3_scenario_overlay_model.md"),
        ("Phase 3B scenario-overlay viewer", DOCS_DIR / "paid_simulator_phase3_scenario_overlay_viewer.md"),
        ("Phase 3B checkpoint summary", DOCS_DIR / "paid_simulator_phase3b_checkpoint_summary.md"),
        ("Phase 3C rich payoff viewer", DOCS_DIR / "paid_simulator_phase3c_rich_payoff_viewer.md"),
        ("Phase 3C rich payoff pipeline", DOCS_DIR / "paid_simulator_phase3c_rich_payoff_pipeline_check.md"),
        ("Phase 3C dashboard tab", DOCS_DIR / "paid_simulator_phase3c_dashboard_tab.md"),
        ("Phase 3C integration readiness", DOCS_DIR / "paid_simulator_phase3c_integration_readiness.md"),
        ("Phase 3C checkpoint summary", DOCS_DIR / "paid_simulator_phase3c_checkpoint_summary.md"),
    ]:
        record(check_file(label, path))

    print_section(lines, "CSV row checks")
    record(check_csv_rows("phase3_scenario_overlay.csv", TABLE_DIR / "phase3_scenario_overlay.csv"))
    record(check_csv_rows("phase3c_rich_payoff_snapshot.csv", TABLE_DIR / "phase3c_rich_payoff_snapshot.csv", optional=True), optional_group=True)

    dashboard_file = PAID_APP_DIR / "config_form_app.py"
    print_section(lines, "Main dashboard Phase 3C tab markers")
    for label, marker in [
        ("Dashboard marker 'Phase 3 interactive payoff'", "Phase 3 interactive payoff"),
        ("Dashboard marker 'Phase 3B scenario overlay'", "Phase 3B scenario overlay"),
        ("Dashboard marker 'Phase 3C rich payoff'", "Phase 3C rich payoff"),
        ("Dashboard marker 'phase3c_rich_payoff_viewer'", "phase3c_rich_payoff_viewer"),
        ("Dashboard marker 'run_paid_simulator_phase3c_rich_payoff_pipeline_check.py'", "run_paid_simulator_phase3c_rich_payoff_pipeline_check.py"),
    ]:
        record(check_marker(label, dashboard_file, marker))

    viewer_file = PAID_APP_DIR / "phase3c_rich_payoff_viewer.py"
    print_section(lines, "Phase 3C viewer source markers")
    record(check_any_marker("Viewer marker 'Phase 3C'", viewer_file, ["Phase 3C"]))
    record(check_any_marker("Viewer marker 'Covered-call payoff'", viewer_file, ["Covered-call payoff", "Covered call payoff", "covered_call"]))
    record(check_any_marker("Viewer marker 'Buy-and-hold payoff'", viewer_file, ["Buy-and-hold payoff", "Buy-and-hold", "Buy and hold", "buy_hold", "Buy Hold"]))
    record(check_any_marker("Viewer marker 'Strike'", viewer_file, ["Strike", "strike"]))
    record(check_any_marker("Viewer marker 'Breakeven'", viewer_file, ["Breakeven", "Break-even", "break_even", "break even"]))

    blocking = [r for r in required_results if r.status in {"MISSING", "REVIEW"}]
    optional_missing = [r for r in optional_results if r.status in {"OPTIONAL", "MISSING", "REVIEW"}]

    lines.append("")
    lines.append("=" * 96)
    if blocking:
        status_line = "Overall Phase 3C checkpoint status: REVIEW"
        detail_line = "One or more required Phase 3C checkpoint items need attention."
        exit_code = 1
    elif optional_missing:
        status_line = "Overall Phase 3C checkpoint status: PASS WITH OPTIONAL SNAPSHOT REVIEW"
        detail_line = "Only optional snapshot items require review. This is acceptable if no setup has been saved yet."
        exit_code = 0
    else:
        status_line = "Overall Phase 3C checkpoint status: PASS"
        detail_line = "All Phase 3C checkpoint items passed."
        exit_code = 0
    lines.append(status_line)
    lines.append(detail_line)
    lines.append("=" * 96)
    lines.append("")
    lines.append(f"Saved checkpoint report: {CHECK_REPORT}")

    text = "\n".join(lines)
    print(text)
    CHECK_REPORT.write_text(text, encoding="utf-8")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
