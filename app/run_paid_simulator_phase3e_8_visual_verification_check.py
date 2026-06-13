"""
run_paid_simulator_phase3e_8_visual_verification_check.py

Phase 3E-8 visual verification checklist for the Covered Call Simulator.

This checkpoint is intentionally browser-facing. It does not change the
Streamlit dashboard. Instead, it verifies that the dashboard integration files
and markers exist, then writes a visual QA checklist that Mark can use while
viewing the dashboard in the browser.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
PANEL_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase3e_customer_workbench_streamlit_panel.py"
CHECKLIST_MD = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3e_8_browser_visual_checklist.md"
CHECKLIST_JSON = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3e_8_visual_verification.json"
CHECKPOINT_REPORT = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3e_8_visual_verification_checkpoint_report.txt"


@dataclass
class CheckResult:
    status: str
    name: str
    detail: str


def _status(condition: bool) -> str:
    return "PASS" if condition else "FAIL"


def _add(results: list[CheckResult], condition: bool, name: str, detail: str) -> None:
    results.append(CheckResult(_status(condition), name, detail))


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="cp1252")


def _import_dashboard_file() -> tuple[bool, str]:
    try:
        spec = importlib.util.spec_from_file_location("phase3e_dashboard_import_check", DASHBOARD_FILE)
        if spec is None or spec.loader is None:
            return False, "could not build import spec"
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return True, "config_form_app.py imported"
    except Exception as exc:  # pragma: no cover - diagnostic checkpoint path
        return False, repr(exc)


def _import_panel_model() -> tuple[bool, str, dict[str, Any]]:
    try:
        from app.paid_simulator.phase3e_customer_workbench_streamlit_panel import (
            PHASE3E_PANEL_TITLE,
            build_panel_render_model,
            render_phase3e_customer_workbench_panel,
        )

        model = build_panel_render_model()
        render_model = render_phase3e_customer_workbench_panel(streamlit_module=None)
        details = {
            "panel_title": PHASE3E_PANEL_TITLE,
            "model_title": model.get("title"),
            "render_title": render_model.get("title") if isinstance(render_model, dict) else None,
            "section_count": len(model.get("sections", [])) if isinstance(model, dict) else None,
        }
        return True, "panel model built and render fallback returned", details
    except Exception as exc:  # pragma: no cover - diagnostic checkpoint path
        return False, repr(exc), {}


def _build_visual_checklist() -> str:
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""# Phase 3E-8 Browser Visual Verification Checklist

Generated: {generated}

Project root:

```text
{PROJECT_ROOT}
```

## Purpose

This checklist verifies the browser-facing dashboard behavior after the Phase 3E Developer-view tab integration.

Phase 3E should be visible only in Developer view. The Customer view should remain protected from experimental/developer controls.

## How to run the dashboard

From PyCharm, open the terminal or use your current Streamlit run method and run:

```text
streamlit run app\\paid_simulator\\config_form_app.py
```

Then open the local Streamlit browser page if it does not open automatically.

## Visual checks

### 1. Dashboard opens

Expected result:

```text
The paid simulator dashboard loads without a red Python traceback.
```

Mark as PASS if the browser dashboard opens normally.

### 2. Customer view remains clean

Expected result:

```text
The Customer view does not show Phase 3E customer payoff workbench, Developer-view labels, checkpoint tools, or test controls.
```

Mark as PASS if customer-facing users would not see Phase 3E experimental workflow controls.

### 3. Developer view still shows prior Phase 3D material

Expected result:

```text
Developer view still contains the Phase 3D integrated overlay / payoff-overlay area.
```

Mark as PASS if Phase 3D remains visible and usable.

### 4. Phase 3E Developer-view workbench is available

Expected result:

```text
Developer view includes a Phase 3E customer payoff workbench entry, helper, or panel.
```

Mark as PASS if Phase 3E is visible in the Developer-view area and not in Customer view.

### 5. Phase 3E panel content is customer-facing

Expected result:

```text
The Phase 3E workbench uses customer-friendly labels such as current price, strike, premium, breakeven, max profit, downside cushion, and assignment zone.
```

Mark as PASS if the labels are understandable and not implementation/debug language.

### 6. Risk warnings appear

Expected result:

```text
The Phase 3E workbench includes clear warning or caution language for risky covered-call setups.
```

Mark as PASS if a customer would see warnings before relying on a risky setup.

### 7. Save/reload/export actions are visible or clearly staged

Expected result:

```text
The Phase 3E workbench shows save, reload, refresh, or export workflow language, even if some controls remain staged for the next checkpoint.
```

Mark as PASS if the intended customer workflow is visible enough for visual QA.

## If all visual checks pass

Say:

```text
pass next
```

Next recommended checkpoint:

```text
Phase 3E-9 — Customer workflow polish and final Phase 3E completion report
```
"""


def main() -> int:
    results: list[CheckResult] = []

    print("=" * 100)
    print("Phase 3E-8 browser visual verification check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")

    print("\nExpected files")
    print("-" * 100)
    _add(results, DASHBOARD_FILE.exists(), "Dashboard file exists", str(DASHBOARD_FILE))
    _add(results, PANEL_FILE.exists(), "Phase 3E panel file exists", str(PANEL_FILE))

    dashboard_text = _read_text(DASHBOARD_FILE) if DASHBOARD_FILE.exists() else ""
    panel_text = _read_text(PANEL_FILE) if PANEL_FILE.exists() else ""

    print("\nDashboard import and marker checks")
    print("-" * 100)
    ok, detail = _import_dashboard_file()
    _add(results, ok, "Dashboard imports without syntax/runtime error", detail)
    _add(results, "PHASE3E_7C_DEVELOPER_TAB_READY" in dashboard_text, "Phase 3E readiness marker present", "PHASE3E_7C_DEVELOPER_TAB_READY")
    _add(results, "_render_phase3e_customer_payoff_workbench_tab" in dashboard_text, "Phase 3E helper function present", "_render_phase3e_customer_payoff_workbench_tab")
    _add(results, "Phase 3D" in dashboard_text or "phase3d" in dashboard_text.lower(), "Phase 3D markers still present", "Phase 3D marker search")
    _add(results, "Customer" in dashboard_text or "customer" in dashboard_text.lower(), "Customer-view markers still present", "Customer marker search")
    _add(results, "CUSTOMER_VIEW_PHASE3E_ENABLED = True" not in dashboard_text, "Customer view is not Phase 3E enabled", "customer protected")

    print("\nPanel model checks")
    print("-" * 100)
    panel_ok, panel_detail, panel_model_details = _import_panel_model()
    _add(results, panel_ok, "Panel model and fallback render work", panel_detail)
    _add(results, "current price" in panel_text.lower(), "Current price label present", "current price")
    _add(results, "breakeven" in panel_text.lower(), "Breakeven label present", "breakeven")
    _add(results, "max profit" in panel_text.lower(), "Max profit label present", "max profit")
    _add(results, "downside cushion" in panel_text.lower(), "Downside cushion label present", "downside cushion")
    _add(results, "assignment zone" in panel_text.lower(), "Assignment zone label present", "assignment zone")
    _add(results, "warning" in panel_text.lower() or "risk" in panel_text.lower(), "Warning/risk language present", "warning/risk")

    print("\nWriting browser checklist")
    print("-" * 100)
    CHECKLIST_MD.parent.mkdir(parents=True, exist_ok=True)
    checklist = _build_visual_checklist()
    CHECKLIST_MD.write_text(checklist, encoding="utf-8")
    _add(results, CHECKLIST_MD.exists(), "Browser visual checklist written", str(CHECKLIST_MD))

    CHECKLIST_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "checkpoint": "Phase 3E-8",
        "project_root": str(PROJECT_ROOT),
        "dashboard_file": str(DASHBOARD_FILE),
        "panel_file": str(PANEL_FILE),
        "visual_checklist": str(CHECKLIST_MD),
        "panel_model_details": panel_model_details,
        "results": [result.__dict__ for result in results],
    }
    CHECKLIST_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _add(results, CHECKLIST_JSON.exists(), "Visual verification JSON written", str(CHECKLIST_JSON))

    for result in results:
        print(f"{result.status:<10} {result.name:<65} {result.detail}")

    failures = [result for result in results if result.status != "PASS"]

    CHECKPOINT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "Phase 3E-8 browser visual verification checkpoint report",
        "=" * 100,
        f"Project root: {PROJECT_ROOT}",
        "",
    ]
    for result in results:
        lines.append(f"{result.status:<10} {result.name:<65} {result.detail}")
    lines.extend([
        "",
        "Overall Phase 3E-8 checkpoint status: " + ("PASS" if not failures else "FAIL"),
        f"Browser checklist: {CHECKLIST_MD}",
        f"JSON report: {CHECKLIST_JSON}",
    ])
    CHECKPOINT_REPORT.write_text("\n".join(lines), encoding="utf-8")

    print("\n" + "=" * 100)
    print("Overall Phase 3E-8 checkpoint status: " + ("PASS" if not failures else "FAIL"))
    print("=" * 100)
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved browser checklist: {CHECKLIST_MD}")
    print(f"Saved checkpoint JSON:   {CHECKLIST_JSON}")

    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
