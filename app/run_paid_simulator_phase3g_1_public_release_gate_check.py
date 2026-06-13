"""
run_paid_simulator_phase3g_1_public_release_gate_check.py

Phase 3G-1 public Customer-view release-gate checkpoint.

This check does not enable the public Customer view. It verifies that the
project is ready to discuss a later controlled public-release switch while
keeping the current Customer view protected.
"""

from __future__ import annotations

import ast
import csv
import importlib
import json
import sys
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)

CHECKPOINT_REPORT = REPORT_DIR / "phase3g_1_public_release_gate_checkpoint_report.txt"
CHECKPOINT_JSON = REPORT_DIR / "phase3g_1_public_release_gate_checkpoint.json"
CHECKLIST_CSV = TABLE_DIR / "phase3g_1_public_release_gate_checklist.csv"

DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
GATE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase3g_public_customer_release_gate.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase3g_1_public_customer_release_gate.md"


def syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:  # pragma: no cover
        return False, repr(exc)


def contains(path: Path, text: str) -> bool:
    if not path.exists():
        return False
    return text in path.read_text(encoding="utf-8", errors="ignore")


def add(results: list[dict], name: str, passed: bool, detail: str):
    results.append({"name": name, "passed": bool(passed), "detail": detail})


def write_outputs(results: list[dict], model_data: dict | None):
    lines = []
    lines.append("=" * 100)
    lines.append("Phase 3G-1 public Customer-view release-gate check")
    lines.append("=" * 100)
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append("")

    for item in results:
        status = "PASS" if item["passed"] else "FAIL"
        lines.append(f"{status:<10} {item['name']:<70} {item['detail']}")

    all_passed = all(item["passed"] for item in results)
    lines.append("")
    lines.append("=" * 100)
    lines.append(f"Overall Phase 3G-1 checkpoint status: {'PASS' if all_passed else 'FAIL'}")
    lines.append("=" * 100)

    CHECKPOINT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    CHECKPOINT_JSON.write_text(
        json.dumps(
            {
                "checkpoint": "Phase 3G-1 public Customer-view release gate",
                "passed": all_passed,
                "results": results,
                "model": model_data,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    with CHECKLIST_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "passed", "detail"])
        writer.writeheader()
        writer.writerows(results)

    print("\n".join(lines))
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")
    print(f"Saved checklist CSV:     {CHECKLIST_CSV}")
    return all_passed


def main() -> int:
    results: list[dict] = []
    model_data: dict | None = None

    add(results, "phase3g_public_customer_release_gate.py exists", GATE_FILE.exists(), str(GATE_FILE))
    add(results, "run_paid_simulator_phase3g_1_public_release_gate_check.py exists", CURRENT_FILE.exists(), str(CURRENT_FILE))
    add(results, "phase3g_1_public_customer_release_gate.md exists", DOC_FILE.exists(), str(DOC_FILE))
    add(results, "Dashboard file exists", DASHBOARD_FILE.exists(), str(DASHBOARD_FILE))

    if DASHBOARD_FILE.exists():
        ok, detail = syntax_valid(DASHBOARD_FILE)
        add(results, "Dashboard syntax valid", ok, detail)
    else:
        add(results, "Dashboard syntax valid", False, "dashboard missing")

    if GATE_FILE.exists():
        ok, detail = syntax_valid(GATE_FILE)
        add(results, "Phase 3G gate module syntax valid", ok, detail)
    else:
        add(results, "Phase 3G gate module syntax valid", False, "module missing")

    try:
        module = importlib.import_module("app.paid_simulator.phase3g_public_customer_release_gate")
        model = module.build_phase3g_public_release_gate_model()
        model_data = model.to_dict()
        fallback = module.render_phase3g_public_release_gate(streamlit_module=None)
        add(results, "Phase 3G gate imports and renders", isinstance(fallback, dict), type(fallback).__name__)
        add(results, "Phase 3G ready marker present", model_data.get("marker") == "PHASE3G_1_PUBLIC_RELEASE_GATE_READY", str(model_data.get("marker")))
        add(results, "Public Customer release remains disabled", model_data.get("public_customer_release_enabled") is False, str(model_data.get("public_customer_release_enabled")))
        add(results, "Protected preview remains required", model_data.get("protected_preview_required") is True, str(model_data.get("protected_preview_required")))
        add(results, "Release guardrails present", len(model_data.get("guardrails", [])) >= 4, str(len(model_data.get("guardrails", []))))
        add(results, "Customer-facing requirements present", len(model_data.get("customer_facing_requirements", [])) >= 8, str(len(model_data.get("customer_facing_requirements", []))))
    except Exception as exc:
        add(results, "Phase 3G gate imports and renders", False, repr(exc))

    add(results, "Phase 3D markers still present", contains(DASHBOARD_FILE, "Phase 3D") or contains(DASHBOARD_FILE, "phase3d"), "Phase 3D marker search")
    add(results, "Phase 3E dashboard marker still present", contains(DASHBOARD_FILE, "PHASE3E_7C_DEVELOPER_TAB_READY"), "Phase 3E marker search")
    add(results, "Phase 3F dashboard marker still present", contains(DASHBOARD_FILE, "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY"), "Phase 3F marker search")
    add(results, "Ordinary Customer view not Phase 3G enabled", not contains(DASHBOARD_FILE, "PHASE3G_PUBLIC_CUSTOMER_ENABLED = True"), "customer protected")

    prior_reports = [
        REPORT_DIR / "phase3e_9_completion_checkpoint_report.txt",
        REPORT_DIR / "phase3f_3_customer_preview_route_checkpoint_report.txt",
        REPORT_DIR / "phase3f_8_completion_gate_checkpoint_report.txt",
    ]
    existing_reports = sum(1 for path in prior_reports if path.exists())
    add(results, "Prior Phase 3E/3F reports available", existing_reports >= 2, f"{existing_reports} of {len(prior_reports)} found")

    all_passed = write_outputs(results, model_data)
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
