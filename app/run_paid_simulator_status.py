"""
run_paid_simulator_status.py

Standalone status checker for the Covered Call Simulator paid simulator dashboard.
This is a safe add-on script. It does not modify the simulator or config files.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.paid_simulator.dashboard_status import get_dashboard_status, status_table_rows


def print_section(title: str) -> None:
    print("\n" + title)
    print("-" * len(title))


def print_rows(rows: list[dict]) -> None:
    for row in rows:
        print(f"{row['Status']:<8} {row['Item']:<35} {row['Modified']:<20} {row['Path']}")


def main() -> None:
    status = get_dashboard_status(PROJECT_ROOT)

    print("=" * 92)
    print("Paid simulator dashboard status")
    print("=" * 92)
    print(f"Build:        {status.build_name}")
    print(f"Version:      {status.build_version}")
    print(f"Build date:   {status.build_date}")
    print(f"Project root: {status.project_root}")
    print(f"Overall:      {status.overall_status}")

    if status.problems:
        print_section("Problems")
        for problem in status.problems:
            print(f"- {problem}")

    print_section("Config summary")
    if status.config_summary:
        for key, value in status.config_summary.items():
            print(f"{key:<24} {value}")
    else:
        print("No config summary available.")

    print_section("Required files")
    print_rows(status_table_rows(status.required_files))

    print_section("Output files")
    print_rows(status_table_rows(status.output_files))

    print_section("Optional dashboard files")
    print_rows(status_table_rows(status.optional_files))

    print("\nDone.")


if __name__ == "__main__":
    main()
