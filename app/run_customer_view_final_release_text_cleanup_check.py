"""
run_customer_view_final_release_text_cleanup_check.py

Checks that local/pre-release wording has been removed from the dashboard source.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CHECK_REPORT = OUTPUT_REPORT_DIR / "customer_view_final_release_text_cleanup_check_report.txt"
CHECK_JSON = OUTPUT_REPORT_DIR / "customer_view_final_release_text_cleanup_check_report.json"

PATCH_MARKER = "CUSTOMER_VIEW_FINAL_RELEASE_TEXT_CLEANUP_APPLIED"
FORBIDDEN = [
    "Local prototype / pre-release dashboard",
    "2026-06-11 local checkpoint",
    "local checkpoint",
]
REQUIRED = [
    "Covered Call Strategy Stress Test",
    "Beta release",
    "Synthetic scenarios",
    "Imported historical data",
    "Historical data is scenario input, not forecast",
]


class Recorder:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(self, passed: bool, label: str, detail: Any = "") -> None:
        status = "PASS" if passed else "FAIL"
        detail_text = "" if detail is None else str(detail)
        self.rows.append({"status": status, "label": label, "detail": detail_text})
        print(f"{status:<10} {label:<76} {detail_text}")

    @property
    def passed(self) -> bool:
        return all(row["status"] == "PASS" for row in self.rows)


def main() -> int:
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 100)
    print("Customer-view final release text cleanup check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)

    text = ""
    if DASHBOARD_FILE.exists():
        text = DASHBOARD_FILE.read_text(encoding="utf-8")
        try:
            ast.parse(text, filename=str(DASHBOARD_FILE))
            rec.add(True, "Dashboard syntax remains valid", "syntax valid")
        except Exception as exc:
            rec.add(False, "Dashboard syntax remains valid", exc)

    rec.add(PATCH_MARKER in text, "Cleanup patch marker is present", "present" if PATCH_MARKER in text else None)

    for phrase in FORBIDDEN:
        rec.add(phrase not in text, f"Forbidden local/pre-release text removed: {phrase}", "removed" if phrase not in text else "still present")

    for phrase in REQUIRED:
        rec.add(phrase in text, f"Required customer-safe text present: {phrase}", "present" if phrase in text else None)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall customer-view final release text cleanup status: {final_status}")
    print("=" * 100)

    CHECK_REPORT.write_text(
        "\n".join([f"{r['status']:<10} {r['label']:<76} {r['detail']}" for r in rec.rows] + ["", f"Overall customer-view final release text cleanup status: {final_status}"]) + "\n",
        encoding="utf-8",
    )
    CHECK_JSON.write_text(json.dumps({"overall_status": final_status, "checks": rec.rows}, indent=2), encoding="utf-8")
    print(f"Saved check report: {CHECK_REPORT}")
    print(f"Saved check JSON:   {CHECK_JSON}")

    return 0 if rec.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
