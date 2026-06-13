"""
run_paid_simulator_phase2f_integration_readiness_check.py

Phase 2F model-decision integration-readiness check for the
Covered Call Strategy Stress Test project.

This script verifies that the Phase 2F model-decision layer is installed,
that its outputs are present, and that the main dashboard contains the
Developer-view-only Phase 2F model-decision tab markers.

It checks structure, generated files, CSV row counts, dashboard markers,
viewer markers, and documentation. It does not judge whether any model
should be promoted for customer use.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Iterable


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_SIMULATOR_DIR = APP_DIR / "paid_simulator"
CONFIG_DIR = PROJECT_ROOT / "config"
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
REPORT_PATH = OUTPUT_REPORTS_DIR / "phase2f_integration_readiness_report.txt"


class CheckResult:
    def __init__(self, label: str, status: str, detail: str = "") -> None:
        self.label = label
        self.status = status
        self.detail = detail

    @property
    def passed(self) -> bool:
        return self.status == "PASS"

    def line(self) -> str:
        if self.detail:
            return f"{self.status:<10} {self.label:<62} {self.detail}"
        return f"{self.status:<10} {self.label}"


def banner(title: str) -> str:
    rule = "=" * 100
    return f"{rule}\n{title}\n{rule}"


def section(title: str) -> str:
    return f"\n{title}\n" + "-" * 100


def check_exists(label: str, path: Path) -> CheckResult:
    if path.exists():
        return CheckResult(label, "PASS", str(path))
    return CheckResult(label, "REVIEW", f"Missing: {path}")


def count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            return sum(1 for _ in reader)
    except Exception:
        return 0


def check_csv_rows(label: str, path: Path, minimum_rows: int = 1) -> CheckResult:
    rows = count_csv_rows(path)
    if rows >= minimum_rows:
        return CheckResult(label, "PASS", f"rows={rows}")
    if path.exists():
        return CheckResult(label, "REVIEW", f"rows={rows}; expected at least {minimum_rows}")
    return CheckResult(label, "REVIEW", f"Missing CSV: {path}")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def check_marker(label: str, path: Path, markers: Iterable[str]) -> list[CheckResult]:
    text = read_text(path)
    results: list[CheckResult] = []
    if not text:
        return [CheckResult(label, "REVIEW", f"Could not read: {path}")]
    lower_text = text.lower()
    for marker in markers:
        if marker.lower() in lower_text:
            results.append(CheckResult(f"{label}: {marker}", "PASS"))
        else:
            results.append(CheckResult(f"{label}: {marker}", "REVIEW", f"Marker not found in {path}"))
    return results


def check_any_marker(label: str, path: Path, marker_options: Iterable[str]) -> CheckResult:
    text = read_text(path)
    if not text:
        return CheckResult(label, "REVIEW", f"Could not read: {path}")
    lower_text = text.lower()
    for marker in marker_options:
        if marker.lower() in lower_text:
            return CheckResult(label, "PASS", f"Matched marker: {marker}")
    return CheckResult(label, "REVIEW", f"None of the expected markers found in {path}")


def add_results(lines: list[str], results: list[CheckResult]) -> None:
    for result in results:
        lines.append(result.line())


def main() -> int:
    OUTPUT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append(banner("Phase 2F model-decision integration-readiness check"))
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Project root: {PROJECT_ROOT}")

    all_results: list[CheckResult] = []

    source_files = [
        ("Model-decision summary module", PAID_SIMULATOR_DIR / "model_decision_summary.py"),
        ("Phase 2F model-decision viewer", PAID_SIMULATOR_DIR / "phase2f_model_decision_viewer.py"),
        ("Premium model adjustment module", PAID_SIMULATOR_DIR / "premium_model_adjustment.py"),
        ("Adjusted premium payoff comparison", PAID_SIMULATOR_DIR / "adjusted_premium_payoff_comparison.py"),
        ("Premium model tuning module", PAID_SIMULATOR_DIR / "premium_model_tuning.py"),
        ("Premium-model validation module", PAID_SIMULATOR_DIR / "premium_model_validation.py"),
        ("Option premium model", PAID_SIMULATOR_DIR / "option_premium_model.py"),
        ("Premium-aware payoff runner", PAID_SIMULATOR_DIR / "premium_aware_payoff_runner.py"),
        ("Main dashboard app", PAID_SIMULATOR_DIR / "config_form_app.py"),
        ("Main dashboard launcher", APP_DIR / "run_paid_simulator_form.py"),
    ]

    lines.append(section("Required Phase 2F source files"))
    results = [check_exists(label, path) for label, path in source_files]
    all_results.extend(results)
    add_results(lines, results)

    runner_files = [
        ("Phase 2E checkpoint check", APP_DIR / "run_paid_simulator_phase2e_checkpoint_check.py"),
        ("Model-decision summary check", APP_DIR / "run_paid_simulator_model_decision_summary_check.py"),
        ("Phase 2F model-decision viewer launcher", APP_DIR / "run_paid_simulator_phase2f_model_decision_viewer.py"),
        ("Phase 2F model-decision viewer check", APP_DIR / "run_paid_simulator_phase2f_model_decision_viewer_check.py"),
        ("Phase 2F model-decision pipeline check", APP_DIR / "run_paid_simulator_phase2f_model_decision_pipeline_check.py"),
        ("Phase 2F dashboard-tab check", APP_DIR / "run_paid_simulator_phase2f_dashboard_tab_check.py"),
    ]

    lines.append(section("Required Phase 2F runner/check files"))
    results = [check_exists(label, path) for label, path in runner_files]
    all_results.extend(results)
    add_results(lines, results)

    config_files = [
        ("Premium model adjustment config", CONFIG_DIR / "premium_model_adjustment_config.json"),
        ("Premium model tuning config", CONFIG_DIR / "premium_model_tuning_config.json"),
        ("Premium-model validation config", CONFIG_DIR / "premium_model_validation_config.json"),
    ]

    lines.append(section("Required model-development config files"))
    results = [check_exists(label, path) for label, path in config_files]
    all_results.extend(results)
    add_results(lines, results)

    generated_outputs = [
        ("Model decision CSV", OUTPUT_TABLES_DIR / "model_decision_summary.csv"),
        ("Model decision HTML", OUTPUT_REPORTS_DIR / "model_decision_summary.html"),
        ("Model decision text summary", OUTPUT_REPORTS_DIR / "model_decision_summary.txt"),
        ("Model decision summary check report", OUTPUT_REPORTS_DIR / "phase2f_model_decision_summary_check_report.txt"),
        ("Model decision viewer check report", OUTPUT_REPORTS_DIR / "phase2f_model_decision_viewer_check_report.txt"),
        ("Model decision pipeline report", OUTPUT_REPORTS_DIR / "phase2f_model_decision_pipeline_report.txt"),
        ("Adjusted payoff comparison CSV", OUTPUT_TABLES_DIR / "adjusted_premium_payoff_comparison.csv"),
        ("Adjusted premiums CSV", OUTPUT_TABLES_DIR / "premium_model_adjusted_premiums.csv"),
        ("Premium tuning recommendations CSV", OUTPUT_TABLES_DIR / "premium_model_tuning_recommendations.csv"),
        ("Premium validation CSV", OUTPUT_TABLES_DIR / "premium_model_validation_scaffold.csv"),
        ("Premium-aware payoff CSV", OUTPUT_TABLES_DIR / "premium_aware_payoff_scaffold.csv"),
        ("Option premium CSV", OUTPUT_TABLES_DIR / "option_premium_scaffold.csv"),
    ]

    lines.append(section("Expected Phase 2F generated outputs and context"))
    results = [check_exists(label, path) for label, path in generated_outputs]
    all_results.extend(results)
    add_results(lines, results)

    csv_checks = [
        ("model_decision_summary.csv", OUTPUT_TABLES_DIR / "model_decision_summary.csv"),
        ("adjusted_premium_payoff_comparison.csv", OUTPUT_TABLES_DIR / "adjusted_premium_payoff_comparison.csv"),
        ("premium_model_adjusted_premiums.csv", OUTPUT_TABLES_DIR / "premium_model_adjusted_premiums.csv"),
        ("premium_model_tuning_recommendations.csv", OUTPUT_TABLES_DIR / "premium_model_tuning_recommendations.csv"),
        ("premium_model_validation_scaffold.csv", OUTPUT_TABLES_DIR / "premium_model_validation_scaffold.csv"),
        ("premium_aware_payoff_scaffold.csv", OUTPUT_TABLES_DIR / "premium_aware_payoff_scaffold.csv"),
        ("option_premium_scaffold.csv", OUTPUT_TABLES_DIR / "option_premium_scaffold.csv"),
    ]

    lines.append(section("CSV row checks"))
    results = [check_csv_rows(label, path, minimum_rows=1) for label, path in csv_checks]
    all_results.extend(results)
    add_results(lines, results)

    documentation_files = [
        ("Phase 2F model-decision summary", DOCS_DIR / "paid_simulator_phase2f_model_decision_summary.md"),
        ("Phase 2F model-decision viewer", DOCS_DIR / "paid_simulator_phase2f_model_decision_viewer.md"),
        ("Phase 2F model-decision pipeline", DOCS_DIR / "paid_simulator_phase2f_model_decision_pipeline_check.md"),
        ("Phase 2F dashboard tab", DOCS_DIR / "paid_simulator_phase2f_dashboard_tab.md"),
        ("Phase 2E checkpoint summary", DOCS_DIR / "paid_simulator_phase2e_checkpoint_summary.md"),
        ("Phase 2E integration readiness", DOCS_DIR / "paid_simulator_phase2e_integration_readiness.md"),
    ]

    lines.append(section("Phase 2F documentation"))
    results = [check_exists(label, path) for label, path in documentation_files]
    all_results.extend(results)
    add_results(lines, results)

    lines.append(section("Main dashboard Phase 2F markers"))
    results = check_marker(
        "Dashboard marker",
        PAID_SIMULATOR_DIR / "config_form_app.py",
        [
            "Phase 2F model decision",
            "model_decision_summary",
            "phase2f_model_decision_viewer",
            "run_paid_simulator_phase2f_model_decision_pipeline_check.py",
        ],
    )
    all_results.extend(results)
    add_results(lines, results)

    lines.append(section("Standalone Phase 2F viewer markers"))
    results = check_marker(
        "Viewer marker",
        PAID_SIMULATOR_DIR / "phase2f_model_decision_viewer.py",
        [
            "Phase 2F model-decision viewer",
            "Model decisions",
            "Promotion candidates",
            "model_decision_summary.csv",
        ],
    )
    all_results.extend(results)
    add_results(lines, results)

    lines.append(section("Phase 2F summary markers"))
    results = [
        check_any_marker(
            "Model-decision text summary marker",
            OUTPUT_REPORTS_DIR / "model_decision_summary.txt",
            ["model", "decision", "promotion", "research"],
        ),
        check_any_marker(
            "Model-decision HTML marker",
            OUTPUT_REPORTS_DIR / "model_decision_summary.html",
            ["model", "decision", "summary"],
        ),
    ]
    all_results.extend(results)
    add_results(lines, results)

    status = "PASS" if all(result.passed for result in all_results) else "REVIEW"
    lines.append("")
    lines.append(banner(f"Overall Phase 2F integration-readiness status: {status}"))
    if status == "PASS":
        lines.append("Phase 2F model-decision layer is installed and connected. The project is ready for the Phase 2F checkpoint.")
    else:
        lines.append("One or more Phase 2F integration-readiness items need attention before the Phase 2F checkpoint.")
    lines.append(f"Saved integration-readiness report: {REPORT_PATH}")

    report_text = "\n".join(lines) + "\n"
    REPORT_PATH.write_text(report_text, encoding="utf-8")
    print(report_text)

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
