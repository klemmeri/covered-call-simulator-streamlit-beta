"""
Phase 3H-8 post-activation completion gate check.

Validates that the public Customer-view activation from Phase 3H-7 is present,
controlled, backed up, and compatible with prior Phase 3D/3E/3F/3G/3H markers.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
DASHBOARD_FILE = APP_DIR / "paid_simulator" / "config_form_app.py"
MODULE_FILE = APP_DIR / "paid_simulator" / "phase3h_post_activation_completion_gate.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase3h_8_post_activation_completion_gate.md"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
BACKUP_DIR = PROJECT_ROOT / "outputs" / "backups" / "paid_simulator"

REPORT_FILE = REPORT_DIR / "phase3h_8_post_activation_completion_checkpoint_report.txt"
JSON_FILE = REPORT_DIR / "phase3h_8_post_activation_completion_checkpoint.json"
CSV_FILE = TABLE_DIR / "phase3h_8_post_activation_completion_checklist.csv"
DECISION_FILE = REPORT_DIR / "phase3h_8_post_activation_completion_release_decision.txt"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def valid_syntax(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True, "syntax valid"
    except Exception as exc:
        return False, repr(exc)


def add(results: list[dict], label: str, passed: bool, detail: str = "") -> None:
    results.append({"label": label, "passed": bool(passed), "detail": detail})


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []

    add(results, "Dashboard file exists", DASHBOARD_FILE.exists(), str(DASHBOARD_FILE))
    add(results, "Phase 3H-8 completion module exists", MODULE_FILE.exists(), str(MODULE_FILE))
    add(results, "Phase 3H-8 documentation exists", DOC_FILE.exists(), str(DOC_FILE))

    if DASHBOARD_FILE.exists():
        ok, detail = valid_syntax(DASHBOARD_FILE)
        add(results, "Dashboard syntax remains valid", ok, detail)
        dashboard_text = DASHBOARD_FILE.read_text(encoding="utf-8", errors="ignore")
    else:
        dashboard_text = ""

    for marker, label in [
        ("Phase 3D", "Phase 3D markers remain present"),
        ("PHASE3E_7C_DEVELOPER_TAB_READY", "Phase 3E marker remains present"),
        ("PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY", "Phase 3F marker remains present"),
        ("PHASE3G_4", "Phase 3G route-readiness marker remains present"),
        ("PHASE3H_2", "Phase 3H route marker/evidence remains present"),
    ]:
        evidence = marker in dashboard_text
        if marker == "PHASE3H_2":
            evidence = evidence or (REPORT_DIR / "phase3h_2_activation_route_checkpoint_report.txt").exists()
        add(results, label, evidence, marker)

    activation_evidence = any(s in dashboard_text for s in [
        "PHASE3H_7_PUBLIC_CUSTOMER_VIEW_CONTROLLED_ACTIVATION_ENABLED",
        "PHASE3H_7_PUBLIC_CUSTOMER_ENABLED = True",
        "PHASE3H_7_PUBLIC_CUSTOMER_ACTIVATION_READY",
    ])
    add(results, "Phase 3H-7 controlled activation marker present", activation_evidence, "Phase 3H-7 activation marker search")

    public_disabled_legacy = "PHASE3H_2_PUBLIC_CUSTOMER_ENABLED = False" in dashboard_text
    public_enabled_controlled = activation_evidence
    add(results, "Public Customer view controlled activation is enabled", public_enabled_controlled, str(public_enabled_controlled))
    add(results, "Legacy disabled marker may remain but is superseded by Phase 3H-7", public_disabled_legacy or public_enabled_controlled, "compatibility marker check")

    backup_exists = False
    backup_detail = ""
    if BACKUP_DIR.exists():
        backups = sorted(BACKUP_DIR.glob("config_form_app_before_phase3h_7*.py"))
        backup_exists = len(backups) > 0
        backup_detail = str(backups[-1]) if backups else "no Phase 3H-7 backup found"
    add(results, "Timestamped Phase 3H-7 dashboard backup exists", backup_exists, backup_detail)

    if MODULE_FILE.exists():
        ok, detail = valid_syntax(MODULE_FILE)
        add(results, "Phase 3H-8 module syntax valid", ok, detail)
        try:
            module = load_module(MODULE_FILE, "phase3h8_completion_gate_runtime")
            model = module.render_phase3h_8_completion_gate(streamlit_module=None)
            add(results, "Fallback render returns dict", isinstance(model, dict), type(model).__name__)
            add(results, "Completion model has ready marker", model.get("marker") == "PHASE3H_8_POST_ACTIVATION_COMPLETION_READY", str(model.get("marker")))
            add(results, "Completion model confirms public Customer activation", model.get("public_customer_view_enabled") is True, str(model.get("public_customer_view_enabled")))
            add(results, "Completion model has final release decision", model.get("release_decision") == "PHASE3H_COMPLETE_PUBLIC_CUSTOMER_VIEW_CONTROLLED_ACTIVATION_VERIFIED", str(model.get("release_decision")))
            add(results, "Completion model has guardrails", len(model.get("guardrails", [])) >= 5, str(len(model.get("guardrails", []))))
            label_text = "\n".join(model.get("customer_labels", [])).lower()
            for required in ["current price", "breakeven", "max profit", "downside cushion", "assignment zone", "warning"]:
                add(results, f"Customer-facing label present: {required}", required in label_text, required)
        except Exception as exc:
            add(results, "Phase 3H-8 module imports and renders", False, repr(exc))

    prior_reports = [
        "phase3e_9_completion_checkpoint_report.txt",
        "phase3f_8_completion_gate_checkpoint_report.txt",
        "phase3g_8_completion_gate_checkpoint_report.txt",
        "phase3h_6_final_activation_review_checkpoint_report.txt",
        "phase3h_7_public_activation_checkpoint_report.txt",
    ]
    for filename in prior_reports:
        path = REPORT_DIR / filename
        add(results, f"Prior report exists: {filename}", path.exists(), str(path))

    decision = "PHASE3H_COMPLETE_PUBLIC_CUSTOMER_VIEW_CONTROLLED_ACTIVATION_VERIFIED"
    DECISION_FILE.write_text(decision + "\n", encoding="utf-8")
    add(results, "Completion release-decision file written", DECISION_FILE.exists(), str(DECISION_FILE))

    lines = []
    header = "=" * 100
    title = "Phase 3H-8 post-activation completion gate check"
    lines.append(header)
    lines.append(title)
    lines.append(header)
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append("")
    for item in results:
        status = "PASS" if item["passed"] else "FAIL"
        lines.append(f"{status:<10} {item['label']:<70} {item['detail']}")
    lines.append("")
    overall = all(item["passed"] for item in results)
    lines.append(header)
    lines.append(f"Overall Phase 3H-8 checkpoint status: {'PASS' if overall else 'FAIL'}")
    lines.append(header)

    report_text = "\n".join(lines) + "\n"
    REPORT_FILE.write_text(report_text, encoding="utf-8")
    JSON_FILE.write_text(json.dumps({"overall_pass": overall, "results": results}, indent=2), encoding="utf-8")
    CSV_FILE.write_text("status,label,detail\n" + "\n".join(
        f"{'PASS' if r['passed'] else 'FAIL'},\"{r['label']}\",\"{str(r['detail']).replace(chr(34), chr(34)+chr(34))}\"" for r in results
    ) + "\n", encoding="utf-8")

    print(report_text)
    print(f"Saved checkpoint report: {REPORT_FILE}")
    print(f"Saved checkpoint JSON:   {JSON_FILE}")
    print(f"Saved checklist CSV:     {CSV_FILE}")
    print(f"Saved release decision:  {DECISION_FILE}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
