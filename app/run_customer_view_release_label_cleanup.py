"""
run_customer_view_release_label_cleanup.py

Customer-view release-label cleanup for the Covered Call Simulator dashboard.

This patch removes local prototype / local checkpoint wording from the dashboard
source and replaces it with beta-release wording suitable for a customer-facing
local or hosted preview.

It does not change the simulator engine or option calculations.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
BACKUP_DIR = PROJECT_ROOT / "outputs" / "archive" / "customer_view_release_label_cleanup"

REPLACEMENTS = [
    (
        "Local prototype / pre-release dashboard | 2026-06-11 local checkpoint",
        "Beta release",
    ),
    (
        "Local prototype / pre-release dashboard",
        "Beta release",
    ),
    (
        "2026-06-11 local checkpoint",
        "Beta release",
    ),
    (
        "local checkpoint",
        "beta release",
    ),
]

PATCH_MARKER = "PHASE_POST10_CUSTOMER_VIEW_RELEASE_LABEL_CLEANUP_APPLIED"
PATCH_COMMENT = f"\n# {PATCH_MARKER}: local prototype/checkpoint wording replaced with beta-release wording.\n"


def main() -> int:
    print("=" * 100)
    print("Customer-view release-label cleanup")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Dashboard file: {DASHBOARD_FILE}")
    print()

    if not DASHBOARD_FILE.exists():
        print("FAIL: Dashboard file does not exist.")
        return 1

    original = DASHBOARD_FILE.read_text(encoding="utf-8")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"config_form_app_before_release_label_cleanup_{timestamp}.py"
    shutil.copy2(DASHBOARD_FILE, backup_path)

    updated = original
    replacements_applied = 0
    for old, new in REPLACEMENTS:
        count = updated.count(old)
        if count:
            updated = updated.replace(old, new)
            replacements_applied += count

    if PATCH_MARKER not in updated:
        updated = updated.rstrip() + PATCH_COMMENT

    DASHBOARD_FILE.write_text(updated, encoding="utf-8")

    print(f"Backup saved: {backup_path}")
    print(f"Replacements applied: {replacements_applied}")
    print(f"Patch marker: {PATCH_MARKER}")
    print()
    print("PASS: Customer-view release-label cleanup applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
