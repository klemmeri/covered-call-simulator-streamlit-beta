"""
run_paid_simulator_phase2c_premium_validation_viewer_check.py

Readiness check for the standalone Phase 2C Premium Validation Viewer.
"""

from __future__ import annotations

import csv
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

EXPECTED_FILES = [
    ("Viewer app", APP_DIR / "paid_simulator" / "phase2c_premium_validation_viewer.py"),
    ("Viewer launcher", APP_DIR / "run_paid_simulator_phase2c_premium_validation_viewer.py"),
    ("Viewer check", APP_DIR / "run_paid_simulator_phase2c_premium_validation_viewer_check.py"),
    ("Viewer documentation", PROJECT_ROOT / "docs" / "paid_simulator_phase2c_premium_validation_viewer.md"),
]

EXPECTED_OUTPUTS = [
    ("Validation CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_model_validation_scaffold.csv"),
    ("Validation HTML", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_model_validation_scaffold.html"),
    ("Validation summary", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_model_validation_summary.txt"),
    ("Option premium CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "option_premium_scaffold.csv"),
    ("Premium-aware payoff CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_aware_payoff_scaffold.csv"),
]


def count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            rows = list(reader)
        return max(len(rows) - 1, 0)
    except UnicodeDecodeError:
        with path.open("r", errors="ignore", newline="") as handle:
            reader = csv.reader(handle)
            rows = list(reader)
        return max(len(rows) - 1, 0)
    except Exception:
        return 0


def print_header(title: str) -> None:
    print("=" * 92)
    print(title)
    print("=" * 92)


def main() -> None:
    print_header("Phase 2C Premium Validation Viewer readiness check")
    print(f"Project root: {PROJECT_ROOT}")
    print()

    overall_pass = True

    print("Expected app files")
    print("-" * 92)
    for label, path in EXPECTED_FILES:
        status = "FOUND" if path.exists() else "MISSING"
        if status == "MISSING":
            overall_pass = False
        print(f"{status:<8} {label:<32} {path}")
    print()

    print("Expected Phase 2C output files")
    print("-" * 92)
    for label, path in EXPECTED_OUTPUTS:
        status = "FOUND" if path.exists() else "MISSING"
        rows_text = ""
        if path.suffix.lower() == ".csv" and path.exists():
            row_count = count_csv_rows(path)
            rows_text = f" rows={row_count}"
            if row_count <= 0:
                status = "EMPTY"
        if status in {"MISSING", "EMPTY"}:
            overall_pass = False
        print(f"{status:<8} {label:<32} {path}{rows_text}")
    print()

    if overall_pass:
        print("PASS: Phase 2C premium-validation viewer is ready to run.")
        print()
        print("To open it, run:")
        print(r"  app\run_paid_simulator_phase2c_premium_validation_viewer.py")
    else:
        print("REVIEW: One or more files or outputs are missing.")
        print()
        print("Recommended fix:")
        print(r"  1. Run app\run_paid_simulator_premium_model_validation_check.py")
        print(r"  2. Re-run this viewer readiness check")

    print()
    print(f"Overall Phase 2C premium-validation viewer status: {'PASS' if overall_pass else 'REVIEW'}")


if __name__ == "__main__":
    main()
