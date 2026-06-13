"""
run_paid_simulator_phase2b_integration_readiness_check.py

Integration-readiness checker for Phase 2B of the Covered Call Strategy
Stress Test project.

This checker is intentionally conservative. It does not modify the working
simulator or dashboard. It verifies that the Phase 2B premium-model layer is
present, that its expected output files exist and contain rows, and that the
main dashboard appears to include the Developer-view-only Phase 2B tab.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_SIM_DIR = APP_DIR / "paid_simulator"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"

REPORT_PATH = OUTPUT_REPORT_DIR / "phase2b_integration_readiness_report.txt"


@dataclass
class CheckResult:
    label: str
    path: Path | None
    status: str
    detail: str


def rel_path(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def count_csv_rows(path: Path) -> int:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return sum(1 for _ in reader)


def read_csv_headers(path: Path) -> list[str]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or [])


def check_file(label: str, path: Path) -> CheckResult:
    if path.exists() and path.is_file():
        return CheckResult(label, path, "PASS", "Found")
    return CheckResult(label, path, "FAIL", "Missing")


def check_csv(label: str, path: Path, required_columns: Iterable[str] | None = None) -> CheckResult:
    if not path.exists():
        return CheckResult(label, path, "FAIL", "Missing CSV")

    try:
        rows = count_csv_rows(path)
        headers = read_csv_headers(path)
    except Exception as exc:  # pragma: no cover - defensive script
        return CheckResult(label, path, "FAIL", f"Could not read CSV: {exc}")

    if rows <= 0:
        return CheckResult(label, path, "FAIL", "CSV exists but has no data rows")

    missing_columns: list[str] = []
    if required_columns:
        normalized_headers = {header.strip().lower() for header in headers}
        for column in required_columns:
            if column.strip().lower() not in normalized_headers:
                missing_columns.append(column)

    if missing_columns:
        return CheckResult(
            label,
            path,
            "REVIEW",
            f"Rows: {rows}; missing expected columns: {', '.join(missing_columns)}",
        )

    return CheckResult(label, path, "PASS", f"Rows: {rows}; columns: {len(headers)}")


def check_text_contains(label: str, path: Path, required_phrases: Iterable[str]) -> CheckResult:
    if not path.exists():
        return CheckResult(label, path, "FAIL", "Missing file")

    try:
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
    except Exception as exc:  # pragma: no cover - defensive script
        return CheckResult(label, path, "FAIL", f"Could not read file: {exc}")

    missing = [phrase for phrase in required_phrases if phrase.lower() not in text]
    if missing:
        return CheckResult(label, path, "REVIEW", f"Missing marker text: {', '.join(missing)}")
    return CheckResult(label, path, "PASS", "Expected marker text found")


def print_section(title: str) -> None:
    print("\n" + title)
    print("-" * 92)


def print_result(result: CheckResult) -> None:
    print(f"{result.status:<7} {result.label:<44} {rel_path(result.path)}")
    if result.detail:
        print(f"        {result.detail}")


def write_report(results: list[CheckResult], overall_status: str) -> None:
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("Phase 2B Integration Readiness Report")
    lines.append("=" * 44)
    lines.append("")
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append(f"Overall status: {overall_status}")
    lines.append("")
    lines.append("Checks")
    lines.append("------")
    for result in results:
        lines.append(f"{result.status:<7} {result.label:<44} {rel_path(result.path)}")
        if result.detail:
            lines.append(f"        {result.detail}")
    lines.append("")
    lines.append("Interpretation")
    lines.append("--------------")
    if overall_status == "PASS":
        lines.append("Phase 2B premium-model integration appears ready for checkpointing.")
        lines.append("The premium model should still remain Developer-view-only until more validation is complete.")
    elif overall_status == "REVIEW":
        lines.append("Phase 2B is mostly present, but one or more non-blocking checks need review.")
    else:
        lines.append("One or more blocking files or outputs are missing. Re-run the Phase 2B pipeline before continuing.")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    print("=" * 92)
    print("Phase 2B premium-model integration readiness check")
    print("=" * 92)
    print(f"Project root: {PROJECT_ROOT}")

    results: list[CheckResult] = []

    print_section("Core Phase 2B model files")
    core_files = [
        ("Option premium model", PAID_SIM_DIR / "option_premium_model.py"),
        ("Premium-aware payoff runner", PAID_SIM_DIR / "premium_aware_payoff_runner.py"),
        ("Premium vs scaffold comparison", PAID_SIM_DIR / "premium_vs_scaffold_comparison.py"),
        ("Phase 2B premium viewer", PAID_SIM_DIR / "phase2b_premium_viewer.py"),
    ]
    for label, path in core_files:
        result = check_file(label, path)
        results.append(result)
        print_result(result)

    print_section("Phase 2B runner/check files")
    runner_files = [
        ("Option premium check", APP_DIR / "run_paid_simulator_option_premium_check.py"),
        ("Premium-aware payoff check", APP_DIR / "run_paid_simulator_premium_aware_payoff_check.py"),
        ("Premium vs scaffold check", APP_DIR / "run_paid_simulator_premium_vs_scaffold_check.py"),
        ("Phase 2B viewer launcher", APP_DIR / "run_paid_simulator_phase2b_premium_viewer.py"),
        ("Phase 2B viewer check", APP_DIR / "run_paid_simulator_phase2b_premium_viewer_check.py"),
        ("Phase 2B pipeline check", APP_DIR / "run_paid_simulator_phase2b_pipeline_check.py"),
        ("Phase 2B dashboard-tab check", APP_DIR / "run_paid_simulator_phase2b_dashboard_tab_check.py"),
    ]
    for label, path in runner_files:
        result = check_file(label, path)
        results.append(result)
        print_result(result)

    print_section("Phase 2B output files")
    csv_checks = [
        (
            "Option premium scaffold CSV",
            OUTPUT_TABLE_DIR / "option_premium_scaffold.csv",
            ["scenario", "estimated_call_premium", "estimated_call_delta"],
        ),
        (
            "Premium-aware payoff CSV",
            OUTPUT_TABLE_DIR / "premium_aware_payoff_scaffold.csv",
            ["scenario", "covered_call_minus_buy_hold", "premium_income"],
        ),
        (
            "Premium vs scaffold CSV",
            OUTPUT_TABLE_DIR / "premium_vs_scaffold_comparison.csv",
            ["scenario", "premium_aware_minus_scaffold"],
        ),
    ]
    for label, path, columns in csv_checks:
        result = check_csv(label, path, columns)
        results.append(result)
        print_result(result)

    html_files = [
        ("Premium-aware payoff HTML", OUTPUT_REPORT_DIR / "premium_aware_payoff_scaffold.html"),
        ("Premium vs scaffold HTML", OUTPUT_REPORT_DIR / "premium_vs_scaffold_comparison.html"),
    ]
    for label, path in html_files:
        result = check_file(label, path)
        results.append(result)
        print_result(result)

    print_section("Main dashboard integration")
    dashboard_result = check_text_contains(
        "Developer-view Phase 2B dashboard tab",
        PAID_SIM_DIR / "config_form_app.py",
        ["Phase 2B premium model", "phase2b"],
    )
    results.append(dashboard_result)
    print_result(dashboard_result)

    print_section("Documentation")
    doc_files = [
        ("Option premium docs", DOCS_DIR / "paid_simulator_phase2_option_premium_model_scaffold.md"),
        ("Premium-aware payoff docs", DOCS_DIR / "paid_simulator_phase2b_premium_aware_payoff.md"),
        ("Premium vs scaffold docs", DOCS_DIR / "paid_simulator_phase2b_premium_vs_scaffold_comparison.md"),
        ("Phase 2B viewer docs", DOCS_DIR / "paid_simulator_phase2b_premium_viewer.md"),
        ("Phase 2B pipeline docs", DOCS_DIR / "paid_simulator_phase2b_pipeline_check.md"),
        ("Phase 2B dashboard-tab docs", DOCS_DIR / "paid_simulator_phase2b_dashboard_tab.md"),
    ]
    for label, path in doc_files:
        result = check_file(label, path)
        results.append(result)
        print_result(result)

    has_fail = any(result.status == "FAIL" for result in results)
    has_review = any(result.status == "REVIEW" for result in results)

    if has_fail:
        overall_status = "FAIL"
    elif has_review:
        overall_status = "REVIEW"
    else:
        overall_status = "PASS"

    write_report(results, overall_status)

    print_section("Overall result")
    print(f"Overall Phase 2B integration-readiness status: {overall_status}")
    print(f"Report written to: {REPORT_PATH}")

    if overall_status == "PASS":
        print("\nNext recommended step: create a Phase 2B checkpoint package or begin validation of the premium model assumptions.")
    elif overall_status == "REVIEW":
        print("\nReview the non-blocking items above before moving Phase 2B closer to customer-facing use.")
    else:
        print("\nRe-run the Phase 2B pipeline and fix missing files before continuing.")


if __name__ == "__main__":
    main()
