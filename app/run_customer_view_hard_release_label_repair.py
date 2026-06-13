"""
run_customer_view_hard_release_label_repair.py

Hard repair for customer-facing release-label text in the Streamlit dashboard.

This script removes remaining local/pre-release wording from config_form_app.py
and replaces it with customer-safe beta wording. It also records a report.
"""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
REPORT_TXT = REPORT_DIR / "customer_view_hard_release_label_repair_report.txt"
REPORT_JSON = REPORT_DIR / "customer_view_hard_release_label_repair_report.json"

BAD_PHRASES = [
    "Local prototype / pre-release dashboard | 2026-06-11 local checkpoint",
    "Local prototype / pre-release dashboard",
    "2026-06-11 local checkpoint",
    "local checkpoint",
]

BETA_WORDING = "Beta release"
PATCH_MARKER = "CUSTOMER_VIEW_HARD_RELEASE_LABEL_REPAIR_APPLIED"


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    if not DASHBOARD_FILE.exists():
        raise FileNotFoundError(f"Dashboard file not found: {DASHBOARD_FILE}")

    original = DASHBOARD_FILE.read_text(encoding="utf-8")
    text = original

    replacements = {}
    for phrase in BAD_PHRASES:
        count = text.count(phrase)
        replacements[phrase] = count
        if count:
            text = text.replace(phrase, BETA_WORDING)

    # Clean repeated beta wording that can occur after phrase overlap replacements.
    while "Beta release | Beta release" in text:
        text = text.replace("Beta release | Beta release", "Beta release")
    while "Beta release Beta release" in text:
        text = text.replace("Beta release Beta release", "Beta release")

    if PATCH_MARKER not in text:
        text += f"\n\n# {PATCH_MARKER}\n"

    DASHBOARD_FILE.write_text(text, encoding="utf-8")

    remaining = {phrase: text.count(phrase) for phrase in BAD_PHRASES}
    summary = {
        "patch_marker": PATCH_MARKER,
        "dashboard_file": str(DASHBOARD_FILE),
        "replacement_counts": replacements,
        "remaining_counts": remaining,
        "beta_wording_present": BETA_WORDING in text,
        "local_wording_removed": all(count == 0 for count in remaining.values()),
    }

    REPORT_TXT.write_text(
        "Customer-view hard release-label repair\n"
        "=======================================\n"
        f"Dashboard file: {DASHBOARD_FILE}\n"
        f"Patch marker: {PATCH_MARKER}\n"
        f"Beta wording present: {summary['beta_wording_present']}\n"
        f"Local wording removed: {summary['local_wording_removed']}\n"
        f"Replacement counts: {replacements}\n"
        f"Remaining counts: {remaining}\n",
        encoding="utf-8",
    )
    REPORT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("Customer-view hard release-label repair complete.")
    print(f"Dashboard file: {DASHBOARD_FILE}")
    print(f"Beta wording present: {summary['beta_wording_present']}")
    print(f"Local wording removed: {summary['local_wording_removed']}")
    print(f"Saved report: {REPORT_TXT}")

    return 0 if summary["local_wording_removed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
