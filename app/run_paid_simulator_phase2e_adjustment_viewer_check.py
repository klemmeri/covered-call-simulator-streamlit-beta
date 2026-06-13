"""
run_paid_simulator_phase2e_adjustment_viewer_check.py

Checks whether the standalone Phase 2E premium adjustment viewer is installed and
whether the expected Phase 2E adjustment outputs are present.
"""

from pathlib import Path
import csv
import datetime as dt
import sys


APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"

VIEWER_APP = APP_DIR / "paid_simulator" / "phase2e_adjustment_viewer.py"
VIEWER_LAUNCHER = APP_DIR / "run_paid_simulator_phase2e_adjustment_viewer.py"
CHECK_SCRIPT = APP_DIR / "run_paid_simulator_phase2e_adjustment_viewer_check.py"
DOC_FILE = DOCS_DIR / "paid_simulator_phase2e_adjustment_viewer.md"
CHECK_REPORT = REPORT_DIR / "phase2e_adjustment_viewer_check_report.txt"

REQUIRED_FILES = [
    ("Phase 2E viewer app", VIEWER_APP),
    ("Phase 2E viewer launcher", VIEWER_LAUNCHER),
    ("Phase 2E viewer check", CHECK_SCRIPT),
    ("Phase 2E viewer documentation", DOC_FILE),
]

EXPECTED_OUTPUTS = [
    ("Adjusted premiums CSV", TABLE_DIR / "premium_model_adjusted_premiums.csv"),
    ("Adjusted premium comparison HTML", REPORT_DIR / "premium_model_adjustment_comparison.html"),
    ("Adjusted premium summary", REPORT_DIR / "premium_model_adjustment_summary.txt"),
    ("Adjusted payoff comparison CSV", TABLE_DIR / "adjusted_premium_payoff_comparison.csv"),
    ("Adjusted payoff comparison HTML", REPORT_DIR / "adjusted_premium_payoff_comparison.html"),
    ("Adjusted payoff summary", REPORT_DIR / "adjusted_premium_payoff_summary.txt"),
]

VIEWER_MARKERS = [
    "Phase 2E premium adjustment viewer",
    "Adjusted premiums",
    "Adjusted payoff comparison",
    "premium_model_adjusted_premiums.csv",
    "adjusted_premium_payoff_comparison.csv",
]


def print_section(title: str) -> None:
    print()
    print(title)
    print("-" * 96)


def check_file(label: str, path: Path, report_lines: list[str]) -> bool:
    ok = path.exists()
    status = "FOUND" if ok else "MISSING"
    line = f"{status:<10} {label:<45} {path}"
    print(line)
    report_lines.append(line)
    return ok


def csv_row_count(path: Path) -> int:
    if not path.exists():
        return -1
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
        return max(len(rows) - 1, 0)
    except Exception:
        return -1


def check_csv_rows(label: str, path: Path, report_lines: list[str]) -> bool:
    rows = csv_row_count(path)
    ok = rows > 0
    status = "PASS" if ok else "REVIEW"
    row_text = f"rows={rows}" if rows >= 0 else "could not read"
    line = f"{status:<10} {label:<45} {row_text}"
    print(line)
    report_lines.append(line)
    return ok


def check_viewer_markers(report_lines: list[str]) -> bool:
    if not VIEWER_APP.exists():
        line = f"REVIEW     Viewer source markers cannot be checked; file missing: {VIEWER_APP}"
        print(line)
        report_lines.append(line)
        return False

    text = VIEWER_APP.read_text(encoding="utf-8", errors="replace")
    ok_all = True
    for marker in VIEWER_MARKERS:
        ok = marker in text
        status = "PASS" if ok else "REVIEW"
        line = f"{status:<10} Viewer marker {marker!r}"
        print(line)
        report_lines.append(line)
        ok_all = ok_all and ok
    return ok_all


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    report_lines: list[str] = []
    header = "Phase 2E premium adjustment viewer check"
    generated = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("=" * 96)
    print(header)
    print("=" * 96)
    print(f"Generated: {generated}")
    print(f"Project root: {PROJECT_ROOT}")

    report_lines.append(header)
    report_lines.append(f"Generated: {generated}")
    report_lines.append(f"Project root: {PROJECT_ROOT}")
    report_lines.append("")

    print_section("Required viewer files")
    report_lines.append("Required viewer files")
    files_ok = True
    for label, path in REQUIRED_FILES:
        files_ok = check_file(label, path, report_lines) and files_ok

    print_section("Expected Phase 2E outputs")
    report_lines.append("")
    report_lines.append("Expected Phase 2E outputs")
    outputs_ok = True
    for label, path in EXPECTED_OUTPUTS:
        outputs_ok = check_file(label, path, report_lines) and outputs_ok

    print_section("CSV row checks")
    report_lines.append("")
    report_lines.append("CSV row checks")
    rows_ok = True
    rows_ok = check_csv_rows("premium_model_adjusted_premiums.csv", TABLE_DIR / "premium_model_adjusted_premiums.csv", report_lines) and rows_ok
    rows_ok = check_csv_rows("adjusted_premium_payoff_comparison.csv", TABLE_DIR / "adjusted_premium_payoff_comparison.csv", report_lines) and rows_ok

    print_section("Viewer source markers")
    report_lines.append("")
    report_lines.append("Viewer source markers")
    markers_ok = check_viewer_markers(report_lines)

    overall_ok = files_ok and outputs_ok and rows_ok and markers_ok

    print()
    print("=" * 96)
    if overall_ok:
        final = "Overall Phase 2E adjustment-viewer status: PASS"
        print(final)
        print("The Phase 2E adjustment viewer is installed and the expected outputs are present.")
    else:
        final = "Overall Phase 2E adjustment-viewer status: REVIEW"
        print(final)
        print("One or more Phase 2E adjustment-viewer items need attention.")
    print("=" * 96)

    report_lines.append("")
    report_lines.append(final)
    CHECK_REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"\nSaved check report: {CHECK_REPORT}")

    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
