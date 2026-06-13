"""
Phase 3I-2 customer workflow smoke-test checkpoint.

Run from PyCharm or terminal:
    python app/run_paid_simulator_phase3i_2_customer_workflow_smoke_test_check.py
"""
from __future__ import annotations

import ast
import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)

DASHBOARD = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
MODULE = PROJECT_ROOT / "app" / "paid_simulator" / "phase3i_customer_workflow_smoke_test.py"
DOC = PROJECT_ROOT / "docs" / "phase3i_2_customer_workflow_smoke_test.md"

REQUIRED_LABELS = [
    "current price",
    "strike",
    "premium",
    "breakeven",
    "max profit",
    "downside cushion",
    "assignment zone",
    "warning",
]

PRIOR_REPORTS = [
    "phase3h_8_post_activation_completion_checkpoint_report.txt",
    "phase3i_1_post_activation_browser_checkpoint_report.txt",
]


def add_result(rows, ok, name, detail=""):
    rows.append({"status": "PASS" if ok else "FAIL", "check": name, "detail": str(detail)})


def syntax_valid(path: Path):
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:
        return False, repr(exc)


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def main():
    rows = []
    print("=" * 100)
    print("Phase 3I-2 customer workflow smoke-test check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}\n")

    add_result(rows, DASHBOARD.exists(), "Dashboard file exists", DASHBOARD)
    add_result(rows, MODULE.exists(), "Phase 3I-2 smoke-test module exists", MODULE)
    add_result(rows, DOC.exists(), "Phase 3I-2 documentation exists", DOC)

    if DASHBOARD.exists():
        ok, detail = syntax_valid(DASHBOARD)
        add_result(rows, ok, "Dashboard syntax remains valid", detail)
        text = DASHBOARD.read_text(encoding="utf-8", errors="replace")
        add_result(rows, "PHASE3H_7_PUBLIC_CUSTOMER_ACTIVATION_ENABLED" in text or "PHASE3H_7_PUBLIC_CUSTOMER_VIEW_CONTROLLED_ACTIVATION_ENABLED" in text, "Phase 3H public activation evidence present", "activation marker search")
        add_result(rows, "PHASE3E_7C_DEVELOPER_TAB_READY" in text, "Phase 3E marker remains present", "Phase 3E marker search")
        add_result(rows, "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY" in text, "Phase 3F marker remains present", "Phase 3F marker search")
        add_result(rows, "PHASE3G_4_PUBLIC_CUSTOMER" in text or "PHASE3G_8_PUBLIC_CUSTOMER_COMPLETION_READY" in text, "Phase 3G marker/evidence remains present", "Phase 3G marker search")
        add_result(rows, "Phase 3D" in text or "phase3d" in text.lower(), "Phase 3D markers remain present", "Phase 3D marker search")

    model = {}
    if MODULE.exists():
        ok, detail = syntax_valid(MODULE)
        add_result(rows, ok, "Phase 3I-2 module syntax valid", detail)
        try:
            mod = import_module(MODULE, "phase3i_customer_workflow_smoke_test")
            model = mod.render_phase3i_customer_workflow_smoke_test(streamlit_module=None)
            add_result(rows, isinstance(model, dict), "Fallback render returns dict", type(model).__name__)
        except Exception as exc:
            add_result(rows, False, "Phase 3I-2 module imports and renders", repr(exc))
            model = {}

    add_result(rows, model.get("marker") == "PHASE3I_2_CUSTOMER_WORKFLOW_SMOKE_TEST_READY", "Smoke-test model has ready marker", model.get("marker"))
    add_result(rows, model.get("public_customer_view_expected_enabled") is True, "Smoke-test expects controlled public activation enabled", model.get("public_customer_view_expected_enabled"))
    add_result(rows, model.get("release_decision") == "PHASE3I_2_CUSTOMER_WORKFLOW_SMOKE_TEST_PASS", "Smoke-test model has pass release decision", model.get("release_decision"))
    add_result(rows, len(model.get("guardrails", [])) >= 4, "Smoke-test model has guardrails", len(model.get("guardrails", [])))
    labels_text = " ".join(model.get("customer_facing_labels", [])).lower()
    for label in REQUIRED_LABELS:
        add_result(rows, label in labels_text, f"Customer-facing label present: {label}", label)

    for report in PRIOR_REPORTS:
        path = REPORT_DIR / report
        add_result(rows, path.exists(), f"Prior report exists: {report}", path)

    decision_path = REPORT_DIR / "phase3i_2_customer_workflow_smoke_test_release_decision.txt"
    decision_path.write_text(str(model.get("release_decision", "UNKNOWN")), encoding="utf-8")
    add_result(rows, decision_path.exists(), "Smoke-test release-decision file written", decision_path)

    df = pd.DataFrame(rows)
    csv_path = TABLE_DIR / "phase3i_2_customer_workflow_smoke_test_checklist.csv"
    report_path = REPORT_DIR / "phase3i_2_customer_workflow_smoke_test_checkpoint_report.txt"
    json_path = REPORT_DIR / "phase3i_2_customer_workflow_smoke_test_checkpoint.json"
    df.to_csv(csv_path, index=False)
    json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    lines = []
    for row in rows:
        lines.append(f"{row['status']:<10} {row['check']:<70} {row['detail']}")
    report_path.write_text("\n".join(lines), encoding="utf-8")

    for line in lines:
        print(line)
    print("\n" + "=" * 100)
    failed = [r for r in rows if r["status"] != "PASS"]
    if failed:
        print("Overall Phase 3I-2 checkpoint status: FAIL")
        print("=" * 100)
        print(f"Saved checkpoint report: {report_path}")
        sys.exit(1)
    print("Overall Phase 3I-2 checkpoint status: PASS")
    print("=" * 100)
    print(f"Saved checkpoint report: {report_path}")
    print(f"Saved checkpoint JSON:   {json_path}")
    print(f"Saved checklist CSV:     {csv_path}")
    print(f"Saved release decision:  {decision_path}")


if __name__ == "__main__":
    main()
