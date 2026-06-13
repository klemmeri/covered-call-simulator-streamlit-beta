"""
Checks whether the Phase 2B premium-model viewer and its expected inputs exist.
"""

from __future__ import annotations

import sys
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]

EXPECTED_FILES = [
    ("Phase 2B premium viewer app", PROJECT_ROOT / "app" / "paid_simulator" / "phase2b_premium_viewer.py"),
    ("Phase 2B premium viewer launcher", PROJECT_ROOT / "app" / "run_paid_simulator_phase2b_premium_viewer.py"),
    ("Option premium scaffold CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "option_premium_scaffold.csv"),
    ("Premium-aware payoff CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_aware_payoff_scaffold.csv"),
    ("Premium-vs-scaffold comparison CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_vs_scaffold_comparison.csv"),
    ("Premium-aware payoff HTML", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_aware_payoff_scaffold.html"),
    ("Premium-vs-scaffold HTML", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_vs_scaffold_comparison.html"),
    ("Premium viewer doc", PROJECT_ROOT / "docs" / "paid_simulator_phase2b_premium_viewer.md"),
]


def print_header(title: str) -> None:
    print("=" * 88)
    print(title)
    print("=" * 88)


def print_section(title: str) -> None:
    print("\n" + "-" * 88)
    print(title)
    print("-" * 88)


def count_rows(path: Path) -> int | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if not text:
        return 0
    return max(len(text) - 1, 0)


def main() -> None:
    print_header("Phase 2B premium-model viewer check")
    print(f"Project root: {PROJECT_ROOT}")

    ok = True
    print_section("Expected files")
    for label, path in EXPECTED_FILES:
        exists = path.exists()
        status = "FOUND" if exists else "MISSING"
        print(f"{status:<10} {label:<38} {path}")
        if not exists:
            ok = False

    print_section("CSV row counts")
    for label, path in [
        ("option_premium_scaffold.csv", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "option_premium_scaffold.csv"),
        ("premium_aware_payoff_scaffold.csv", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_aware_payoff_scaffold.csv"),
        ("premium_vs_scaffold_comparison.csv", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_vs_scaffold_comparison.csv"),
    ]:
        rows = count_rows(path)
        if rows is None:
            print(f"MISSING    {label}")
            ok = False
        elif rows <= 0:
            print(f"EMPTY      {label}: {rows} rows")
            ok = False
        else:
            print(f"PASS       {label}: {rows} rows")

    print("\n" + "=" * 88)
    if ok:
        print("Overall Phase 2B premium-viewer status: PASS")
        print("Premium-model viewer files and outputs are present.")
    else:
        print("Overall Phase 2B premium-viewer status: REVIEW")
        print("One or more premium-viewer files or outputs need attention.")
    print("=" * 88)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
