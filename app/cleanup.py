"""
cleanup.py

Output cleanup and archiving utilities for the Covered Call Simulator.

This module keeps the active output folders clean by moving old CSV and PNG
files into a timestamped archive folder before a new simulation run.

It archives both:

1. New organized output folders:
       outputs/tables/path_level
       outputs/tables/cycle_level
       outputs/tables/comparison
       outputs/charts/path_level
       outputs/charts/cycle_level
       outputs/charts/comparison

2. Old loose files from earlier versions:
       outputs/tables/*.csv
       outputs/charts/*.png

It does not delete prior results.
"""

from datetime import datetime
from pathlib import Path
import shutil


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

TABLES_DIR = OUTPUTS_DIR / "tables"
CHARTS_DIR = OUTPUTS_DIR / "charts"
ARCHIVE_DIR = OUTPUTS_DIR / "archive"

TABLES_PATH_LEVEL_DIR = TABLES_DIR / "path_level"
TABLES_CYCLE_LEVEL_DIR = TABLES_DIR / "cycle_level"
TABLES_COMPARISON_DIR = TABLES_DIR / "comparison"

CHARTS_PATH_LEVEL_DIR = CHARTS_DIR / "path_level"
CHARTS_CYCLE_LEVEL_DIR = CHARTS_DIR / "cycle_level"
CHARTS_COMPARISON_DIR = CHARTS_DIR / "comparison"


def ensure_output_folders() -> None:
    """
    Ensure that all expected output folders exist.
    """

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    TABLES_PATH_LEVEL_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_CYCLE_LEVEL_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_COMPARISON_DIR.mkdir(parents=True, exist_ok=True)

    CHARTS_PATH_LEVEL_DIR.mkdir(parents=True, exist_ok=True)
    CHARTS_CYCLE_LEVEL_DIR.mkdir(parents=True, exist_ok=True)
    CHARTS_COMPARISON_DIR.mkdir(parents=True, exist_ok=True)

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)


def archive_existing_outputs() -> None:
    """
    Move existing output files into a timestamped archive folder.

    Files archived:
        outputs/tables/*.csv
        outputs/tables/path_level/*.csv
        outputs/tables/cycle_level/*.csv
        outputs/tables/comparison/*.csv

        outputs/charts/*.png
        outputs/charts/path_level/*.png
        outputs/charts/cycle_level/*.png
        outputs/charts/comparison/*.png

    The archive preserves relative folder structure under outputs.
    """

    ensure_output_folders()

    output_folders = [
        TABLES_DIR,
        TABLES_PATH_LEVEL_DIR,
        TABLES_CYCLE_LEVEL_DIR,
        TABLES_COMPARISON_DIR,
        CHARTS_DIR,
        CHARTS_PATH_LEVEL_DIR,
        CHARTS_CYCLE_LEVEL_DIR,
        CHARTS_COMPARISON_DIR,
    ]

    files_to_archive = []

    for folder in output_folders:
        for file_path in folder.iterdir():
            if not file_path.is_file():
                continue

            if file_path.suffix.lower() in {".csv", ".png"}:
                files_to_archive.append(file_path)

    if not files_to_archive:
        print()
        print("=" * 80)
        print("No existing output files to archive.")
        print("=" * 80)
        print()
        return

    timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    run_archive_dir = ARCHIVE_DIR / f"run_{timestamp}"

    moved_count = 0

    for file_path in files_to_archive:
        relative_path = file_path.relative_to(OUTPUTS_DIR)
        destination = run_archive_dir / relative_path

        destination.parent.mkdir(parents=True, exist_ok=True)

        shutil.move(str(file_path), str(destination))
        moved_count += 1

    print()
    print("=" * 80)
    print("Archived previous output files.")
    print(f"Files archived: {moved_count}")
    print(f"Archive folder: {run_archive_dir}")
    print("=" * 80)
    print()