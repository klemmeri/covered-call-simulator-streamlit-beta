"""
run_customer_view_release_label_cleanup_check.py

Checks that local prototype/checkpoint wording has been removed from the
customer-facing dashboard source after the release-label cleanup patch.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CHECK_REPORT = OUTPUT_REPORT_DIR / "customer_view_release_label_cleanup_check_report.txt"
CHECK_JSON = OUTPUT_REPORT_DIR / "customer_view_release_label_cleanup_check_report.json"

PATCH_MARKER = "PHASE_POST10_CUSTOMER_VIEW_RELEASE_LABEL_CLEANUP_APPLIED"
FORBIDDEN_CUSTOMER_STRINGS = [
    "Local prototype / pre-release dashboard",
    "2026-06-11 local checkpoint",
    "local checkpoint",
]
REQUIRED_CUSTOMER_STRINGS = [
    "Beta release",
    "Covered Call Strategy Stress Test",
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


def _compile_file(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        return True, "syntax valid"
    except Exception as exc:
        return False, str(exc)


def main() -> int:
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 100)
    print("Customer-view release-label cleanup check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)

    if DASHBOARD_FILE.exists():
        ok, detail = _compile_file(DASHBOARD_FILE)
        rec.add(ok, "Dashboard syntax remains valid", detail)
        text = DASHBOARD_FILE.read_text(encoding="utf-8")
    else:
        text = ""

    rec.add(PATCH_MARKER in text, "Release-label cleanup patch marker is present", "present" if PATCH_MARKER in text else None)

    for forbidden in FORBIDDEN_CUSTOMER_STRINGS:
        rec.add(forbidden not in text, f"Local debug wording removed: {forbidden}", "absent" if forbidden not in text else "still present")

    for required in REQUIRED_CUSTOMER_STRINGS:
        rec.add(required in text, f"Required customer wording present: {required}", "present" if required in text else None)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall customer-view release-label cleanup status: {final_status}")
    print("=" * 100)

    CHECK_REPORT.write_text(
        "\n".join([f"{r['status']:<10} {r['label']:<76} {r['detail']}" for r in rec.rows] + ["", f"Overall customer-view release-label cleanup status: {final_status}"]) + "\n",
        encoding="utf-8",
    )
    CHECK_JSON.write_text(json.dumps({"overall_status": final_status, "checks": rec.rows}, indent=2), encoding="utf-8")

    print(f"Saved check report: {CHECK_REPORT}")
    print(f"Saved check JSON:   {CHECK_JSON}")

    return 0 if rec.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
