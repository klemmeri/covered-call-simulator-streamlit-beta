"""
Check the Phase 3B scenario-overlay viewer installation.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

REQUIRED_FILES = [
    ("Phase 3B viewer app", APP_DIR / "paid_simulator" / "phase3_scenario_overlay_viewer.py"),
    ("Phase 3B viewer launcher", APP_DIR / "run_paid_simulator_phase3_scenario_overlay_viewer.py"),
    ("Phase 3B viewer check", APP_DIR / "run_paid_simulator_phase3_scenario_overlay_viewer_check.py"),
    ("Phase 3B viewer documentation", PROJECT_ROOT / "docs" / "paid_simulator_phase3_scenario_overlay_viewer.md"),
]

CONTEXT_FILES = [
    ("Scenario overlay CSV", OUTPUT_TABLE_DIR / "phase3_scenario_overlay.csv"),
    ("Scenario overlay HTML", OUTPUT_REPORT_DIR / "phase3_scenario_overlay.html"),
    ("Scenario overlay summary", OUTPUT_REPORT_DIR / "phase3_scenario_overlay_summary.txt"),
    ("Interactive payoff snapshot CSV optional", OUTPUT_TABLE_DIR / "phase3_interactive_payoff_snapshot.csv"),
]

SOURCE_MARKERS = [
    "Phase 3B scenario-overlay viewer",
    "Scenario overlay",
    "Payoff context",
    "phase3_scenario_overlay.csv",
    "phase3_interactive_payoff_snapshot.csv",
]


def print_header(title: str) -> None:
    print("=" * 96)
    print(title)
    print("=" * 96)


def print_section(title: str) -> None:
    print("\n" + title)
    print("-" * 96)


def count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        with path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            rows = list(reader)
        return max(len(rows) - 1, 0)
    except Exception:
        return 0


def report_file(label: str, path: Path, required: bool = True) -> bool:
    exists = path.exists()
    if exists:
        status = "FOUND"
    elif required:
        status = "MISSING"
    else:
        status = "OPTIONAL"
    print(f"{status:<10} {label:<45} {path}")
    return exists or not required


def main() -> int:
    print_header("Phase 3B scenario-overlay viewer check")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project root: {PROJECT_ROOT}")

    failures = 0

    print_section("Required viewer files")
    for label, path in REQUIRED_FILES:
        if not report_file(label, path, required=True):
            failures += 1

    print_section("Phase 3B context outputs")
    for label, path in CONTEXT_FILES:
        required = "optional" not in label.lower()
        if not report_file(label, path, required=required):
            failures += 1

    print_section("CSV row checks")
    overlay_csv = OUTPUT_TABLE_DIR / "phase3_scenario_overlay.csv"
    if overlay_csv.exists():
        row_count = count_csv_rows(overlay_csv)
        if row_count > 0:
            print(f"PASS       phase3_scenario_overlay.csv                 rows={row_count}")
        else:
            print("REVIEW     phase3_scenario_overlay.csv                 rows=0")
            failures += 1
    else:
        print("MISSING    phase3_scenario_overlay.csv")
        failures += 1

    print_section("Viewer source markers")
    viewer_path = APP_DIR / "paid_simulator" / "phase3_scenario_overlay_viewer.py"
    viewer_text = viewer_path.read_text(encoding="utf-8") if viewer_path.exists() else ""
    for marker in SOURCE_MARKERS:
        if marker in viewer_text:
            print(f"PASS       Viewer marker '{marker}'")
        else:
            print(f"REVIEW     Viewer marker '{marker}'")
            failures += 1

    report_path = OUTPUT_REPORT_DIR / "phase3_scenario_overlay_viewer_check_report.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    status = "PASS" if failures == 0 else "REVIEW"
    report_path.write_text(
        "Phase 3B scenario-overlay viewer check\n"
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Status: {status}\n"
        f"Failures/review items: {failures}\n",
        encoding="utf-8",
    )

    print("\n" + "=" * 96)
    print(f"Overall Phase 3B scenario-overlay viewer status: {status}")
    if failures == 0:
        print("The Phase 3B scenario-overlay viewer is installed and ready.")
    else:
        print("One or more Phase 3B scenario-overlay viewer items need attention.")
    print("=" * 96)
    print(f"\nSaved check report: {report_path}")

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
