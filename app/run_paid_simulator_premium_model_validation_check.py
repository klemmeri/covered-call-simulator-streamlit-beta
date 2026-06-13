"""
run_paid_simulator_premium_model_validation_check.py

PyCharm runner for the Phase 2C premium-model validation scaffold.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CONFIG_PATH = PROJECT_ROOT / "config" / "premium_model_validation_config.json"
VALIDATION_CSV = TABLE_DIR / "premium_model_validation_scaffold.csv"
VALIDATION_HTML = REPORT_DIR / "premium_model_validation_scaffold.html"
VALIDATION_SUMMARY_TXT = REPORT_DIR / "premium_model_validation_summary.txt"


def print_header(title: str) -> None:
    print("=" * 92)
    print(title)
    print("=" * 92)


def print_section(title: str) -> None:
    print()
    print(title)
    print("-" * 92)


def csv_row_count(path: Path) -> int:
    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return sum(1 for _ in reader)


def main() -> None:
    print_header("Phase 2C premium-model validation check")
    print(f"Project root: {PROJECT_ROOT}")

    ok = True

    print_section("Import check")
    try:
        from app.paid_simulator.premium_model_validation import run_premium_model_validation
        print("PASS - premium_model_validation imported")
    except Exception as exc:
        print(f"FAILED - could not import premium-model validation module: {exc}")
        raise SystemExit(1)

    print_section("Run validation")
    try:
        result = run_premium_model_validation()
        print(f"Rows validated: {result.row_count}")
        print(f"PASS rows: {result.pass_count}")
        print(f"WATCH rows: {result.review_count}")
        print(f"REVIEW rows: {result.fail_count}")
        print(f"Overall model-validation status: {result.overall_status}")
    except Exception as exc:
        print(f"FAILED - validation run raised an error: {exc}")
        raise SystemExit(1)

    print_section("Output file check")
    expected_files = [
        ("Validation config", CONFIG_PATH),
        ("Validation CSV", VALIDATION_CSV),
        ("Validation HTML", VALIDATION_HTML),
        ("Validation summary", VALIDATION_SUMMARY_TXT),
    ]
    for label, path in expected_files:
        if path.exists():
            print(f"FOUND  - {label:<22} {path}")
        else:
            print(f"MISSING - {label:<22} {path}")
            ok = False

    print_section("CSV structure check")
    if VALIDATION_CSV.exists():
        with VALIDATION_CSV.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            columns = reader.fieldnames or []
            rows = list(reader)
        print(f"Rows excluding header: {len(rows)}")
        print(f"Columns: {', '.join(columns)}")
        required = [
            "scenario_name",
            "validation_status",
            "estimated_call_premium",
            "premium_percent_of_underlying",
            "implied_volatility",
            "validation_issue",
            "suggested_adjustment",
        ]
        missing = [col for col in required if col not in columns]
        if missing:
            print(f"FAILED - missing required columns: {missing}")
            ok = False
        if len(rows) < 5:
            print("FAILED - expected at least 5 scenario rows")
            ok = False
        statuses = sorted({row.get("validation_status", "") for row in rows})
        print(f"Validation statuses present: {', '.join(statuses)}")
    else:
        print("FAILED - validation CSV is missing")
        ok = False

    print_section("Interpretation")
    if VALIDATION_SUMMARY_TXT.exists():
        print(VALIDATION_SUMMARY_TXT.read_text(encoding="utf-8"))

    print("=" * 92)
    if ok:
        print("Overall Phase 2C premium-model validation status: PASS")
        print("The premium-model validation scaffold is installed and writing its checkpoint files.")
        print("A WATCH or REVIEW inside the validation report is a modeling signal, not an installation failure.")
        print("=" * 92)
        raise SystemExit(0)

    print("Overall Phase 2C premium-model validation status: REVIEW")
    print("One or more installation or output checks need attention.")
    print("=" * 92)
    raise SystemExit(1)


if __name__ == "__main__":
    main()
