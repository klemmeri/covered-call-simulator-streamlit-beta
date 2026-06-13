"""
run_paid_simulator_phase2c_integration_readiness_check.py

Integration-readiness checker for Phase 2C premium-model validation.

This script verifies that the Phase 2C validation layer is installed,
that its pipeline can run, that the Developer-view dashboard tab check
passes, and that the expected CSV/HTML/text outputs exist.

It is intentionally conservative: it does not modify the main dashboard
or simulator logic. It only runs existing check scripts and writes a
plain-text readiness report.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
REPORT_PATH = REPORT_DIR / "phase2c_integration_readiness_report.txt"


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str


def status_line(status: str) -> str:
    return status.upper().ljust(7)


def run_script(relative_path: str, label: str) -> CheckResult:
    script_path = PROJECT_ROOT / relative_path
    if not script_path.exists():
        return CheckResult(label, "FAIL", f"Missing script: {script_path}")

    try:
        completed = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(PROJECT_ROOT),
            text=True,
            capture_output=True,
            check=False,
        )
    except Exception as exc:  # pragma: no cover - defensive for local environment
        return CheckResult(label, "FAIL", f"Could not run script: {exc}")

    if completed.returncode == 0:
        return CheckResult(label, "PASS", f"Ran successfully: {relative_path}")

    tail = "\n".join((completed.stdout + "\n" + completed.stderr).splitlines()[-12:])
    return CheckResult(label, "FAIL", f"Script returned {completed.returncode}: {relative_path}\n{tail}")


def check_file(relative_path: str, label: str) -> CheckResult:
    path = PROJECT_ROOT / relative_path
    if path.exists() and path.is_file():
        return CheckResult(label, "PASS", f"Found: {path}")
    return CheckResult(label, "FAIL", f"Missing: {path}")


def check_csv_has_rows(relative_path: str, label: str) -> CheckResult:
    path = PROJECT_ROOT / relative_path
    if not path.exists():
        return CheckResult(label, "FAIL", f"Missing CSV: {path}")

    try:
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            reader = csv.reader(handle)
            rows = list(reader)
    except Exception as exc:
        return CheckResult(label, "FAIL", f"Could not read CSV: {path} ({exc})")

    data_rows = max(0, len(rows) - 1)
    if data_rows > 0:
        return CheckResult(label, "PASS", f"CSV has {data_rows} data row(s): {path}")
    return CheckResult(label, "FAIL", f"CSV has no data rows: {path}")


def check_text_contains(relative_path: str, label: str, required_terms: list[str]) -> CheckResult:
    path = PROJECT_ROOT / relative_path
    if not path.exists():
        return CheckResult(label, "FAIL", f"Missing file: {path}")

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return CheckResult(label, "FAIL", f"Could not read file: {path} ({exc})")

    missing = [term for term in required_terms if term not in text]
    if not missing:
        return CheckResult(label, "PASS", f"Required text found in: {path}")
    return CheckResult(label, "FAIL", f"Missing text {missing} in: {path}")


def write_report(results: list[CheckResult]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    overall = "PASS" if all(item.status == "PASS" for item in results) else "REVIEW"

    lines: list[str] = []
    lines.append("Phase 2C integration-readiness report")
    lines.append("=" * 72)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append(f"Overall status: {overall}")
    lines.append("")

    for item in results:
        lines.append(f"{status_line(item.status)} {item.name}")
        lines.append(f"        {item.detail}")
        lines.append("")

    if overall == "PASS":
        lines.append("Interpretation:")
        lines.append("The Phase 2C validation layer is installed, runnable, and connected to the Developer-view dashboard path.")
        lines.append("The project is ready for premium-model assumption tuning.")
    else:
        lines.append("Interpretation:")
        lines.append("At least one Phase 2C readiness check needs attention before moving on to model tuning.")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    print("=" * 92)
    print("Phase 2C integration-readiness check")
    print("=" * 92)
    print(f"Project root: {PROJECT_ROOT}")
    print("")

    results: list[CheckResult] = []

    # Run end-to-end checks first so the expected outputs are refreshed.
    results.append(run_script("app/run_paid_simulator_phase2c_validation_pipeline_check.py", "Run Phase 2C validation pipeline"))
    results.append(run_script("app/run_paid_simulator_phase2c_dashboard_tab_check.py", "Run Phase 2C dashboard-tab check"))

    # Core Phase 2C files.
    required_files = [
        ("app/paid_simulator/premium_model_validation.py", "Premium-model validation module"),
        ("app/run_paid_simulator_premium_model_validation_check.py", "Premium-model validation check script"),
        ("app/paid_simulator/phase2c_premium_validation_viewer.py", "Phase 2C validation viewer app"),
        ("app/run_paid_simulator_phase2c_premium_validation_viewer.py", "Phase 2C validation viewer launcher"),
        ("app/run_paid_simulator_phase2c_premium_validation_viewer_check.py", "Phase 2C validation viewer check"),
        ("app/run_paid_simulator_phase2c_validation_pipeline_check.py", "Phase 2C validation pipeline check"),
        ("app/run_paid_simulator_phase2c_dashboard_tab_check.py", "Phase 2C dashboard-tab check"),
        ("config/premium_model_validation_config.json", "Premium-model validation config"),
        ("docs/paid_simulator_phase2c_premium_model_validation.md", "Phase 2C validation documentation"),
        ("docs/paid_simulator_phase2c_premium_validation_viewer.md", "Phase 2C validation viewer documentation"),
        ("docs/paid_simulator_phase2c_validation_pipeline_check.md", "Phase 2C validation pipeline documentation"),
        ("docs/paid_simulator_phase2c_dashboard_tab.md", "Phase 2C dashboard-tab documentation"),
    ]
    for relative_path, label in required_files:
        results.append(check_file(relative_path, label))

    # Expected refreshed outputs.
    csv_outputs = [
        ("outputs/tables/paid_simulator/option_premium_scaffold.csv", "Option-premium scaffold CSV"),
        ("outputs/tables/paid_simulator/premium_aware_payoff_scaffold.csv", "Premium-aware payoff CSV"),
        ("outputs/tables/paid_simulator/premium_model_validation_scaffold.csv", "Premium-model validation CSV"),
    ]
    for relative_path, label in csv_outputs:
        results.append(check_csv_has_rows(relative_path, label))

    output_files = [
        ("outputs/reports/paid_simulator/premium_aware_payoff_scaffold.html", "Premium-aware payoff HTML report"),
        ("outputs/reports/paid_simulator/premium_vs_scaffold_comparison.html", "Premium-vs-scaffold HTML report"),
        ("outputs/reports/paid_simulator/premium_model_validation_scaffold.html", "Premium-model validation HTML report"),
        ("outputs/reports/paid_simulator/premium_model_validation_summary.txt", "Premium-model validation summary"),
        ("outputs/reports/paid_simulator/phase2c_validation_pipeline_report.txt", "Phase 2C validation pipeline report"),
    ]
    for relative_path, label in output_files:
        results.append(check_file(relative_path, label))

    # Main dashboard should contain the Developer-view-only tab label.
    results.append(
        check_text_contains(
            "app/paid_simulator/config_form_app.py",
            "Main dashboard contains Phase 2C tab label",
            ["Phase 2C validation"],
        )
    )

    write_report(results)

    for item in results:
        print(f"{status_line(item.status)} {item.name}")
        print(f"        {item.detail}")

    overall = "PASS" if all(item.status == "PASS" for item in results) else "REVIEW"
    print("")
    print("-" * 92)
    print(f"Overall Phase 2C integration-readiness status: {overall}")
    print(f"Report written to: {REPORT_PATH}")
    print("-" * 92)

    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
