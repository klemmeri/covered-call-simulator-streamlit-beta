"""
Check that the Developer-view-only Phase 2 scaffold tab was installed in the dashboard.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_APP = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
DOC_PATH = PROJECT_ROOT / "docs" / "paid_simulator_phase2_dashboard_tab.md"


def main() -> None:
    print("=" * 88)
    print("Phase 2 dashboard-tab install check")
    print("=" * 88)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    ok = True

    for label, path in [
        ("Dashboard app", DASHBOARD_APP),
        ("Phase 2 dashboard-tab doc", DOC_PATH),
    ]:
        exists = path.exists()
        print(f"{'FOUND' if exists else 'MISSING':<10} {label:<35} {path}")
        ok = ok and exists

    if DASHBOARD_APP.exists():
        text = DASHBOARD_APP.read_text(encoding="utf-8")
        required_tokens = [
            "Phase 2 scaffold",
            "show_phase2_scaffold_tab",
            "PHASE2_V0_COMPARISON_PATH",
            "Run Phase 2 pipeline check",
            "Run integration-readiness check",
        ]
        print()
        print("Dashboard code markers")
        print("-" * 88)
        for token in required_tokens:
            found = token in text
            print(f"{'FOUND' if found else 'MISSING':<10} {token}")
            ok = ok and found

    print()
    print("=" * 88)
    if ok:
        print("Overall Phase 2 dashboard-tab status: PASS")
        print("The Developer-view-only Phase 2 scaffold tab is installed.")
    else:
        print("Overall Phase 2 dashboard-tab status: REVIEW")
        print("One or more dashboard-tab files or markers are missing.")
    print("=" * 88)
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
