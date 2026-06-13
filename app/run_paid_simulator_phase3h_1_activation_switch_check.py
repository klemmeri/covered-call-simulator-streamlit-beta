"""
run_paid_simulator_phase3h_1_activation_switch_check.py

Checkpoint script for Phase 3H-1 public Customer-view activation switch scaffold.
"""

from __future__ import annotations

import ast
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

DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase3h_public_customer_activation_switch.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase3h_1_public_customer_activation_switch.md"

CHECKPOINT_REPORT = REPORT_DIR / "phase3h_1_activation_switch_checkpoint_report.txt"
CHECKPOINT_JSON = REPORT_DIR / "phase3h_1_activation_switch_checkpoint.json"
CHECKLIST_CSV = TABLE_DIR / "phase3h_1_activation_switch_checklist.csv"
RELEASE_DECISION_FILE = REPORT_DIR / "phase3h_1_activation_switch_release_decision.txt"

EXPECTED_PRIOR_REPORT_CANDIDATES = [
    ["phase3e_9_completion_checkpoint_report.txt"],
    ["phase3f_8_completion_gate_checkpoint_report.txt"],
    ["phase3g_8_completion_gate_checkpoint_report.txt"],
]

DASHBOARD_MARKERS = {
    "Phase 3D markers remain present": ["Phase 3D", "phase3d", "integrated overlay"],
    "Phase 3E marker remains present": ["PHASE3E_7C_DEVELOPER_TAB_READY", "Phase 3E customer payoff workbench"],
    "Phase 3F marker remains present": ["PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY"],
    "Phase 3G marker remains present": ["PHASE3G_4_PUBLIC_CUSTOMER_ENABLED", "PHASE3G"],
}


def syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:
        return False, repr(exc)


def has_any_marker(text: str, markers: list[str]) -> bool:
    return any(marker in text for marker in markers)


def record(rows: list[dict], passed: bool, label: str, detail: str) -> None:
    rows.append({"status": "PASS" if passed else "FAIL", "label": label, "detail": detail})


def print_rows(rows: list[dict]) -> None:
    for row in rows:
        print(f"{row['status']:<10} {row['label']:<65} {row['detail']}")


def main() -> int:
    rows: list[dict] = []

    print("=" * 100)
    print("Phase 3H-1 public Customer-view activation switch check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    record(rows, DASHBOARD_FILE.exists(), "Dashboard file exists", str(DASHBOARD_FILE))
    record(rows, MODULE_FILE.exists(), "Phase 3H-1 activation module exists", str(MODULE_FILE))
    record(rows, DOC_FILE.exists(), "Phase 3H-1 documentation exists", str(DOC_FILE))

    if DASHBOARD_FILE.exists():
        ok, detail = syntax_valid(DASHBOARD_FILE)
        record(rows, ok, "Dashboard syntax remains valid", detail)
        dashboard_text = DASHBOARD_FILE.read_text(encoding="utf-8")
        for label, markers in DASHBOARD_MARKERS.items():
            record(rows, has_any_marker(dashboard_text, markers), label, "marker search")
        public_disabled = "PHASE3G_4_PUBLIC_CUSTOMER_ENABLED = False" in dashboard_text or "PUBLIC_CUSTOMER_VIEW_ENABLED = False" in dashboard_text
        record(rows, public_disabled, "Public Customer route remains disabled", "customer protected")
    else:
        dashboard_text = ""

    if MODULE_FILE.exists():
        ok, detail = syntax_valid(MODULE_FILE)
        record(rows, ok, "Phase 3H-1 module syntax valid", detail)
    
    try:
        module = importlib.import_module("app.paid_simulator.phase3h_public_customer_activation_switch")
        model = module.build_phase3h_activation_switch_model()
        data = model.to_dict()
        fallback = module.render_phase3h_activation_switch(streamlit_module=None)
        record(rows, data.get("marker") == "PHASE3H_1_PUBLIC_CUSTOMER_ACTIVATION_SWITCH_READY", "Activation model has ready marker", str(data.get("marker")))
        record(rows, data.get("public_customer_view_enabled") is False, "Activation model keeps public Customer view disabled", str(data.get("public_customer_view_enabled")))
        record(rows, data.get("protected_preview_required") is True, "Activation model requires protected preview", str(data.get("protected_preview_required")))
        record(rows, len(data.get("activation_guardrails", [])) >= 5, "Activation model has guardrails", str(len(data.get("activation_guardrails", []))))
        record(rows, len(data.get("activation_requirements", [])) >= 5, "Activation model has activation requirements", str(len(data.get("activation_requirements", []))))
        for label in ["current price", "breakeven", "max profit", "downside cushion", "assignment zone", "warning"]:
            found = label in " ".join(data.get("customer_facing_requirements", [])).lower()
            record(rows, found, f"Customer-facing requirement present: {label}", label)
        record(rows, isinstance(fallback, dict), "Fallback render returns dict", type(fallback).__name__)
        release_decision = data.get("release_decision", "")
    except Exception as exc:
        record(rows, False, "Phase 3H-1 module imports and renders", repr(exc))
        release_decision = "IMPORT_OR_RENDER_FAILED"

    for candidates in EXPECTED_PRIOR_REPORT_CANDIDATES:
        found_path = None
        for candidate in candidates:
            path = REPORT_DIR / candidate
            if path.exists():
                found_path = path
                break
        record(rows, found_path is not None, f"Prior report exists: {' or '.join(candidates)}", str(found_path) if found_path else "missing")

    RELEASE_DECISION_FILE.write_text(release_decision + "\n", encoding="utf-8")
    record(rows, RELEASE_DECISION_FILE.exists(), "Release-decision file written", str(RELEASE_DECISION_FILE))

    print_rows(rows)
    print()

    passed = all(row["status"] == "PASS" for row in rows)
    status_line = f"Overall Phase 3H-1 checkpoint status: {'PASS' if passed else 'FAIL'}"
    print("=" * 100)
    print(status_line)
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "Phase 3H-1 public Customer-view activation switch check\n"
        + "=" * 100
        + "\n"
        + "\n".join(f"{row['status']:<10} {row['label']:<65} {row['detail']}" for row in rows)
        + "\n\n"
        + status_line
        + "\n",
        encoding="utf-8",
    )
    CHECKPOINT_JSON.write_text(json.dumps({"passed": passed, "rows": rows, "release_decision": release_decision}, indent=2), encoding="utf-8")
    CHECKLIST_CSV.write_text(
        "status,label,detail\n"
        + "\n".join(
            f"{row['status']},\"{row['label'].replace(chr(34), chr(34)*2)}\",\"{row['detail'].replace(chr(34), chr(34)*2)}\""
            for row in rows
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")
    print(f"Saved checklist CSV:     {CHECKLIST_CSV}")
    print(f"Saved release decision:  {RELEASE_DECISION_FILE}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
