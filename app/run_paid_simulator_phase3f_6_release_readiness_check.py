"""
Phase 3F-6 customer-preview release-readiness checkpoint.

Run from PyCharm or terminal:
    python app/run_paid_simulator_phase3f_6_release_readiness_check.py
"""

from __future__ import annotations

import ast
import csv
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)

CHECK_REPORT = REPORT_DIR / "phase3f_6_release_readiness_checkpoint_report.txt"
CHECK_JSON = REPORT_DIR / "phase3f_6_release_readiness_checkpoint.json"
CHECK_CSV = TABLE_DIR / "phase3f_6_release_readiness_checklist.csv"

EXPECTED_FILES = [
    "app/paid_simulator/phase3f_customer_preview_release_readiness.py",
    "app/run_paid_simulator_phase3f_6_release_readiness_check.py",
    "docs/phase3f_6_customer_preview_release_readiness.md",
]


def check_syntax(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:  # pragma: no cover
        return False, repr(exc)


def add(results: list[dict], label: str, passed: bool, detail: str) -> None:
    results.append({"label": label, "passed": bool(passed), "detail": str(detail)})


def main() -> int:
    results: list[dict] = []

    print("=" * 100)
    print("Phase 3F-6 customer-preview release-readiness check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    for rel in EXPECTED_FILES:
        path = PROJECT_ROOT / rel
        add(results, rel, path.exists(), str(path))

    module_path = PROJECT_ROOT / "app" / "paid_simulator" / "phase3f_customer_preview_release_readiness.py"
    ok, detail = check_syntax(module_path)
    add(results, "Release-readiness module syntax valid", ok, detail)

    dashboard_path = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
    ok, detail = check_syntax(dashboard_path)
    add(results, "Dashboard syntax remains valid", ok, detail)

    try:
        from app.paid_simulator.phase3f_customer_preview_release_readiness import (
            PHASE3F_6_RELEASE_READINESS_MARKER,
            build_release_readiness_model,
            render_release_readiness_summary,
        )
        model = build_release_readiness_model(PROJECT_ROOT)
        fallback = render_release_readiness_summary(PROJECT_ROOT, streamlit_module=None)
        add(results, "Release-readiness module imports", True, PHASE3F_6_RELEASE_READINESS_MARKER)
        add(results, "Readiness marker present", model.get("marker") == PHASE3F_6_RELEASE_READINESS_MARKER, model.get("marker"))
        add(results, "Ordinary Customer view remains disabled", model.get("public_customer_enabled") is False, model.get("public_customer_enabled"))
        add(results, "Protected preview remains allowed", model.get("protected_preview_allowed") is True, model.get("protected_preview_allowed"))
        add(results, "Guardrails present", len(model.get("guardrails", [])) >= 4, len(model.get("guardrails", [])))
        add(results, "Customer labels present", len(model.get("customer_labels", [])) >= 6, len(model.get("customer_labels", [])))
        add(results, "Fallback render returns model dict", isinstance(fallback, dict) and fallback.get("marker") == model.get("marker"), type(fallback).__name__)
        missing_modules = [item["path"] for item in model.get("modules", []) if not item.get("exists")]
        missing_reports = [item["path"] for item in model.get("reports", []) if not item.get("exists")]
        add(results, "Core preview modules present", not missing_modules, ", ".join(missing_modules) if missing_modules else "all present")
        add(results, "Prior checkpoint reports present", not missing_reports, ", ".join(missing_reports) if missing_reports else "all present")
    except Exception as exc:
        add(results, "Release-readiness module imports", False, repr(exc))
        model = {}

    dashboard_text = dashboard_path.read_text(encoding="utf-8", errors="replace") if dashboard_path.exists() else ""
    add(results, "Phase 3F-3 route marker still in dashboard", "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY" in dashboard_text, "Phase 3F-3 marker search")
    add(results, "Phase 3E marker still in dashboard", "PHASE3E_7C_DEVELOPER_TAB_READY" in dashboard_text, "Phase 3E marker search")
    add(results, "Customer not publicly enabled", "PHASE3F_PUBLIC_CUSTOMER_ENABLED = True" not in dashboard_text, "public release disabled")

    with CHECK_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["label", "passed", "detail"])
        writer.writeheader()
        writer.writerows(results)

    CHECK_JSON.write_text(json.dumps({"results": results, "model": model}, indent=2), encoding="utf-8")

    lines = []
    lines.append("Phase 3F-6 customer-preview release-readiness check")
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append("")
    for row in results:
        status = "PASS" if row["passed"] else "FAIL"
        lines.append(f"{status:10} {row['label']:<65} {row['detail']}")
    passed = all(row["passed"] for row in results)
    lines.append("")
    lines.append("=" * 100)
    lines.append(f"Overall Phase 3F-6 checkpoint status: {'PASS' if passed else 'FAIL'}")
    lines.append("=" * 100)
    CHECK_REPORT.write_text("\n".join(lines), encoding="utf-8")

    for line in lines:
        print(line)
    print(f"Saved checkpoint report: {CHECK_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECK_JSON}")
    print(f"Saved checklist CSV:     {CHECK_CSV}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
