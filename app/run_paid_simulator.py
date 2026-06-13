"""
run_paid_simulator.py

Top-level launcher for the paid Covered Call Simulator scenario comparison.

Place this file in:

    app/run_paid_simulator.py

Run it from PyCharm to execute:

    app/paid_simulator/runner.py

The launcher:
    1. Runs the compact paid-simulator scenario comparison.
    2. Uses the correct working directory for imports.
    3. Prints the same compact scenario-comparison output.
    4. Shows where the scenario-comparison HTML report is saved.
    5. Opens the scenario-comparison HTML report in the default browser.

The actual paid-simulator logic remains in:

    app/paid_simulator
"""

from __future__ import annotations

import subprocess
import sys
import webbrowser
from pathlib import Path


def get_project_root() -> Path:
    """
    Return the Covered Call Simulator project root.
    """
    return Path(__file__).resolve().parents[1]


def get_paid_simulator_runner_path() -> Path:
    """
    Return the paid simulator runner path.
    """
    return get_project_root() / "app" / "paid_simulator" / "runner.py"


def get_paid_simulator_working_dir() -> Path:
    """
    Return the paid simulator working directory.
    """
    return get_project_root() / "app" / "paid_simulator"


def get_scenario_comparison_report_path() -> Path:
    """
    Return the expected scenario-comparison HTML report path.
    """
    return (
        get_project_root()
        / "outputs"
        / "reports"
        / "paid_simulator"
        / "scenario_comparison_report.html"
    )


def open_report_in_browser(report_path: Path) -> None:
    """
    Open the generated HTML report in the default browser.
    """
    if not report_path.exists():
        print()
        print("Report was not opened because it was not found:")
        print(report_path)
        return

    print()
    print("Opening scenario comparison report in browser:")
    print(report_path)

    webbrowser.open(report_path.as_uri())


def run_paid_simulator(open_report: bool = True) -> None:
    """
    Run the paid simulator scenario-comparison workflow.
    """
    runner_path = get_paid_simulator_runner_path()
    working_dir = get_paid_simulator_working_dir()

    if not runner_path.exists():
        raise FileNotFoundError(f"Paid simulator runner not found: {runner_path}")

    print("=" * 79)
    print("Running paid simulator scenario comparison")
    print("=" * 79)
    print(f"Runner: {runner_path}")
    print(f"Working directory: {working_dir}")
    print()

    subprocess.run(
        [sys.executable, str(runner_path)],
        cwd=str(working_dir),
        check=True,
    )

    report_path = get_scenario_comparison_report_path()

    print()
    print("=" * 79)
    print("Paid simulator launcher complete")
    print("=" * 79)

    if report_path.exists():
        print("Scenario comparison report:")
        print(report_path)
    else:
        print("Scenario comparison report was not found at the expected path:")
        print(report_path)

    if open_report:
        open_report_in_browser(report_path)


if __name__ == "__main__":
    run_paid_simulator(open_report=True)
