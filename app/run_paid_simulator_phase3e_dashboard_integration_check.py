"""
run_paid_simulator_phase3e_dashboard_integration_check.py

Phase 3E-7A checkpoint:
Validate the standalone Developer-view dashboard integration adapter for the
customer payoff workbench without replacing config_form_app.py.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"

for path in (PROJECT_ROOT, APP_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


def status_line(ok: bool, label: str, detail: str = "") -> str:
    status = "PASS" if ok else "FAIL"
    return f"{status:<10} {label:<68} {detail}"


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    checks: list[bool] = []

    lines.append("=" * 96)
    lines.append("Phase 3E-7A Developer dashboard integration adapter check")
    lines.append("=" * 96)
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append("")

    expected_files = [
        APP_DIR / "paid_simulator" / "phase3e_customer_workbench_dashboard.py",
        APP_DIR / "run_paid_simulator_phase3e_dashboard_integration_check.py",
        PROJECT_ROOT / "docs" / "phase3e_dashboard_integration.md",
    ]

    lines.append("Expected files")
    lines.append("-" * 96)
    for file_path in expected_files:
        ok = file_path.exists()
        checks.append(ok)
        lines.append(status_line(ok, file_path.name, str(file_path)))
    lines.append("")

    try:
        from app.paid_simulator.phase3e_customer_workbench_dashboard import (
            CUSTOMER_PROTECTION_NOTE,
            TAB_TITLE,
            build_dashboard_render_model,
            get_dashboard_integration_snippet,
            render_phase3e_customer_workbench_dashboard,
        )

        import_ok = True
        import_detail = "module imported"
    except Exception as exc:
        import_ok = False
        import_detail = repr(exc)

    checks.append(import_ok)
    lines.append("Import check")
    lines.append("-" * 96)
    lines.append(status_line(import_ok, "Dashboard adapter import", import_detail))
    lines.append("")

    model_dict = {}
    snippet = ""
    if import_ok:
        try:
            model = build_dashboard_render_model()
            model_dict = model.as_dict()
            snippet = get_dashboard_integration_snippet()
            render_model = render_phase3e_customer_workbench_dashboard(st=None)

            model_checks = [
                (model.tab_title == TAB_TITLE, "Tab title matches exported constant", model.tab_title),
                ("Developer-view only" in model.protection_note, "Protection note says Developer-view only", model.protection_note),
                (len(model.sections) >= 4, "At least four dashboard sections", str(len(model.sections))),
                (any(section.section_type == "warning" for section in model.sections), "Warning section present", "warning section"),
                ("Customer view" in CUSTOMER_PROTECTION_NOTE, "Customer-view protection language present", CUSTOMER_PROTECTION_NOTE),
                ("config_form_app.py" in snippet, "Integration snippet references dashboard file", "snippet ready"),
                ("Developer-view" in snippet or "Developer" in snippet, "Integration snippet is developer scoped", "developer scoped"),
                (render_model.tab_title == model.tab_title, "Render returns same model when Streamlit absent", render_model.tab_title),
            ]
        except Exception as exc:
            model_checks = [(False, "Build/render dashboard model", repr(exc))]

        lines.append("Dashboard adapter behavior")
        lines.append("-" * 96)
        for ok, label, detail in model_checks:
            checks.append(ok)
            lines.append(status_line(ok, label, detail))
        lines.append("")

    config_file = APP_DIR / "paid_simulator" / "config_form_app.py"
    config_exists = config_file.exists()
    checks.append(config_exists)
    lines.append("Existing dashboard boundary check")
    lines.append("-" * 96)
    lines.append(status_line(config_exists, "Existing dashboard file found", str(config_file)))

    if config_exists:
        text = config_file.read_text(encoding="utf-8", errors="replace")
        phase3d_ok = "Phase 3D" in text or "phase3d" in text.lower()
        customer_view_ok = "Customer" in text or "customer" in text.lower()
        phase3e_not_forced = "render_phase3e_customer_workbench_dashboard" not in text
        checks.extend([phase3d_ok, customer_view_ok, phase3e_not_forced])
        lines.append(status_line(phase3d_ok, "Phase 3D dashboard markers still detectable", "marker search"))
        lines.append(status_line(customer_view_ok, "Customer-view markers detectable", "marker search"))
        lines.append(status_line(phase3e_not_forced, "Phase 3E not blindly injected into dashboard", "safe standalone adapter"))
    lines.append("")

    if model_dict:
        json_path = REPORT_DIR / "phase3e_dashboard_integration_render_model.json"
        json_path.write_text(json.dumps(model_dict, indent=2), encoding="utf-8")
        checks.append(json_path.exists())
        lines.append(status_line(json_path.exists(), "Render-model JSON written", str(json_path)))

        sections_csv = TABLE_DIR / "phase3e_dashboard_integration_sections.csv"
        with sections_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "section_type", "body"])
            writer.writeheader()
            for section in model_dict["sections"]:
                writer.writerow(section)
        checks.append(sections_csv.exists())
        lines.append(status_line(sections_csv.exists(), "Section CSV written", str(sections_csv)))

        snippet_path = REPORT_DIR / "phase3e_dashboard_integration_snippet.txt"
        snippet_path.write_text(snippet + "\n", encoding="utf-8")
        checks.append(snippet_path.exists())
        lines.append(status_line(snippet_path.exists(), "Integration snippet written", str(snippet_path)))

    lines.append("")
    lines.append("=" * 96)
    all_ok = all(checks)
    final_status = "PASS" if all_ok else "FAIL"
    lines.append(f"Overall Phase 3E-7A checkpoint status: {final_status}")
    lines.append("=" * 96)

    report_path = REPORT_DIR / "phase3e_dashboard_integration_checkpoint_report.txt"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n".join(lines))
    print(f"\nSaved checkpoint report: {report_path}")

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
