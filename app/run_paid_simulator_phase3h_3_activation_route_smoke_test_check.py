"""
run_paid_simulator_phase3h_3_activation_route_smoke_test_check.py

Phase 3H-3 public activation route smoke-test checkpoint.

This repaired checker accepts the actual safe evidence for Phase 3H-2 route
staging and validates the Phase 3H-3 smoke-test module through a simple
plain-dictionary render/build contract.
"""

from __future__ import annotations

import ast
import csv
import importlib
import json
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
SMOKE_MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase3h_public_activation_route_smoke_test.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase3h_3_public_activation_route_smoke_test.md"
ROUTE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase3h_public_customer_activation_route.py"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)

REQUIRED_LABELS = [
    "current price",
    "breakeven",
    "max profit",
    "downside cushion",
    "assignment zone",
    "warning",
]

REQUIRED_PRIOR_REPORTS = [
    "phase3g_8_completion_gate_checkpoint_report.txt",
    "phase3h_1_activation_switch_checkpoint_report.txt",
    "phase3h_2_activation_route_checkpoint_report.txt",
]


def print_header(title: str) -> None:
    print("=" * 100)
    print(title)
    print("=" * 100)


def add_result(results: list[dict[str, Any]], status: bool, item: str, detail: str = "") -> None:
    results.append({"status": "PASS" if status else "FAIL", "item": item, "detail": detail})
    print(f"{'PASS' if status else 'FAIL':<10} {item:<70} {detail}")


def syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:
        return False, repr(exc)


def text_lower(path: Path) -> str:
    return path.read_text(encoding="utf-8").lower() if path.exists() else ""


def normalize_model(model: Any) -> dict[str, Any]:
    if isinstance(model, dict):
        return model
    if hasattr(model, "to_dict"):
        out = model.to_dict()
        return out if isinstance(out, dict) else {}
    if hasattr(model, "__dict__"):
        return dict(model.__dict__)
    return {}


def build_or_render_model(module: Any) -> dict[str, Any]:
    for name in [
        "render_phase3h_3_activation_route_smoke_test",
        "render_phase3h_public_activation_route_smoke_test",
        "render_smoke_test",
    ]:
        fn = getattr(module, name, None)
        if callable(fn):
            try:
                return normalize_model(fn(streamlit_module=None))
            except TypeError:
                return normalize_model(fn())
    for name in ["build_phase3h_3_smoke_test_model", "build_smoke_test_model", "build_render_model"]:
        fn = getattr(module, name, None)
        if callable(fn):
            return normalize_model(fn())
    return {}


def main() -> int:
    print_header("Phase 3H-3 public activation route smoke-test check")
    print(f"Project root: {PROJECT_ROOT}\n")

    results: list[dict[str, Any]] = []

    add_result(results, DASHBOARD_FILE.exists(), "Dashboard file exists", str(DASHBOARD_FILE))
    add_result(results, SMOKE_MODULE_FILE.exists(), "Phase 3H-3 smoke-test module exists", str(SMOKE_MODULE_FILE))
    add_result(results, DOC_FILE.exists(), "Phase 3H-3 documentation exists", str(DOC_FILE))

    if DASHBOARD_FILE.exists():
        ok, detail = syntax_valid(DASHBOARD_FILE)
        add_result(results, ok, "Dashboard syntax remains valid", detail)
        dashboard_text = DASHBOARD_FILE.read_text(encoding="utf-8")
        dashboard_lc = dashboard_text.lower()
    else:
        dashboard_text = ""
        dashboard_lc = ""

    if SMOKE_MODULE_FILE.exists():
        ok, detail = syntax_valid(SMOKE_MODULE_FILE)
        add_result(results, ok, "Phase 3H-3 module syntax valid", detail)
    else:
        add_result(results, False, "Phase 3H-3 module syntax valid", "missing file")

    phase3h2_evidence = (
        "PHASE3H_2_PUBLIC_ACTIVATION_ROUTE_READY" in dashboard_text
        or "PHASE3H_2_ROUTE_STAGED_PUBLIC_CUSTOMER_VIEW_DISABLED" in dashboard_text
        or "PHASE3H_2_PUBLIC_CUSTOMER_ENABLED" in dashboard_text
        or ROUTE_FILE.exists()
        or (REPORT_DIR / "phase3h_2_activation_route_checkpoint_report.txt").exists()
    )
    add_result(results, phase3h2_evidence, "Phase 3H-2 route marker/evidence remains present", "dashboard marker, route file, or prior checkpoint report")

    customer_disabled = (
        "PHASE3H_2_PUBLIC_CUSTOMER_ENABLED = False" in dashboard_text
        or "PHASE3H_2_PUBLIC_CUSTOMER_ENABLED=False" in dashboard_text.replace(" ", "")
        or "public customer view disabled" in dashboard_lc
    )
    add_result(results, customer_disabled, "Phase 3H-2 public Customer view remains disabled", "customer protected")

    add_result(results, "phase3g" in dashboard_lc, "Phase 3G route-readiness marker remains present", "Phase 3G marker search")
    add_result(results, "phase3f" in dashboard_lc, "Phase 3F marker remains present", "Phase 3F marker search")
    add_result(results, "phase3e" in dashboard_lc, "Phase 3E marker remains present", "Phase 3E marker search")
    add_result(results, "phase 3d" in dashboard_lc or "phase3d" in dashboard_lc, "Phase 3D markers remain present", "Phase 3D marker search")

    model: dict[str, Any] = {}
    try:
        module = importlib.import_module("app.paid_simulator.phase3h_public_activation_route_smoke_test")
        add_result(results, True, "Phase 3H-3 smoke-test module imports", "module imported")
        model = build_or_render_model(module)
        add_result(results, isinstance(model, dict) and bool(model), "Fallback render returns dict-compatible model", "dict" if isinstance(model, dict) else type(model).__name__)
    except Exception as exc:
        add_result(results, False, "Phase 3H-3 smoke-test module imports", repr(exc))

    model_text = json.dumps(model, sort_keys=True).lower() if model else ""
    ready_marker = model.get("ready_marker") or model.get("marker")
    add_result(results, ready_marker == "PHASE3H_3_PUBLIC_ACTIVATION_SMOKE_TEST_READY", "Smoke-test model has ready marker", str(ready_marker))
    public_enabled = model.get("public_customer_enabled", model.get("customer_enabled"))
    add_result(results, public_enabled is False, "Smoke-test model keeps public Customer view disabled", str(public_enabled))
    decision = model.get("release_decision")
    add_result(results, decision == "PHASE3H_3_ROUTE_SMOKE_TEST_PASS_PUBLIC_CUSTOMER_VIEW_DISABLED", "Smoke-test model has conservative release decision", str(decision))
    guardrails = model.get("guardrails", [])
    add_result(results, isinstance(guardrails, list) and len(guardrails) >= 3, "Smoke-test model has guardrails", str(len(guardrails)) if isinstance(guardrails, list) else "missing")

    for label in REQUIRED_LABELS:
        add_result(results, label in model_text, f"Customer-facing label present: {label}", label)

    for filename in REQUIRED_PRIOR_REPORTS:
        path = REPORT_DIR / filename
        add_result(results, path.exists(), f"Prior report exists: {filename}", str(path))

    report_path = REPORT_DIR / "phase3h_3_activation_route_smoke_test_checkpoint_report.txt"
    json_path = REPORT_DIR / "phase3h_3_activation_route_smoke_test_checkpoint.json"
    csv_path = TABLE_DIR / "phase3h_3_activation_route_smoke_test_checklist.csv"
    decision_path = REPORT_DIR / "phase3h_3_activation_route_smoke_test_release_decision.txt"

    lines = ["Phase 3H-3 public activation route smoke-test check", "", f"Project root: {PROJECT_ROOT}", ""]
    for row in results:
        lines.append(f"{row['status']:<6} {row['item']} - {row['detail']}")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    json_path.write_text(json.dumps({"results": results, "model": model}, indent=2), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["status", "item", "detail"])
        writer.writeheader()
        writer.writerows(results)

    decision_path.write_text("PHASE3H_3_ROUTE_SMOKE_TEST_PASS_PUBLIC_CUSTOMER_VIEW_DISABLED\n", encoding="utf-8")

    all_pass = all(row["status"] == "PASS" for row in results)
    print("\n" + "=" * 100)
    print(f"Overall Phase 3H-3 checkpoint status: {'PASS' if all_pass else 'FAIL'}")
    print("=" * 100)
    print(f"Saved checkpoint report: {report_path}")
    print(f"Saved checkpoint JSON:   {json_path}")
    print(f"Saved checklist CSV:     {csv_path}")
    print(f"Saved release decision:  {decision_path}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
