"""
run_paid_simulator_phase2e_checkpoint_check.py

Phase 2E controlled premium-adjustment checkpoint checker for the
Covered Call Strategy Stress Test paid simulator.

This script is intentionally read-only except for writing its checkpoint
report. It verifies that the Phase 2E adjustment milestone is installed,
connected, and producing the expected files before the project moves to the
next modeling step.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]

APP_DIR = PROJECT_ROOT / "app"
PAID_APP_DIR = APP_DIR / "paid_simulator"
CONFIG_DIR = PROJECT_ROOT / "config"
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CHECKPOINT_REPORT_PATH = OUTPUT_REPORTS_DIR / "phase2e_checkpoint_report.txt"


@dataclass
class CheckResult:
    section: str
    label: str
    status: str
    detail: str


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def check_file(section: str, label: str, path: Path) -> CheckResult:
    if path.exists():
        return CheckResult(section, label, "FOUND", str(path))
    return CheckResult(section, label, "MISSING", str(path))


def count_csv_rows(path: Path) -> tuple[bool, int, str]:
    if not path.exists():
        return False, 0, "file missing"

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            rows = list(reader)
    except Exception as exc:  # pragma: no cover - diagnostic path
        return False, 0, f"could not read CSV: {exc}"

    if not rows:
        return False, 0, "CSV is empty"

    data_rows = max(len(rows) - 1, 0)
    if data_rows <= 0:
        return False, data_rows, "CSV has no data rows"

    return True, data_rows, f"rows={data_rows}"


def check_csv_rows(section: str, label: str, path: Path) -> CheckResult:
    ok, row_count, detail = count_csv_rows(path)
    status = "PASS" if ok else "REVIEW"
    return CheckResult(section, label, status, detail)


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def check_marker_any(section: str, label: str, path: Path, markers: Iterable[str]) -> CheckResult:
    text = read_text(path)
    if not text:
        return CheckResult(section, label, "REVIEW", f"could not read {rel(path)}")

    lowered = text.lower()
    for marker in markers:
        if marker.lower() in lowered:
            return CheckResult(section, label, "PASS", f"found marker: {marker}")

    marker_text = " OR ".join(markers)
    return CheckResult(section, label, "REVIEW", f"missing marker: {marker_text}")


def section_title(title: str) -> str:
    return f"\n{title}\n" + "-" * 96


def print_result(result: CheckResult) -> None:
    print(f"{result.status:<10} {result.label:<52} {result.detail}")


def write_report(results: list[CheckResult], overall_status: str) -> None:
    OUTPUT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("Phase 2E controlled premium-adjustment checkpoint report")
    lines.append("=" * 96)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append("")

    current_section = None
    for result in results:
        if result.section != current_section:
            current_section = result.section
            lines.append(result.section)
            lines.append("-" * 96)
        lines.append(f"{result.status:<10} {result.label:<52} {result.detail}")
    lines.append("")
    lines.append(f"Overall Phase 2E checkpoint status: {overall_status}")

    CHECKPOINT_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    print("=" * 96)
    print("Phase 2E controlled premium-adjustment checkpoint check")
    print("=" * 96)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project root: {PROJECT_ROOT}")

    results: list[CheckResult] = []

    required_source_files = [
        ("Option premium model", PAID_APP_DIR / "option_premium_model.py"),
        ("Premium-aware payoff runner", PAID_APP_DIR / "premium_aware_payoff_runner.py"),
        ("Premium-vs-scaffold comparison", PAID_APP_DIR / "premium_vs_scaffold_comparison.py"),
        ("Premium-model validation module", PAID_APP_DIR / "premium_model_validation.py"),
        ("Premium-model tuning module", PAID_APP_DIR / "premium_model_tuning.py"),
        ("Premium-model adjustment module", PAID_APP_DIR / "premium_model_adjustment.py"),
        ("Adjusted payoff comparison module", PAID_APP_DIR / "adjusted_premium_payoff_comparison.py"),
        ("Phase 2E adjustment viewer", PAID_APP_DIR / "phase2e_adjustment_viewer.py"),
        ("Main dashboard app", PAID_APP_DIR / "config_form_app.py"),
        ("Main dashboard launcher", APP_DIR / "run_paid_simulator_form.py"),
    ]

    required_runner_files = [
        ("Phase 2D checkpoint check", APP_DIR / "run_paid_simulator_phase2d_checkpoint_check.py"),
        ("Premium-model adjustment check", APP_DIR / "run_paid_simulator_premium_model_adjustment_check.py"),
        ("Adjusted payoff comparison check", APP_DIR / "run_paid_simulator_adjusted_premium_payoff_comparison_check.py"),
        ("Phase 2E viewer launcher", APP_DIR / "run_paid_simulator_phase2e_adjustment_viewer.py"),
        ("Phase 2E viewer check", APP_DIR / "run_paid_simulator_phase2e_adjustment_viewer_check.py"),
        ("Phase 2E pipeline check", APP_DIR / "run_paid_simulator_phase2e_adjustment_pipeline_check.py"),
        ("Phase 2E dashboard-tab check", APP_DIR / "run_paid_simulator_phase2e_dashboard_tab_check.py"),
        ("Phase 2E integration-readiness check", APP_DIR / "run_paid_simulator_phase2e_integration_readiness_check.py"),
    ]

    required_config_files = [
        ("Premium-model adjustment config", CONFIG_DIR / "premium_model_adjustment_config.json"),
    ]

    expected_outputs = [
        ("Adjusted premiums CSV", OUTPUT_TABLES_DIR / "premium_model_adjusted_premiums.csv"),
        ("Adjustment comparison HTML", OUTPUT_REPORTS_DIR / "premium_model_adjustment_comparison.html"),
        ("Adjustment summary TXT", OUTPUT_REPORTS_DIR / "premium_model_adjustment_summary.txt"),
        ("Adjusted payoff comparison CSV", OUTPUT_TABLES_DIR / "adjusted_premium_payoff_comparison.csv"),
        ("Adjusted payoff comparison HTML", OUTPUT_REPORTS_DIR / "adjusted_premium_payoff_comparison.html"),
        ("Adjusted payoff summary TXT", OUTPUT_REPORTS_DIR / "adjusted_premium_payoff_summary.txt"),
        ("Phase 2E pipeline report", OUTPUT_REPORTS_DIR / "phase2e_adjustment_pipeline_report.txt"),
        ("Phase 2E integration-readiness report", OUTPUT_REPORTS_DIR / "phase2e_integration_readiness_report.txt"),
    ]

    required_docs = [
        ("Phase 2E premium adjustment", DOCS_DIR / "paid_simulator_phase2e_premium_model_adjustment.md"),
        ("Phase 2E adjusted payoff comparison", DOCS_DIR / "paid_simulator_phase2e_adjusted_premium_payoff_comparison.md"),
        ("Phase 2E adjustment viewer", DOCS_DIR / "paid_simulator_phase2e_adjustment_viewer.md"),
        ("Phase 2E pipeline check", DOCS_DIR / "paid_simulator_phase2e_adjustment_pipeline_check.md"),
        ("Phase 2E dashboard tab", DOCS_DIR / "paid_simulator_phase2e_dashboard_tab.md"),
        ("Phase 2E integration readiness", DOCS_DIR / "paid_simulator_phase2e_integration_readiness.md"),
        ("Phase 2E checkpoint summary", DOCS_DIR / "paid_simulator_phase2e_checkpoint_summary.md"),
    ]

    csv_outputs = [
        ("premium_model_adjusted_premiums.csv", OUTPUT_TABLES_DIR / "premium_model_adjusted_premiums.csv"),
        ("adjusted_premium_payoff_comparison.csv", OUTPUT_TABLES_DIR / "adjusted_premium_payoff_comparison.csv"),
    ]

    print(section_title("Required Phase 2E source files"))
    for label, path in required_source_files:
        result = check_file("Required Phase 2E source files", label, path)
        results.append(result)
        print_result(result)

    print(section_title("Required Phase 2E runner/check files"))
    for label, path in required_runner_files:
        result = check_file("Required Phase 2E runner/check files", label, path)
        results.append(result)
        print_result(result)

    print(section_title("Required Phase 2E config files"))
    for label, path in required_config_files:
        result = check_file("Required Phase 2E config files", label, path)
        results.append(result)
        print_result(result)

    print(section_title("Expected Phase 2E generated outputs"))
    for label, path in expected_outputs:
        result = check_file("Expected Phase 2E generated outputs", label, path)
        results.append(result)
        print_result(result)

    print(section_title("Phase 2E documentation"))
    for label, path in required_docs:
        result = check_file("Phase 2E documentation", label, path)
        results.append(result)
        print_result(result)

    print(section_title("CSV row checks"))
    for label, path in csv_outputs:
        result = check_csv_rows("CSV row checks", label, path)
        results.append(result)
        print_result(result)

    print(section_title("Main dashboard Phase 2E tab markers"))
    dashboard_path = PAID_APP_DIR / "config_form_app.py"
    dashboard_marker_checks = [
        ("Dashboard marker 'Phase 2E adjustment'", ["Phase 2E adjustment"]),
        ("Dashboard marker 'phase2e_adjustment_viewer'", ["phase2e_adjustment_viewer"]),
        ("Dashboard marker 'run_paid_simulator_phase2e_adjustment_pipeline_check.py'", ["run_paid_simulator_phase2e_adjustment_pipeline_check.py"]),
        ("Dashboard marker 'premium_model_adjusted_premiums.csv'", ["premium_model_adjusted_premiums.csv"]),
    ]
    for label, markers in dashboard_marker_checks:
        result = check_marker_any("Main dashboard Phase 2E tab markers", label, dashboard_path, markers)
        results.append(result)
        print_result(result)

    print(section_title("Phase 2E report markers"))
    report_marker_checks = [
        (
            "Adjustment summary marker",
            OUTPUT_REPORTS_DIR / "premium_model_adjustment_summary.txt",
            ["premium model adjustment", "adjusted premium", "adjustment"],
        ),
        (
            "Adjusted payoff summary marker",
            OUTPUT_REPORTS_DIR / "adjusted_premium_payoff_summary.txt",
            ["adjusted premium", "covered-call", "payoff"],
        ),
        (
            "Integration report marker",
            OUTPUT_REPORTS_DIR / "phase2e_integration_readiness_report.txt",
            ["Phase 2E", "integration"],
        ),
    ]
    for label, path, markers in report_marker_checks:
        result = check_marker_any("Phase 2E report markers", label, path, markers)
        results.append(result)
        print_result(result)

    failures = [r for r in results if r.status in {"MISSING", "REVIEW"}]
    overall_status = "PASS" if not failures else "REVIEW"

    print("\n" + "=" * 96)
    print(f"Overall Phase 2E checkpoint status: {overall_status}")
    if overall_status == "PASS":
        print("Phase 2E controlled premium-adjustment milestone is installed and connected.")
    else:
        print("One or more Phase 2E checkpoint items need attention before the next step.")
    print("=" * 96)

    write_report(results, overall_status)
    print(f"\nSaved checkpoint report: {CHECKPOINT_REPORT_PATH}")

    return 0 if overall_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
