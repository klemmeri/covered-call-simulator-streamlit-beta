"""Phase 3H-2 guarded public activation route checkpoint."""

from __future__ import annotations

import ast
import csv
import importlib.util
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
ROUTE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase3h_public_customer_activation_route.py"
INSTALLER_FILE = PROJECT_ROOT / "app" / "install_phase3h_2_public_activation_route.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase3h_2_public_customer_activation_route.md"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
BACKUP_DIR = PROJECT_ROOT / "outputs" / "backups" / "paid_simulator"

REPORT = REPORT_DIR / "phase3h_2_activation_route_checkpoint_report.txt"
JSON_REPORT = REPORT_DIR / "phase3h_2_activation_route_checkpoint.json"
CSV_REPORT = TABLE_DIR / "phase3h_2_activation_route_checklist.csv"
DECISION = REPORT_DIR / "phase3h_2_activation_route_release_decision.txt"

checks: list[tuple[bool, str, str]] = []


def add(condition: bool, label: str, detail: str = "") -> None:
    checks.append((bool(condition), label, detail))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> int:
    print("=" * 100)
    print("Phase 3H-2 guarded public activation route check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")

    for path, label in [
        (INSTALLER_FILE, "install_phase3h_2_public_activation_route.py"),
        (Path(__file__).resolve(), "run_paid_simulator_phase3h_2_activation_route_check.py"),
        (ROUTE_FILE, "phase3h_public_customer_activation_route.py"),
        (DOC_FILE, "phase3h_2_public_customer_activation_route.md"),
    ]:
        add(path.exists(), label, str(path))

    dashboard_text = read_text(DASHBOARD_FILE)
    route_text = read_text(ROUTE_FILE)

    try:
        ast.parse(dashboard_text)
        add(True, "Dashboard syntax valid", "syntax valid")
    except Exception as exc:
        add(False, "Dashboard syntax valid", repr(exc))

    try:
        ast.parse(route_text)
        add(True, "Activation route module syntax valid", "syntax valid")
    except Exception as exc:
        add(False, "Activation route module syntax valid", repr(exc))

    try:
        module = import_module(ROUTE_FILE, "phase3h_public_customer_activation_route_check")
        model = module.build_phase3h_public_activation_route_model()
        data = model.to_dict()
        fallback = module.render_phase3h_public_activation_route(streamlit_module=None)
        add(data.get("marker") == "PHASE3H_2_PUBLIC_CUSTOMER_ACTIVATION_ROUTE_READY", "Route model has ready marker", str(data.get("marker")))
        add(data.get("public_customer_enabled") is False, "Route model keeps public Customer view disabled", str(data.get("public_customer_enabled")))
        add(data.get("release_decision") == "PHASE3H_2_ROUTE_STAGED_PUBLIC_CUSTOMER_VIEW_DISABLED", "Route model has conservative release decision", str(data.get("release_decision")))
        add(len(data.get("guardrails", [])) >= 5, "Route model has guardrails", str(len(data.get("guardrails", []))))
        add(isinstance(fallback, dict), "Fallback render returns dict", type(fallback).__name__)
        labels = " ".join(data.get("customer_labels", [])).lower()
        for required in ["current price", "breakeven", "max profit", "downside cushion", "assignment zone", "warning"]:
            add(required in labels, f"Customer-facing label present: {required}", required)
    except Exception as exc:
        add(False, "Activation route module imports and renders", repr(exc))

    add("PHASE3H_2_PUBLIC_CUSTOMER_ACTIVATION_ROUTE_READY" in dashboard_text, "Dashboard has Phase 3H-2 readiness marker", "PHASE3H_2_PUBLIC_CUSTOMER_ACTIVATION_ROUTE_READY")
    add("_render_phase3h_public_customer_activation_route" in dashboard_text, "Dashboard has Phase 3H-2 helper function", "_render_phase3h_public_customer_activation_route")
    add("PHASE3H_2_PUBLIC_CUSTOMER_ENABLED = True" not in dashboard_text, "Public Customer view not enabled by Phase 3H-2", "customer protected")
    add("PHASE3G_4_PUBLIC_CUSTOMER_ENABLED = True" not in dashboard_text, "Phase 3G public route still disabled", "customer protected")
    add("PHASE3E_7C_DEVELOPER_TAB_READY" in dashboard_text, "Phase 3E marker still present", "Phase 3E marker search")
    add("PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY" in dashboard_text, "Phase 3F marker still present", "Phase 3F marker search")
    add("PHASE3G_4_PUBLIC_CUSTOMER_ROUTE_READY" in dashboard_text or "PHASE3G_4_PUBLIC_CUSTOMER_ENABLED" in dashboard_text, "Phase 3G marker still present", "Phase 3G marker search")
    backups = list(BACKUP_DIR.glob("config_form_app_before_phase3h_2_*.py"))
    add(len(backups) > 0, "Timestamped Phase 3H-2 dashboard backup exists", str(max(backups) if backups else BACKUP_DIR))

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    DECISION.write_text("PHASE3H_2_ROUTE_STAGED_PUBLIC_CUSTOMER_VIEW_DISABLED\n", encoding="utf-8")

    lines = []
    lines.append("=" * 100)
    lines.append("Phase 3H-2 guarded public activation route check")
    lines.append("=" * 100)
    for passed, label, detail in checks:
        status = "PASS" if passed else "FAIL"
        line = f"{status:<10} {label:<70} {detail}"
        print(line)
        lines.append(line)

    overall = all(passed for passed, _, _ in checks)
    lines.append("")
    lines.append("=" * 100)
    lines.append(f"Overall Phase 3H-2 checkpoint status: {'PASS' if overall else 'FAIL'}")
    lines.append("=" * 100)

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    JSON_REPORT.write_text(json.dumps({"overall_pass": overall, "checks": [{"pass": p, "label": l, "detail": d} for p, l, d in checks]}, indent=2), encoding="utf-8")
    with CSV_REPORT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["status", "label", "detail"])
        for passed, label, detail in checks:
            writer.writerow(["PASS" if passed else "FAIL", label, detail])

    print("\n" + "=" * 100)
    print(f"Overall Phase 3H-2 checkpoint status: {'PASS' if overall else 'FAIL'}")
    print("=" * 100)
    print(f"Saved checkpoint report: {REPORT}")
    print(f"Saved checkpoint JSON:   {JSON_REPORT}")
    print(f"Saved checklist CSV:     {CSV_REPORT}")
    print(f"Saved release decision:  {DECISION}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
