"""
run_customer_view_final_release_text_cleanup.py

Final customer-view release text cleanup.

This script removes local/pre-release/debug wording from the Streamlit dashboard
source and replaces it with customer-safe beta wording. It does not change the
simulator engine or calculations.
"""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"

PATCH_MARKER = "CUSTOMER_VIEW_FINAL_RELEASE_TEXT_CLEANUP_APPLIED"

REPLACEMENTS = [
    ("Paid Simulator Dashboard v0.1 | Local prototype / pre-release dashboard | 2026-06-11 local checkpoint", "Paid Simulator Dashboard v0.1 | Beta release"),
    ("Local prototype / pre-release dashboard | 2026-06-11 local checkpoint", "Beta release"),
    ("Local prototype / pre-release dashboard", "Beta release"),
    ("2026-06-11 local checkpoint", ""),
    ("local checkpoint", ""),
]


def main() -> int:
    print("=" * 100)
    print("Customer-view final release text cleanup")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Dashboard file: {DASHBOARD_FILE}")
    print()

    if not DASHBOARD_FILE.exists():
        print("FAIL: dashboard file not found")
        return 1

    text = DASHBOARD_FILE.read_text(encoding="utf-8")
    original = text

    for old, new in REPLACEMENTS:
        text = text.replace(old, new)

    # Normalize possible double separators produced by replacement.
    text = text.replace(" |  | ", " | ")
    text = text.replace(" | )", ")")
    text = text.replace("|  ", "| ")
    text = text.replace("  |", " |")

    if PATCH_MARKER not in text:
        text = text.rstrip() + f"\n\n# {PATCH_MARKER}\n"

    DASHBOARD_FILE.write_text(text, encoding="utf-8")

    if text == original:
        print("No text replacements were needed; marker added if absent.")
    else:
        print("Dashboard release text cleanup applied.")

    print("PASS: cleanup script completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
