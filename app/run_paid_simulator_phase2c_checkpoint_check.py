"""
run_paid_simulator_phase2c_checkpoint_check.py

Checkpoint verifier for the Covered Call Strategy Stress Test Phase 2C
premium-model validation milestone.

This script is intentionally read-only except for writing a plain-text
checkpoint report. It verifies that the Phase 2C validation files, runner
scripts, generated outputs, documentation, and Developer-view dashboard
integration are present after the Phase 2C milestone.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
REPORT_PATH = REPORT_DIR / "phase2c_checkpoint_report.txt"

REQUIRED_SOURCE_FILES = [
    ("Option premium model", PROJECT_ROOT / "app" / "paid_simulator" / "option_premium_model.py"),
    ("Premium-aware payoff runner", PROJECT_ROOT / "app" / "paid_simulator" / "premium_aware_payoff_runner.py"),
    ("Premium-vs-scaffold comparison", PROJECT_ROOT / "app" / "paid_simulator" / "premium_vs_scaffold_comparison.py"),
    ("Premium-model validation module", PROJECT_ROOT / "app" / "paid_simulator" / "premium_model_validation.py"),
    ("Phase 2C validation viewer", PROJECT_ROOT / "app" / "paid_simulator" / "phase2c_premium_validation_viewer.py"),
    ("Main dashboard app", PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"),
    ("Main dashboard launcher", PROJECT_ROOT / "app" / "run_paid_simulator_form.py"),
]

REQUIRED_RUNNER_FILES = [
    ("Option premium check", PROJECT_ROOT / "app" / "run_paid_simulator_option_premium_check.py"),
    ("Premium-aware payoff check", PROJECT_ROOT / "app" / "run_paid_simulator_premium_aware_payoff_check.py"),
    ("Premium-vs-scaffold check", PROJECT_ROOT / "app" / "run_paid_simulator_premium_vs_scaffold_check.py"),
    ("Phase 2B pipeline check", PROJECT_ROOT / "app" / "run_paid_simulator_phase2b_pipeline_check.py"),
    ("Premium-model validation check", PROJECT_ROOT / "app" / "run_paid_simulator_premium_model_validation_check.py"),
    ("Phase 2C validation viewer launcher", PROJECT_ROOT / "app" / "run_paid_simulator_phase2c_premium_validation_viewer.py"),
    ("Phase 2C validation viewer check", PROJECT_ROOT / "app" / "run_paid_simulator_phase2c_premium_validation_viewer_check.py"),
    ("Phase 2C validation pipeline check", PROJECT_ROOT / "app" / "run_paid_simulator_phase2c_validation_pipeline_check.py"),
    ("Phase 2C dashboard-tab check", PROJECT_ROOT / "app" / "run_paid_simulator_phase2c_dashboard_tab_check.py"),
    ("Phase 2C integration-readiness check", PROJECT_ROOT / "app" / "run_paid_simulator_phase2c_integration_readiness_check.py"),
]

EXPECTED_OUTPUTS = [
    ("Option premium CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "option_premium_scaffold.csv"),
    ("Premium-aware payoff CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_aware_payoff_scaffold.csv"),
    ("Premium-aware payoff HTML", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_aware_payoff_scaffold.html"),
    ("Premium-vs-scaffold CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_vs_scaffold_comparison.csv"),
    ("Premium-vs-scaffold HTML", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_vs_scaffold_comparison.html"),
    ("Premium validation CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_model_validation_scaffold.csv"),
    ("Premium validation HTML", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_model_validation_scaffold.html"),
    ("Premium validation summary", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_model_validation_summary.txt"),
    ("Phase 2C validation pipeline report", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2c_validation_pipeline_report.txt"),
    ("Phase 2C integration-readiness report", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2c_integration_readiness_report.txt"),
]

CONFIG_FILES = [
    ("Premium-model validation config", PROJECT_ROOT / "config" / "premium_model_validation_config.json"),
]

DOCS = [
    ("Option premium model scaffold", PROJECT_ROOT / "docs" / "paid_simulator_phase2_option_premium_model_scaffold.md"),
    ("Premium-aware payoff", PROJECT_ROOT / "docs" / "paid_simulator_phase2b_premium_aware_payoff.md"),
    ("Premium-vs-scaffold comparison", PROJECT_ROOT / "docs" / "paid_simulator_phase2b_premium_vs_scaffold_comparison.md"),
    ("Phase 2B pipeline check", PROJECT_ROOT / "docs" / "paid_simulator_phase2b_pipeline_check.md"),
    ("Phase 2B checkpoint summary", PROJECT_ROOT / "docs" / "paid_simulator_phase2b_checkpoint_summary.md"),
    ("Premium-model validation", PROJECT_ROOT / "docs" / "paid_simulator_phase2c_premium_model_validation.md"),
    ("Phase 2C validation viewer", PROJECT_ROOT / "docs" / "paid_simulator_phase2c_premium_validation_viewer.md"),
    ("Phase 2C validation pipeline", PROJECT_ROOT / "docs" / "paid_simulator_phase2c_validation_pipeline_check.md"),
    ("Phase 2C dashboard tab", PROJECT_ROOT / "docs" / "paid_simulator_phase2c_dashboard_tab.md"),
    ("Phase 2C integration readiness", PROJECT_ROOT / "docs" / "paid_simulator_phase2c_integration_readiness.md"),
    ("Phase 2C checkpoint summary", PROJECT_ROOT / "docs" / "paid_simulator_phase2c_checkpoint_summary.md"),
]

CSV_MIN_ROWS = {
    "option_premium_scaffold.csv": 5,
    "premium_aware_payoff_scaffold.csv": 5,
    "premium_vs_scaffold_comparison.csv": 1,
    "premium_model_validation_scaffold.csv": 5,
}

DASHBOARD_REQUIRED_TEXT = [
    "Phase 2B premium model",
    "Phase 2C validation",
    "phase2c_premium_validation_viewer",
    "run_paid_simulator_phase2c_validation_pipeline_check.py",
]

SUMMARY_REQUIRED_TEXT_GROUPS = [
    (
        "Premium-model validation title",
        [
            "Premium-model validation",
            "Premium model validation",
            "Phase 2C premium-model validation",
            "Phase 2C premium model validation",
            "premium_model_validation",
        ],
    ),
    (
        "Overall status",
        [
            "Overall",
            "Overall status",
            "Overall premium-model validation status",
            "Overall Phase 2C premium-model validation status",
        ],
    ),
]


def print_header(title: str) -> None:
    print("\n" + title)
    print("-" * 96)


def check_file(label: str, path: Path) -> bool:
    exists = path.exists() and path.is_file()
    print(f"{'FOUND' if exists else 'MISSING':<10} {label:<48} {path}")
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


def check_dashboard_tab() -> bool:
    dashboard_path = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
    if not dashboard_path.exists():
        print("REVIEW     Main dashboard app is missing; cannot inspect Phase 2C tab text")
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


def normalize_text_for_marker_check(text: str) -> str:
    """Return text in a loose form for non-critical marker checks."""
    return (
        text.lower()
        .replace("-", " ")
        .replace("_", " ")
        .replace("/", " ")
        .replace("\\", " ")
    )


def check_validation_summary() -> bool:
    summary_path = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_model_validation_summary.txt"
    if not summary_path.exists():
        print("REVIEW     Premium-model validation summary is missing")
        return False

    try:
        text = summary_path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        print(f"REVIEW     Could not read validation summary: {exc}")
        return False

    normalized_text = normalize_text_for_marker_check(text)

    ok = True
    for label, marker_options in SUMMARY_REQUIRED_TEXT_GROUPS:
        present = any(
            normalize_text_for_marker_check(marker) in normalized_text
            for marker in marker_options
        )
        if present:
            print(f"{'PASS':<10} Validation-summary marker group {label!r}")
        else:
            print(f"{'REVIEW':<10} Validation-summary marker group {label!r}")
            print(f"{'':<10} Accepted marker options: {', '.join(marker_options)}")
        ok = present and ok
    return ok


def write_checkpoint_report(lines: list[str]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nSaved checkpoint report: {REPORT_PATH}")


def main() -> None:
    transcript: list[str] = []

    def log(message: str) -> None:
        print(message)
        transcript.append(message)

    log("=" * 96)
    log("Phase 2C premium-model validation checkpoint check")
    log("=" * 96)
    log(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Project root: {PROJECT_ROOT}")

    ok = True

    print_header("Required Phase 2B/2C source files")
    transcript.append("\nRequired Phase 2B/2C source files")
    for label, path in REQUIRED_SOURCE_FILES:
        result = check_file(label, path)
        transcript.append(f"{'FOUND' if result else 'MISSING'} {label}: {path}")
        ok = result and ok

    print_header("Required Phase 2B/2C runner/check files")
    transcript.append("\nRequired Phase 2B/2C runner/check files")
    for label, path in REQUIRED_RUNNER_FILES:
        result = check_file(label, path)
        transcript.append(f"{'FOUND' if result else 'MISSING'} {label}: {path}")
        ok = result and ok

    print_header("Required Phase 2C config files")
    transcript.append("\nRequired Phase 2C config files")
    for label, path in CONFIG_FILES:
        result = check_file(label, path)
        transcript.append(f"{'FOUND' if result else 'MISSING'} {label}: {path}")
        ok = result and ok

    print_header("Expected Phase 2B/2C generated outputs")
    transcript.append("\nExpected Phase 2B/2C generated outputs")
    for label, path in EXPECTED_OUTPUTS:
        result = check_file(label, path)
        transcript.append(f"{'FOUND' if result else 'MISSING'} {label}: {path}")
        ok = result and ok

    print_header("Phase 2B/2C documentation")
    transcript.append("\nPhase 2B/2C documentation")
    for label, path in DOCS:
        result = check_file(label, path)
        transcript.append(f"{'FOUND' if result else 'MISSING'} {label}: {path}")
        ok = result and ok

    print_header("CSV row checks")
    transcript.append("\nCSV row checks")
    for filename, min_rows in CSV_MIN_ROWS.items():
        path = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / filename
        rows = count_csv_rows(path)
        if rows is None:
            message = f"REVIEW     {filename:<48} could not be read"
            ok = False
        elif rows < min_rows:
            message = f"REVIEW     {filename:<48} rows={rows}, expected at least {min_rows}"
            ok = False
        else:
            message = f"PASS       {filename:<48} rows={rows}"
        print(message)
        transcript.append(message)

    print_header("Main dashboard Phase 2B/2C tab markers")
    transcript.append("\nMain dashboard Phase 2B/2C tab markers")
    dashboard_ok = check_dashboard_tab()
    ok = dashboard_ok and ok
    transcript.append(f"Dashboard Phase 2B/2C tab markers: {'PASS' if dashboard_ok else 'REVIEW'}")

    print_header("Premium-model validation summary markers")
    transcript.append("\nPremium-model validation summary markers")
    summary_ok = check_validation_summary()
    ok = summary_ok and ok
    transcript.append(f"Premium-model validation summary markers: {'PASS' if summary_ok else 'REVIEW'}")

    final_lines = ["", "=" * 96]
    if ok:
        final_lines.append("Overall Phase 2C checkpoint status: PASS")
        final_lines.append("The Phase 2C premium-model validation milestone files, outputs, docs, and dashboard integration are present.")
        final_lines.append("Recommended next step: begin premium-model assumption tuning.")
    else:
        final_lines.append("Overall Phase 2C checkpoint status: REVIEW")
        final_lines.append("One or more Phase 2C checkpoint items need attention before model tuning.")
    final_lines.append("=" * 96)

    for line in final_lines:
        log(line)

    write_checkpoint_report(transcript + final_lines)
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
