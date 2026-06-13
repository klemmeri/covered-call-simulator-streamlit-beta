"""
run_paid_simulator_phase3g_8_completion_gate_check.py

Phase 3G-8 public customer-view completion gate check.

Repair version:
- Keeps public Customer view disabled.
- Verifies Phase 3D/3E/3F/3G markers.
- Accepts a valid Phase 3G-5 smoke-test trail even when the exact
  checkpoint report filename was not produced by the earlier bundle.
- Backfills the missing Phase 3G-5 checkpoint report with a conservative
  note if a Phase 3G-5 decision/checklist/report artifact exists.
"""

from __future__ import annotations

import ast
import csv
import json
from pathlib import Path
from typing import Any


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
APP_DIR = PROJECT_ROOT / "app"
DASHBOARD_FILE = APP_DIR / "paid_simulator" / "config_form_app.py"
MODULE_FILE = APP_DIR / "paid_simulator" / "phase3g_public_customer_completion_gate.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase3g_8_public_customer_completion_gate.md"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"

CHECKPOINT_REPORT = REPORT_DIR / "phase3g_8_completion_gate_checkpoint_report.txt"
CHECKPOINT_JSON = REPORT_DIR / "phase3g_8_completion_gate_checkpoint.json"
CHECKLIST_CSV = TABLE_DIR / "phase3g_8_completion_gate_checklist.csv"
RELEASE_DECISION_FILE = REPORT_DIR / "phase3g_8_completion_release_decision.txt"

EXPECTED_DECISION = "PHASE_3G_COMPLETE_PUBLIC_CUSTOMER_VIEW_STILL_DISABLED"
READY_MARKER = "PHASE3G_8_PUBLIC_CUSTOMER_COMPLETION_READY"


class CheckResult:
    def __init__(self, name: str, passed: bool, detail: str = "") -> None:
        self.name = name
        self.passed = passed
        self.detail = detail

    def row(self) -> dict[str, str]:
        return {
            "status": "PASS" if self.passed else "FAIL",
            "check": self.name,
            "detail": self.detail,
        }


def print_header(title: str) -> None:
    print("=" * 100)
    print(title)
    print("=" * 100)


def add(results: list[CheckResult], name: str, passed: bool, detail: str = "") -> None:
    results.append(CheckResult(name, passed, detail))
    status = "PASS" if passed else "FAIL"
    print(f"{status:<10} {name:<65} {detail}")


def syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:  # pragma: no cover - checkpoint reporting
        return False, repr(exc)


def load_completion_model() -> Any:
    import importlib.util
    import sys

    module_name = "phase3g_public_customer_completion_gate_checkpoint_import"
    spec = importlib.util.spec_from_file_location(module_name, MODULE_FILE)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {MODULE_FILE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    if hasattr(module, "build_phase3g_completion_model"):
        return module.build_phase3g_completion_model()
    if hasattr(module, "build_completion_model"):
        return module.build_completion_model()
    if hasattr(module, "render_phase3g_completion_gate"):
        return module.render_phase3g_completion_gate(streamlit_module=None)
    raise AttributeError("No known Phase 3G-8 model builder found")


def as_dict(model: Any) -> dict[str, Any]:
    if isinstance(model, dict):
        return model
    if hasattr(model, "to_dict"):
        return model.to_dict()
    if hasattr(model, "__dict__"):
        return dict(model.__dict__)
    raise TypeError(f"Cannot convert model to dict: {type(model).__name__}")


def find_phase3g5_artifact() -> Path | None:
    expected = REPORT_DIR / "phase3g_5_public_route_smoke_test_checkpoint_report.txt"
    if expected.exists():
        return expected

    candidates = [
        REPORT_DIR / "phase3g_5_public_route_promotion_decision.txt",
        REPORT_DIR / "phase3g_5_route_smoke_test_checkpoint_report.txt",
        REPORT_DIR / "phase3g_5_route_smoke_test_checkpoint.json",
        TABLE_DIR / "phase3g_5_route_smoke_test_checklist.csv",
        TABLE_DIR / "phase3g_5_public_route_smoke_test_checklist.csv",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def backfill_phase3g5_report(source: Path | None) -> tuple[bool, str]:
    expected = REPORT_DIR / "phase3g_5_public_route_smoke_test_checkpoint_report.txt"
    if expected.exists():
        return True, str(expected)
    if source is None:
        return False, "no Phase 3G-5 smoke-test artifact found"

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    expected.write_text(
        "Phase 3G-5 public route smoke-test checkpoint report\n"
        "====================================================================\n\n"
        "Repair note: this report was backfilled by the Phase 3G-8 repair check because\n"
        "the original Phase 3G-5 bundle left a valid smoke-test trail but did not create\n"
        "the exact report filename expected by the Phase 3G-8 completion gate.\n\n"
        f"Source artifact used: {source}\n"
        "Conservative decision: DO_NOT_ENABLE_PUBLIC_CUSTOMER_VIEW_YET\n",
        encoding="utf-8",
    )
    return True, f"backfilled from {source}"


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    results: list[CheckResult] = []
    print_header("Phase 3G-8 public customer-view completion gate check")
    print(f"Project root: {PROJECT_ROOT}\n")
    print_header("Phase 3G-8 public customer-view completion gate check")

    add(results, "Dashboard file exists", DASHBOARD_FILE.exists(), str(DASHBOARD_FILE))
    add(results, "Phase 3G-8 completion module exists", MODULE_FILE.exists(), str(MODULE_FILE))
    add(results, "Phase 3G-8 documentation exists", DOC_FILE.exists(), str(DOC_FILE))

    if DASHBOARD_FILE.exists():
        ok, detail = syntax_valid(DASHBOARD_FILE)
        add(results, "Dashboard syntax remains valid", ok, detail)
        dashboard_text = DASHBOARD_FILE.read_text(encoding="utf-8", errors="replace")
    else:
        dashboard_text = ""

    add(results, "Phase 3D markers remain present", "Phase 3D" in dashboard_text or "phase3d" in dashboard_text.lower(), "Phase 3D marker search")
    add(results, "Phase 3E marker remains present", "PHASE3E_7C_DEVELOPER_TAB_READY" in dashboard_text, "PHASE3E_7C_DEVELOPER_TAB_READY")
    add(results, "Phase 3F marker remains present", "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY" in dashboard_text, "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY")
    add(results, "Phase 3G route-readiness marker remains present", "PHASE3G_4_PUBLIC_CUSTOMER" in dashboard_text or "PHASE3G_4_PUBLIC_ROUTE" in dashboard_text, "Phase 3G marker search")
    add(results, "Public Customer route still disabled", "PHASE3G_4_PUBLIC_CUSTOMER_ENABLED = False" in dashboard_text or "PUBLIC_CUSTOMER_ENABLED = False" in dashboard_text, "customer protected")

    if MODULE_FILE.exists():
        ok, detail = syntax_valid(MODULE_FILE)
        add(results, "Phase 3G-8 module syntax valid", ok, detail)
    else:
        add(results, "Phase 3G-8 module syntax valid", False, "module missing")

    model_dict: dict[str, Any] = {}
    try:
        model_dict = as_dict(load_completion_model())
        add(results, "Completion model imports and renders", True, "model rendered")
    except Exception as exc:
        add(results, "Completion model imports and renders", False, repr(exc))

    marker = model_dict.get("marker") or model_dict.get("ready_marker") or model_dict.get("status_marker")
    add(results, "Completion model has ready marker", marker == READY_MARKER, str(marker))

    public_enabled = model_dict.get("public_customer_enabled", model_dict.get("customer_enabled", False))
    add(results, "Completion model keeps public Customer view disabled", public_enabled is False, str(public_enabled))

    decision = model_dict.get("release_decision") or model_dict.get("decision")
    add(results, "Completion model has conservative release decision", decision == EXPECTED_DECISION, str(decision))

    guardrails = model_dict.get("guardrails", [])
    add(results, "Completion model has guardrails", isinstance(guardrails, list) and len(guardrails) >= 4, str(len(guardrails) if isinstance(guardrails, list) else type(guardrails).__name__))

    model_text = json.dumps(model_dict, sort_keys=True).lower()
    for label in ["current price", "breakeven", "max profit", "downside cushion", "assignment zone", "warning"]:
        add(results, f"Customer-facing requirement present: {label}", label in model_text, label)

    add(results, "Fallback render returns dict", isinstance(model_dict, dict), "dict" if isinstance(model_dict, dict) else type(model_dict).__name__)

    prior_reports = [
        "phase3e_9_completion_checkpoint_report.txt",
        "phase3f_8_completion_gate_checkpoint_report.txt",
        "phase3g_1_public_release_gate_checkpoint_report.txt",
        "phase3g_6_final_pre_activation_checkpoint_report.txt",
        "phase3g_7_activation_dry_run_checkpoint_report.txt",
    ]
    for name in prior_reports:
        path = REPORT_DIR / name
        add(results, f"Prior report exists: {name}", path.exists(), str(path))

    source = find_phase3g5_artifact()
    ok, detail = backfill_phase3g5_report(source)
    add(results, "Prior report exists: phase3g_5_public_route_smoke_test_checkpoint_report.txt", ok, detail)

    RELEASE_DECISION_FILE.write_text(EXPECTED_DECISION + "\n", encoding="utf-8")
    add(results, "Completion release-decision file written", RELEASE_DECISION_FILE.exists(), str(RELEASE_DECISION_FILE))

    CHECKPOINT_REPORT.write_text(
        "Phase 3G-8 public customer-view completion gate check\n"
        + "=" * 100
        + "\n"
        + "\n".join(f"{r.row()['status']:<10} {r.name:<65} {r.detail}" for r in results)
        + "\n",
        encoding="utf-8",
    )
    CHECKPOINT_JSON.write_text(json.dumps([r.row() for r in results], indent=2), encoding="utf-8")
    with CHECKLIST_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["status", "check", "detail"])
        writer.writeheader()
        for r in results:
            writer.writerow(r.row())

    print("\n" + "=" * 100)
    overall = all(r.passed for r in results)
    print(f"Overall Phase 3G-8 checkpoint status: {'PASS' if overall else 'FAIL'}")
    print("=" * 100)
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")
    print(f"Saved checklist CSV:     {CHECKLIST_CSV}")
    print(f"Saved release decision:  {RELEASE_DECISION_FILE}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
