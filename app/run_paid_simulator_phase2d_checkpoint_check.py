"""
run_paid_simulator_phase2d_checkpoint_check.py

Checkpoint verifier for the Covered Call Strategy Stress Test Phase 2D
premium-model tuning milestone.

This script is intentionally read-only except for writing a plain-text
checkpoint report. It verifies that the Phase 2D tuning files, runner
scripts, generated outputs, documentation, and Developer-view dashboard
integration are present after the Phase 2D milestone.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_SIMULATOR_DIR = APP_DIR / "paid_simulator"
CONFIG_DIR = PROJECT_ROOT / "config"
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
REPORT_PATH = OUTPUT_REPORTS_DIR / "phase2d_checkpoint_report.txt"


REQUIRED_SOURCE_FILES = [
    ("Option premium model", PAID_SIMULATOR_DIR / "option_premium_model.py"),
    ("Premium-aware payoff runner", PAID_SIMULATOR_DIR / "premium_aware_payoff_runner.py"),
    ("Premium-vs-scaffold comparison", PAID_SIMULATOR_DIR / "premium_vs_scaffold_comparison.py"),
    ("Premium-model validation module", PAID_SIMULATOR_DIR / "premium_model_validation.py"),
    ("Phase 2C validation viewer", PAID_SIMULATOR_DIR / "phase2c_premium_validation_viewer.py"),
    ("Premium-model tuning module", PAID_SIMULATOR_DIR / "premium_model_tuning.py"),
    ("Phase 2D tuning viewer", PAID_SIMULATOR_DIR / "phase2d_premium_tuning_viewer.py"),
    ("Main dashboard app", PAID_SIMULATOR_DIR / "config_form_app.py"),
    ("Main dashboard launcher", APP_DIR / "run_paid_simulator_form.py"),
]

REQUIRED_RUNNER_FILES = [
    ("Option premium check", APP_DIR / "run_paid_simulator_option_premium_check.py"),
    ("Premium-aware payoff check", APP_DIR / "run_paid_simulator_premium_aware_payoff_check.py"),
    ("Premium-vs-scaffold check", APP_DIR / "run_paid_simulator_premium_vs_scaffold_check.py"),
    ("Phase 2B pipeline check", APP_DIR / "run_paid_simulator_phase2b_pipeline_check.py"),
    ("Phase 2B checkpoint check", APP_DIR / "run_paid_simulator_phase2b_checkpoint_check.py"),
    ("Premium-model validation check", APP_DIR / "run_paid_simulator_premium_model_validation_check.py"),
    ("Phase 2C validation viewer launcher", APP_DIR / "run_paid_simulator_phase2c_premium_validation_viewer.py"),
    ("Phase 2C validation viewer check", APP_DIR / "run_paid_simulator_phase2c_premium_validation_viewer_check.py"),
    ("Phase 2C validation pipeline check", APP_DIR / "run_paid_simulator_phase2c_validation_pipeline_check.py"),
    ("Phase 2C dashboard-tab check", APP_DIR / "run_paid_simulator_phase2c_dashboard_tab_check.py"),
    ("Phase 2C integration-readiness check", APP_DIR / "run_paid_simulator_phase2c_integration_readiness_check.py"),
    ("Phase 2C checkpoint check", APP_DIR / "run_paid_simulator_phase2c_checkpoint_check.py"),
    ("Premium-model tuning check", APP_DIR / "run_paid_simulator_premium_model_tuning_check.py"),
    ("Phase 2D tuning viewer launcher", APP_DIR / "run_paid_simulator_phase2d_premium_tuning_viewer.py"),
    ("Phase 2D tuning viewer check", APP_DIR / "run_paid_simulator_phase2d_premium_tuning_viewer_check.py"),
    ("Phase 2D tuning pipeline check", APP_DIR / "run_paid_simulator_phase2d_tuning_pipeline_check.py"),
    ("Phase 2D dashboard-tab check", APP_DIR / "run_paid_simulator_phase2d_dashboard_tab_check.py"),
    ("Phase 2D integration-readiness check", APP_DIR / "run_paid_simulator_phase2d_integration_readiness_check.py"),
]

CONFIG_FILES = [
    ("Premium-model validation config", CONFIG_DIR / "premium_model_validation_config.json"),
    ("Premium-model tuning config", CONFIG_DIR / "premium_model_tuning_config.json"),
]

EXPECTED_OUTPUTS = [
    ("Option premium CSV", OUTPUT_TABLES_DIR / "option_premium_scaffold.csv"),
    ("Premium-aware payoff CSV", OUTPUT_TABLES_DIR / "premium_aware_payoff_scaffold.csv"),
    ("Premium-aware payoff HTML", OUTPUT_REPORTS_DIR / "premium_aware_payoff_scaffold.html"),
    ("Premium-vs-scaffold CSV", OUTPUT_TABLES_DIR / "premium_vs_scaffold_comparison.csv"),
    ("Premium-vs-scaffold HTML", OUTPUT_REPORTS_DIR / "premium_vs_scaffold_comparison.html"),
    ("Premium validation CSV", OUTPUT_TABLES_DIR / "premium_model_validation_scaffold.csv"),
    ("Premium validation HTML", OUTPUT_REPORTS_DIR / "premium_model_validation_scaffold.html"),
    ("Premium validation summary", OUTPUT_REPORTS_DIR / "premium_model_validation_summary.txt"),
    ("Phase 2C validation pipeline report", OUTPUT_REPORTS_DIR / "phase2c_validation_pipeline_report.txt"),
    ("Phase 2C integration-readiness report", OUTPUT_REPORTS_DIR / "phase2c_integration_readiness_report.txt"),
    ("Phase 2C checkpoint report", OUTPUT_REPORTS_DIR / "phase2c_checkpoint_report.txt"),
    ("Premium tuning recommendations CSV", OUTPUT_TABLES_DIR / "premium_model_tuning_recommendations.csv"),
    ("Premium tuning recommendations HTML", OUTPUT_REPORTS_DIR / "premium_model_tuning_recommendations.html"),
    ("Premium tuning summary", OUTPUT_REPORTS_DIR / "premium_model_tuning_summary.txt"),
    ("Phase 2D tuning check report", OUTPUT_REPORTS_DIR / "phase2d_premium_model_tuning_check_report.txt"),
    ("Phase 2D tuning pipeline report", OUTPUT_REPORTS_DIR / "phase2d_tuning_pipeline_report.txt"),
    ("Phase 2D integration-readiness report", OUTPUT_REPORTS_DIR / "phase2d_integration_readiness_report.txt"),
]

DOCS = [
    ("Option premium model scaffold", DOCS_DIR / "paid_simulator_phase2_option_premium_model_scaffold.md"),
    ("Premium-aware payoff", DOCS_DIR / "paid_simulator_phase2b_premium_aware_payoff.md"),
    ("Premium-vs-scaffold comparison", DOCS_DIR / "paid_simulator_phase2b_premium_vs_scaffold_comparison.md"),
    ("Phase 2B pipeline check", DOCS_DIR / "paid_simulator_phase2b_pipeline_check.md"),
    ("Phase 2B checkpoint summary", DOCS_DIR / "paid_simulator_phase2b_checkpoint_summary.md"),
    ("Premium-model validation", DOCS_DIR / "paid_simulator_phase2c_premium_model_validation.md"),
    ("Phase 2C validation viewer", DOCS_DIR / "paid_simulator_phase2c_premium_validation_viewer.md"),
    ("Phase 2C validation pipeline", DOCS_DIR / "paid_simulator_phase2c_validation_pipeline_check.md"),
    ("Phase 2C dashboard tab", DOCS_DIR / "paid_simulator_phase2c_dashboard_tab.md"),
    ("Phase 2C integration readiness", DOCS_DIR / "paid_simulator_phase2c_integration_readiness.md"),
    ("Phase 2C checkpoint summary", DOCS_DIR / "paid_simulator_phase2c_checkpoint_summary.md"),
    ("Phase 2D premium model tuning", DOCS_DIR / "paid_simulator_phase2d_premium_model_tuning.md"),
    ("Phase 2D tuning viewer", DOCS_DIR / "paid_simulator_phase2d_premium_tuning_viewer.md"),
    ("Phase 2D tuning pipeline", DOCS_DIR / "paid_simulator_phase2d_tuning_pipeline_check.md"),
    ("Phase 2D dashboard tab", DOCS_DIR / "paid_simulator_phase2d_dashboard_tab.md"),
    ("Phase 2D integration readiness", DOCS_DIR / "paid_simulator_phase2d_integration_readiness.md"),
    ("Phase 2D checkpoint summary", DOCS_DIR / "paid_simulator_phase2d_checkpoint_summary.md"),
]

CSV_MIN_ROWS = {
    "option_premium_scaffold.csv": 5,
    "premium_aware_payoff_scaffold.csv": 5,
    "premium_vs_scaffold_comparison.csv": 1,
    "premium_model_validation_scaffold.csv": 5,
    "premium_model_tuning_recommendations.csv": 1,
}

DASHBOARD_REQUIRED_TEXT = [
    "Phase 2B premium model",
    "Phase 2C validation",
    "Phase 2D tuning",
    "phase2d_premium_tuning_viewer",
    "run_paid_simulator_phase2d_tuning_pipeline_check.py",
]

TUNING_SUMMARY_REQUIRED_TEXT_GROUPS = [
    (
        "Premium-model tuning title",
        [
            "Premium-model tuning",
            "Premium model tuning",
            "Phase 2D premium-model tuning",
            "Phase 2D premium model tuning",
            "premium_model_tuning",
            "tuning recommendations",
        ],
    ),
    (
        "Overall status",
        [
            "Overall",
            "Overall status",
            "Overall premium-model tuning status",
            "Overall Phase 2D premium-model tuning status",
            "recommendation",
        ],
    ),
]


def print_header(title: str) -> None:
    print("\n" + title)
    print("-" * 96)


def check_file(label: str, path: Path) -> bool:
    exists = path.exists() and path.is_file()
    print(f"{'FOUND' if exists else 'MISSING':<10} {label:<52} {path}")
    return exists


def count_csv_rows(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            rows = list(reader)
        return max(len(rows) - 1, 0)
    except Exception:
        return None


def normalize_text_for_marker_check(text: str) -> str:
    return (
        text.lower()
        .replace("-", " ")
        .replace("_", " ")
        .replace("/", " ")
        .replace("\\", " ")
    )


def check_dashboard_markers() -> bool:
    dashboard_path = PAID_SIMULATOR_DIR / "config_form_app.py"
    if not dashboard_path.exists():
        print("REVIEW     Main dashboard app is missing; cannot inspect Phase 2D tab text")
        return False

    try:
        text = dashboard_path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        print(f"REVIEW     Could not read dashboard file: {exc}")
        return False

    ok = True
    for marker in DASHBOARD_REQUIRED_TEXT:
        present = marker in text
        print(f"{'PASS' if present else 'REVIEW':<10} Dashboard marker {marker!r}")
        ok = present and ok
    return ok


def check_tuning_summary_markers() -> bool:
    summary_path = OUTPUT_REPORTS_DIR / "premium_model_tuning_summary.txt"
    if not summary_path.exists():
        print("REVIEW     Premium-model tuning summary is missing")
        return False

    try:
        text = summary_path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        print(f"REVIEW     Could not read tuning summary: {exc}")
        return False

    normalized_text = normalize_text_for_marker_check(text)

    ok = True
    for label, marker_options in TUNING_SUMMARY_REQUIRED_TEXT_GROUPS:
        present = any(
            normalize_text_for_marker_check(marker) in normalized_text
            for marker in marker_options
        )
        if present:
            print(f"{'PASS':<10} Tuning-summary marker group {label!r}")
        else:
            print(f"{'REVIEW':<10} Tuning-summary marker group {label!r}")
            print(f"{'':<10} Accepted marker options: {', '.join(marker_options)}")
        ok = present and ok
    return ok


def write_checkpoint_report(lines: list[str]) -> None:
    OUTPUT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nSaved checkpoint report: {REPORT_PATH}")


def main() -> None:
    transcript: list[str] = []

    def log(message: str) -> None:
        print(message)
        transcript.append(message)

    log("=" * 96)
    log("Phase 2D premium-model tuning checkpoint check")
    log("=" * 96)
    log(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Project root: {PROJECT_ROOT}")

    ok = True

    print_header("Required Phase 2B/2C/2D source files")
    transcript.append("\nRequired Phase 2B/2C/2D source files")
    for label, path in REQUIRED_SOURCE_FILES:
        result = check_file(label, path)
        transcript.append(f"{'FOUND' if result else 'MISSING'} {label}: {path}")
        ok = result and ok

    print_header("Required Phase 2B/2C/2D runner/check files")
    transcript.append("\nRequired Phase 2B/2C/2D runner/check files")
    for label, path in REQUIRED_RUNNER_FILES:
        result = check_file(label, path)
        transcript.append(f"{'FOUND' if result else 'MISSING'} {label}: {path}")
        ok = result and ok

    print_header("Required Phase 2C/2D config files")
    transcript.append("\nRequired Phase 2C/2D config files")
    for label, path in CONFIG_FILES:
        result = check_file(label, path)
        transcript.append(f"{'FOUND' if result else 'MISSING'} {label}: {path}")
        ok = result and ok

    print_header("Expected Phase 2B/2C/2D generated outputs")
    transcript.append("\nExpected Phase 2B/2C/2D generated outputs")
    for label, path in EXPECTED_OUTPUTS:
        result = check_file(label, path)
        transcript.append(f"{'FOUND' if result else 'MISSING'} {label}: {path}")
        ok = result and ok

    print_header("Phase 2B/2C/2D documentation")
    transcript.append("\nPhase 2B/2C/2D documentation")
    for label, path in DOCS:
        result = check_file(label, path)
        transcript.append(f"{'FOUND' if result else 'MISSING'} {label}: {path}")
        ok = result and ok

    print_header("CSV row checks")
    transcript.append("\nCSV row checks")
    for filename, min_rows in CSV_MIN_ROWS.items():
        path = OUTPUT_TABLES_DIR / filename
        rows = count_csv_rows(path)
        if rows is None:
            message = f"REVIEW     {filename:<52} could not be read"
            ok = False
        elif rows < min_rows:
            message = f"REVIEW     {filename:<52} rows={rows}, expected at least {min_rows}"
            ok = False
        else:
            message = f"PASS       {filename:<52} rows={rows}"
        print(message)
        transcript.append(message)

    print_header("Main dashboard Phase 2B/2C/2D tab markers")
    transcript.append("\nMain dashboard Phase 2B/2C/2D tab markers")
    dashboard_ok = check_dashboard_markers()
    ok = dashboard_ok and ok
    transcript.append(f"Dashboard Phase 2B/2C/2D tab markers: {'PASS' if dashboard_ok else 'REVIEW'}")

    print_header("Premium-model tuning summary markers")
    transcript.append("\nPremium-model tuning summary markers")
    summary_ok = check_tuning_summary_markers()
    ok = summary_ok and ok
    transcript.append(f"Premium-model tuning summary markers: {'PASS' if summary_ok else 'REVIEW'}")

    final_lines = ["", "=" * 96]
    if ok:
        final_lines.append("Overall Phase 2D checkpoint status: PASS")
        final_lines.append("The Phase 2D premium-model tuning milestone files, outputs, docs, and dashboard integration are present.")
        final_lines.append("Recommended next step: apply the first controlled premium-model tuning adjustment.")
    else:
        final_lines.append("Overall Phase 2D checkpoint status: REVIEW")
        final_lines.append("One or more Phase 2D checkpoint items need attention before applying tuning adjustments.")
    final_lines.append("=" * 96)

    for line in final_lines:
        log(line)

    write_checkpoint_report(transcript + final_lines)
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
