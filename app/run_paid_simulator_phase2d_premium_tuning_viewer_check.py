"""
run_paid_simulator_phase2d_premium_tuning_viewer_check.py

Check that the standalone Phase 2D premium-model tuning viewer is installed
and that the tuning outputs it reads are present.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parent.parent
APP_DIR = PROJECT_ROOT / "app"
PAID_DIR = APP_DIR / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"
CONFIG_DIR = PROJECT_ROOT / "config"

REQUIRED_FILES = [
    ("Phase 2D tuning viewer app", PAID_DIR / "phase2d_premium_tuning_viewer.py"),
    ("Phase 2D tuning viewer launcher", APP_DIR / "run_paid_simulator_phase2d_premium_tuning_viewer.py"),
    ("Phase 2D tuning viewer check", APP_DIR / "run_paid_simulator_phase2d_premium_tuning_viewer_check.py"),
    ("Phase 2D tuning recommendations CSV", TABLE_DIR / "premium_model_tuning_recommendations.csv"),
    ("Phase 2D tuning recommendations HTML", REPORT_DIR / "premium_model_tuning_recommendations.html"),
    ("Phase 2D tuning summary", REPORT_DIR / "premium_model_tuning_summary.txt"),
    ("Phase 2D tuning check report", REPORT_DIR / "phase2d_premium_model_tuning_check_report.txt"),
    ("Phase 2D tuning config", CONFIG_DIR / "premium_model_tuning_config.json"),
    ("Phase 2D tuning viewer documentation", DOCS_DIR / "paid_simulator_phase2d_premium_tuning_viewer.md"),
]

SUPPORTING_OUTPUTS = [
    ("Option premium CSV", TABLE_DIR / "option_premium_scaffold.csv"),
    ("Premium-aware payoff CSV", TABLE_DIR / "premium_aware_payoff_scaffold.csv"),
    ("Premium validation CSV", TABLE_DIR / "premium_model_validation_scaffold.csv"),
]


def count_csv_rows(path: Path) -> int:
    if not path.exists():
        return -1
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            rows = list(reader)
        return max(len(rows) - 1, 0)
    except Exception:
        return -1


def print_section(title: str) -> None:
    print("\n" + title)
    print("-" * 96)


def main() -> int:
    print("=" * 96)
    print("Phase 2D premium-model tuning viewer check")
    print("=" * 96)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project root: {PROJECT_ROOT}")

    failures = 0

    print_section("Required Phase 2D tuning viewer files")
    for label, path in REQUIRED_FILES:
        exists = path.exists()
        print(f"{'FOUND' if exists else 'MISSING':<10} {label:<48} {path}")
        if not exists:
            failures += 1

    print_section("Supporting Phase 2B/2C outputs")
    for label, path in SUPPORTING_OUTPUTS:
        exists = path.exists()
        print(f"{'FOUND' if exists else 'MISSING':<10} {label:<48} {path}")
        if not exists:
            failures += 1

    print_section("CSV row checks")
    csv_files = [
        TABLE_DIR / "premium_model_tuning_recommendations.csv",
        TABLE_DIR / "option_premium_scaffold.csv",
        TABLE_DIR / "premium_aware_payoff_scaffold.csv",
        TABLE_DIR / "premium_model_validation_scaffold.csv",
    ]
    for csv_path in csv_files:
        row_count = count_csv_rows(csv_path)
        if row_count > 0:
            print(f"PASS       {csv_path.name:<48} rows={row_count}")
        else:
            print(f"REVIEW     {csv_path.name:<48} rows={row_count}")
            failures += 1

    print_section("Viewer source markers")
    viewer_path = PAID_DIR / "phase2d_premium_tuning_viewer.py"
    if viewer_path.exists():
        text = viewer_path.read_text(encoding="utf-8", errors="replace")
        markers = [
            "Phase 2D Premium-Model Tuning Viewer",
            "premium_model_tuning_recommendations.csv",
            "premium_model_tuning_summary.txt",
            "Tuning recommendations",
        ]
        for marker in markers:
            ok = marker in text
            print(f"{'PASS' if ok else 'REVIEW':<10} Viewer marker '{marker}'")
            if not ok:
                failures += 1

    print("\n" + "=" * 96)
    if failures == 0:
        print("Overall Phase 2D premium-tuning viewer status: PASS")
        print("The standalone Phase 2D tuning viewer is installed and ready to open.")
        print("=" * 96)
        return 0

    print("Overall Phase 2D premium-tuning viewer status: REVIEW")
    print("One or more Phase 2D tuning-viewer items need attention.")
    print("=" * 96)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
