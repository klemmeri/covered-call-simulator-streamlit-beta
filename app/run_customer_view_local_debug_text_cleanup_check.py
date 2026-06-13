"""
run_customer_view_local_debug_text_cleanup_check.py

Checks that the customer-view local debug text cleanup patch is present and
that the dashboard remains syntactically valid.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

CHECK_REPORT = OUTPUT_REPORT_DIR / "customer_view_local_debug_text_cleanup_check_report.txt"
CHECK_JSON = OUTPUT_REPORT_DIR / "customer_view_local_debug_text_cleanup_check_report.json"

PATCH_MARKER = "CUSTOMER_VIEW_LOCAL_DEBUG_TEXT_CLEANUP_APPLIED"
START_MARKER = "# === CUSTOMER VIEW LOCAL DEBUG TEXT CLEANUP START ==="
END_MARKER = "# === CUSTOMER VIEW LOCAL DEBUG TEXT CLEANUP END ==="


class Recorder:
    def __init__(self) -> None:
        self.rows: list[dict] = []

    def add(self, passed: bool, label: str, detail: object = "") -> None:
        status = "PASS" if passed else "FAIL"
        detail_text = "" if detail is None else str(detail)
        self.rows.append({"status": status, "label": label, "detail": detail_text})
        print(f"{status:<10} {label:<74} {detail_text}")

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
    print("=" * 100)
    print("Customer-view local debug text cleanup check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)

    ok, detail = compile_ok(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    text = DASHBOARD_FILE.read_text(encoding="utf-8") if DASHBOARD_FILE.exists() else ""
    rec.add(PATCH_MARKER in text, "Cleanup patch marker is present", PATCH_MARKER if PATCH_MARKER in text else None)
    rec.add(START_MARKER in text and END_MARKER in text, "Cleanup patch block is bounded", "present" if START_MARKER in text and END_MARKER in text else None)
    rec.add("Developer view" in text, "Developer-view guard exists", "present" if "Developer view" in text else None)
    rec.add("Project root:" in text, "Project-root text is preserved for Developer view", "present" if "Project root:" in text else None)
    rec.add("Local prototype" in text or "local checkpoint" in text or "pre-release dashboard" in text, "Local prototype/checkpoint text is preserved for Developer view", "present" if ("Local prototype" in text or "local checkpoint" in text or "pre-release dashboard" in text) else None)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall customer-view cleanup check status: {final_status}")
    print("=" * 100)

    CHECK_REPORT.write_text(
        "\n".join([f"{r['status']:<10} {r['label']:<74} {r['detail']}" for r in rec.rows] + ["", f"Overall customer-view cleanup check status: {final_status}"]) + "\n",
        encoding="utf-8",
    )
    CHECK_JSON.write_text(json.dumps({"overall_status": final_status, "checks": rec.rows}, indent=2), encoding="utf-8")

    print(f"Saved check report: {CHECK_REPORT}")
    print(f"Saved check JSON:   {CHECK_JSON}")

    return 0 if rec.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
