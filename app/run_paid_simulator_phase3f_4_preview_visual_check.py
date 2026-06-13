"""
Phase 3F-4 protected customer-preview visual verification check.

This script performs a non-invasive verification of the protected customer-preview
route created in Phase 3F-3. It does not modify dashboard code.
"""

from __future__ import annotations

import ast
import csv
import importlib.util
import json
from datetime import datetime
from pathlib import Path
from typing import Any


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_SIM_DIR = APP_DIR / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"

DASHBOARD_FILE = PAID_SIM_DIR / "config_form_app.py"
ROUTE_FILE = PAID_SIM_DIR / "phase3f_customer_preview_route.py"
SHELL_FILE = PAID_SIM_DIR / "phase3f_customer_preview_shell.py"
PANEL_FILE = PAID_SIM_DIR / "phase3e_customer_workbench_streamlit_panel.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase3f_4_preview_visual_verification.md"

REPORT_FILE = OUTPUT_REPORT_DIR / "phase3f_4_preview_visual_checkpoint_report.txt"
JSON_FILE = OUTPUT_REPORT_DIR / "phase3f_4_preview_visual_checkpoint.json"
CSV_FILE = OUTPUT_TABLE_DIR / "phase3f_4_preview_visual_checklist.csv"
BROWSER_CHECKLIST_FILE = OUTPUT_REPORT_DIR / "phase3f_4_browser_preview_checklist.md"


class CheckRecorder:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(self, name: str, passed: bool, detail: Any = "") -> None:
        self.rows.append({"name": name, "passed": bool(passed), "detail": str(detail)})

    @property
    def ok(self) -> bool:
        return all(row["passed"] for row in self.rows)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def syntax_valid(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(read_text(path), filename=str(path))
        return True, "syntax valid"
    except Exception as exc:  # noqa: BLE001
        return False, repr(exc)


def import_module_from_path(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize_model(model: Any) -> dict[str, Any]:
    if isinstance(model, dict):
        return model
    if hasattr(model, "to_dict"):
        value = model.to_dict()
        if isinstance(value, dict):
            return value
    if hasattr(model, "__dict__"):
        return dict(model.__dict__)
    return {"raw_type": type(model).__name__, "raw_value": str(model)}


def contains_any(text: str, terms: list[str]) -> bool:
    lower_text = text.lower()
    return any(term.lower() in lower_text for term in terms)


def write_outputs(recorder: CheckRecorder, route_model: dict[str, Any]) -> None:
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("=" * 100)
    lines.append("Phase 3F-4 protected customer-preview visual verification check")
    lines.append("=" * 100)
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append("")
    for row in recorder.rows:
        status = "PASS" if row["passed"] else "FAIL"
        lines.append(f"{status:<10} {row['name']:<70} {row['detail']}")
    lines.append("")
    lines.append("=" * 100)
    lines.append(f"Overall Phase 3F-4 checkpoint status: {'PASS' if recorder.ok else 'FAIL'}")
    lines.append("=" * 100)
    REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    JSON_FILE.write_text(
        json.dumps(
            {
                "phase": "Phase 3F-4",
                "checkpoint": "protected customer-preview visual verification",
                "status": "PASS" if recorder.ok else "FAIL",
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "project_root": str(PROJECT_ROOT),
                "route_model": route_model,
                "checks": recorder.rows,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    with CSV_FILE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "passed", "detail"])
        writer.writeheader()
        writer.writerows(recorder.rows)

    checklist = [
        "# Phase 3F-4 Browser Preview Checklist",
        "",
        "Run the dashboard with:",
        "",
        "```text",
        "streamlit run app\\paid_simulator\\config_form_app.py",
        "```",
        "",
        "Confirm these items manually:",
        "",
        "1. The dashboard opens without a red traceback.",
        "2. The ordinary Customer view does not show Phase 3F preview controls.",
        "3. Developer view still contains Phase 3D and Phase 3E material.",
        "4. The protected Phase 3F preview route/helper is present in Developer-view code path.",
        "5. The customer-preview shell uses customer-facing language, not developer/test labels.",
        "6. Guardrail language is visible or available in the route model.",
        "7. The preview remains disabled for ordinary Customer view.",
        "",
        "Route model summary:",
        "",
        "```json",
        json.dumps(route_model, indent=2),
        "```",
    ]
    BROWSER_CHECKLIST_FILE.write_text("\n".join(checklist) + "\n", encoding="utf-8")


def main() -> int:
    recorder = CheckRecorder()
    route_model: dict[str, Any] = {}

    print("=" * 100)
    print("Phase 3F-4 protected customer-preview visual verification check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    expected_files = [
        ("Dashboard file", DASHBOARD_FILE),
        ("Phase 3F preview route", ROUTE_FILE),
        ("Phase 3F preview shell", SHELL_FILE),
        ("Phase 3E workbench panel", PANEL_FILE),
        ("Phase 3F-4 documentation", DOC_FILE),
    ]
    for label, path in expected_files:
        recorder.add(f"{label} exists", path.exists(), path)

    for label, path in [
        ("Dashboard syntax", DASHBOARD_FILE),
        ("Preview route syntax", ROUTE_FILE),
        ("Preview shell syntax", SHELL_FILE),
        ("Workbench panel syntax", PANEL_FILE),
    ]:
        if path.exists():
            passed, detail = syntax_valid(path)
            recorder.add(label, passed, detail)

    dashboard_text = read_text(DASHBOARD_FILE) if DASHBOARD_FILE.exists() else ""
    route_text = read_text(ROUTE_FILE) if ROUTE_FILE.exists() else ""
    shell_text = read_text(SHELL_FILE) if SHELL_FILE.exists() else ""
    panel_text = read_text(PANEL_FILE) if PANEL_FILE.exists() else ""

    recorder.add(
        "Dashboard has Phase 3F-3 readiness marker",
        "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY" in dashboard_text,
        "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY",
    )
    recorder.add(
        "Dashboard has Phase 3F preview helper function",
        "_render_phase3f_customer_preview_route" in dashboard_text,
        "_render_phase3f_customer_preview_route",
    )
    recorder.add(
        "Ordinary Customer view remains protected",
        "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_CUSTOMER_ENABLED = True" not in dashboard_text,
        "Customer route is not enabled",
    )
    recorder.add(
        "Phase 3E Developer marker still present",
        "PHASE3E_7C_DEVELOPER_TAB_READY" in dashboard_text,
        "Phase 3E marker search",
    )
    recorder.add(
        "Phase 3D markers still present",
        "Phase 3D" in dashboard_text or "phase3d" in dashboard_text.lower(),
        "Phase 3D marker search",
    )
    recorder.add(
        "Customer-view markers still present",
        "Customer" in dashboard_text and "Developer" in dashboard_text,
        "Customer/Developer marker search",
    )

    try:
        route_module = import_module_from_path("phase3f_customer_preview_route_check", ROUTE_FILE)
        build_fn = getattr(route_module, "build_customer_preview_route_model", None)
        render_fn = getattr(route_module, "render_customer_preview_route", None)
        recorder.add("Preview route build function exists", callable(build_fn), "build_customer_preview_route_model")
        recorder.add("Preview route render function exists", callable(render_fn), "render_customer_preview_route")
        if callable(build_fn):
            route_model = normalize_model(build_fn())
            recorder.add(
                "Route model has ready marker",
                route_model.get("marker") == "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY",
                route_model.get("marker"),
            )
            recorder.add(
                "Route model keeps customer disabled",
                route_model.get("customer_enabled") is False,
                route_model.get("customer_enabled"),
            )
            recorder.add(
                "Route model has sections",
                len(route_model.get("sections", [])) >= 3,
                len(route_model.get("sections", [])),
            )
            recorder.add(
                "Route model has guardrails",
                len(route_model.get("guardrails", [])) >= 3,
                len(route_model.get("guardrails", [])),
            )
        if callable(render_fn):
            rendered = render_fn(streamlit_module=None)
            recorder.add(
                "Fallback render returns dictionary model",
                isinstance(rendered, dict),
                type(rendered).__name__,
            )
    except Exception as exc:  # noqa: BLE001
        recorder.add("Preview route imports/builds/renders", False, repr(exc))

    combined_preview_text = "\n".join([route_text, shell_text, panel_text])
    recorder.add(
        "Customer-facing labels present",
        contains_any(combined_preview_text, ["current price", "breakeven", "max profit", "downside cushion", "assignment zone"]),
        "payoff labels",
    )
    recorder.add(
        "Warning/risk language present",
        contains_any(combined_preview_text, ["warning", "risk", "guardrail", "protected"]),
        "warning/risk/guardrail",
    )
    recorder.add(
        "Preview language does not claim public release",
        "public customer release enabled" not in combined_preview_text.lower(),
        "no premature release language",
    )

    write_outputs(recorder, route_model)

    for row in recorder.rows:
        status = "PASS" if row["passed"] else "FAIL"
        print(f"{status:<10} {row['name']:<70} {row['detail']}")

    print()
    print("=" * 100)
    print(f"Overall Phase 3F-4 checkpoint status: {'PASS' if recorder.ok else 'FAIL'}")
    print("=" * 100)
    print(f"Saved checkpoint report: {REPORT_FILE}")
    print(f"Saved checkpoint JSON:   {JSON_FILE}")
    print(f"Saved checklist CSV:     {CSV_FILE}")
    print(f"Saved browser checklist: {BROWSER_CHECKLIST_FILE}")
    return 0 if recorder.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
