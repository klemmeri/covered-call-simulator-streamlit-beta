"""
Check that the Phase 2 Scaffold Viewer includes the scenario-assumptions view.
"""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VIEWER_PATH = PROJECT_ROOT / "app" / "paid_simulator" / "phase2_scaffold_viewer.py"
ASSUMPTIONS_CSV = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_assumptions_scaffold.csv"
LAUNCHER_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase2_viewer.py"


def main() -> None:
    print("=" * 88)
    print("Phase 2 assumptions viewer-tab check")
    print("=" * 88)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    problems: list[str] = []

    checks = [
        ("Phase 2 viewer app", VIEWER_PATH),
        ("Phase 2 viewer launcher", LAUNCHER_PATH),
        ("Scenario assumptions CSV", ASSUMPTIONS_CSV),
    ]

    for label, path in checks:
        status = "FOUND" if path.exists() else "MISSING"
        print(f"{status:<10} {label:<35} {path}")
        if not path.exists():
            problems.append(f"Missing {label}: {path}")

    print()
    print("Viewer source checks")
    print("-" * 88)
    if VIEWER_PATH.exists():
        text = VIEWER_PATH.read_text(encoding="utf-8")
        required_tokens = [
            "Scenario assumptions",
            "SCENARIO_ASSUMPTIONS_PATH",
            "show_assumptions_tab",
        ]
        for token in required_tokens:
            if token in text:
                print(f"PASS       viewer contains token: {token}")
            else:
                print(f"MISSING    viewer token: {token}")
                problems.append(f"Viewer source missing token: {token}")

    print()
    print("=" * 88)
    if problems:
        print("Overall Phase 2 assumptions-viewer status: REVIEW")
        print("Items needing attention:")
        for problem in problems:
            print(f"- {problem}")
        print("=" * 88)
        sys.exit(1)

    print("Overall Phase 2 assumptions-viewer status: PASS")
    print("The standalone Phase 2 viewer includes the Scenario assumptions tab.")
    print("=" * 88)


if __name__ == "__main__":
    main()
