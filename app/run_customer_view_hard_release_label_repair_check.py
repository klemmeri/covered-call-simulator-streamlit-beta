"""
run_customer_view_hard_release_label_repair_check.py

Check that local/pre-release dashboard labels have been removed from the source
and replaced by customer-safe beta wording.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CHECK_TXT = REPORT_DIR / "customer_view_hard_release_label_repair_check_report.txt"
CHECK_JSON = REPORT_DIR / "customer_view_hard_release_label_repair_check_report.json"

BAD_PHRASES = [
    "Local prototype / pre-release dashboard",
    "2026-06-11 local checkpoint",
    "local checkpoint",
]
BETA_WORDING = "Beta release"
PATCH_MARKER = "CUSTOMER_VIEW_HARD_RELEASE_LABEL_REPAIR_APPLIED"


class Recorder:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(self, passed: bool, label: str, detail: Any = "") -> None:
        status = "PASS" if passed else "FAIL"
        detail_text = "" if detail is None else str(detail)
        self.rows.append({"status": status, "label": label, "detail": detail_text})
        print(f"{status:<10} {label:<72} {detail_text}")

    @property
    def passed(self) -> bool:
        return all(row["status"] == "PASS" for row in self.rows)


def compile_ok(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        return True, "syntax valid"
    except Exception as exc:
        return False, str(exc)


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 100)
    print("Customer-view hard release-label repair check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)

    text = DASHBOARD_FILE.read_text(encoding="utf-8") if DASHBOARD_FILE.exists() else ""
    ok, detail = compile_ok(DASHBOARD_FILE) if DASHBOARD_FILE.exists() else (False, "missing")
    rec.add(ok, "Dashboard syntax remains valid", detail)
    rec.add(PATCH_MARKER in text, "Hard repair patch marker is present", "present" if PATCH_MARKER in text else None)
    rec.add(BETA_WORDING in text, "Beta release wording is present", "present" if BETA_WORDING in text else None)

    for phrase in BAD_PHRASES:
        rec.add(phrase not in text, f"Removed phrase: {phrase}", "removed" if phrase not in text else "still present")

    # Preserve main dashboard identity and core customer wording.
    rec.add("Covered Call Strategy Stress Test" in text, "Main product title preserved", "present" if "Covered Call Strategy Stress Test" in text else None)
    rec.add("decision-support tool" in text, "Decision-support wording preserved", "present" if "decision-support tool" in text else None)
    rec.add("not a trade recommendation engine" in text, "No-trade-recommendation wording preserved", "present" if "not a trade recommendation engine" in text else None)

    print()
    print("=" * 100)
    status = "PASS" if rec.passed else "FAIL"
    print(f"Overall customer-view hard release-label repair status: {status}")
    print("=" * 100)

    CHECK_TXT.write_text(
        "\n".join([f"{row['status']:<10} {row['label']:<72} {row['detail']}" for row in rec.rows] + ["", f"Overall customer-view hard release-label repair status: {status}"]) + "\n",
        encoding="utf-8",
    )
    CHECK_JSON.write_text(json.dumps({"overall_status": status, "checks": rec.rows}, indent=2), encoding="utf-8")
    print(f"Saved check report: {CHECK_TXT}")
    print(f"Saved check JSON:   {CHECK_JSON}")

    return 0 if rec.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
