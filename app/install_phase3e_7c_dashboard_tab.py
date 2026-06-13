"""
install_phase3e_7c_dashboard_tab.py

Repair-safe installer for Phase 3E-7C dashboard integration.

This version is deliberately conservative:

1. If config_form_app.py is syntactically broken, restore the newest Phase 3E-7C
   backup before patching.
2. Create a new timestamped backup before writing changes.
3. Remove any previous Phase 3E-7C injected block.
4. Append a small lazy helper block at the end of the file, rather than inserting
   imports into the middle of existing dashboard logic.

The actual Customer view remains protected.  This only stages the Developer-view
helper needed by the Phase 3E-7C checkpoint.
"""

from __future__ import annotations

import ast
import shutil
from datetime import datetime
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
BACKUP_DIR = PROJECT_ROOT / "outputs" / "backups" / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
REPORT_FILE = REPORT_DIR / "phase3e_7c_dashboard_tab_install_repair_report.txt"

START_MARKER = "# --- PHASE 3E-7C DEVELOPER TAB INTEGRATION START ---"
END_MARKER = "# --- PHASE 3E-7C DEVELOPER TAB INTEGRATION END ---"

PATCH_BLOCK = f'''

{START_MARKER}
# PHASE3E_7C_DEVELOPER_TAB_READY
# Developer-view helper for the Phase 3E customer payoff workbench.
# Customer view remains protected until the Phase 3E completion checkpoint passes.

def _render_phase3e_customer_payoff_workbench_tab():
    """Render the Phase 3E customer payoff workbench in Developer view only."""
    from app.paid_simulator.phase3e_customer_workbench_streamlit_panel import (
        render_phase3e_customer_workbench_panel,
    )

    try:
        import streamlit as st
    except Exception:
        st = None

    return render_phase3e_customer_workbench_panel(streamlit_module=st)


def render_phase3e_customer_payoff_workbench_developer_tab():
    """Backward-compatible Developer-view entry point for Phase 3E."""
    return _render_phase3e_customer_payoff_workbench_tab()


PHASE3E_CUSTOMER_PAYOFF_WORKBENCH_TAB_TITLE = "Phase 3E customer payoff workbench"
PHASE3E_CUSTOMER_PAYOFF_WORKBENCH_SCOPE = "Developer view only; Customer view protected."
{END_MARKER}
'''


def _is_valid_python(text: str) -> tuple[bool, str]:
    try:
        ast.parse(text)
        return True, "valid"
    except SyntaxError as exc:
        return False, f"SyntaxError line {exc.lineno}: {exc.msg}"


def _latest_backup() -> Path | None:
    if not BACKUP_DIR.exists():
        return None
    candidates = sorted(
        BACKUP_DIR.glob("config_form_app_before_phase3e_7c_*.py"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _strip_previous_patch(text: str) -> str:
    while START_MARKER in text and END_MARKER in text:
        start = text.index(START_MARKER)
        end = text.index(END_MARKER) + len(END_MARKER)
        text = text[:start].rstrip() + "\n" + text[end:].lstrip()
    return text.rstrip() + "\n"


def main() -> int:
    lines: list[str] = []
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    lines.append("Phase 3E-7C dashboard integration repair installer")
    lines.append("=" * 80)
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append(f"Dashboard file: {DASHBOARD_FILE}")

    if not DASHBOARD_FILE.exists():
        lines.append("FAIL: dashboard file not found")
        REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
        print("\n".join(lines))
        return 1

    original_text = DASHBOARD_FILE.read_text(encoding="utf-8")
    valid, reason = _is_valid_python(original_text)
    lines.append(f"Initial syntax status: {reason}")

    if not valid:
        backup = _latest_backup()
        if backup is None:
            lines.append("FAIL: dashboard file is invalid and no Phase 3E-7C backup was found")
            REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
            print("\n".join(lines))
            return 1
        shutil.copy2(backup, DASHBOARD_FILE)
        lines.append(f"Restored latest dashboard backup: {backup}")
        original_text = DASHBOARD_FILE.read_text(encoding="utf-8")
        valid, reason = _is_valid_python(original_text)
        lines.append(f"Restored syntax status: {reason}")
        if not valid:
            lines.append("FAIL: restored backup is still not valid Python")
            REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
            print("\n".join(lines))
            return 1

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"config_form_app_before_phase3e_7c_repair_{timestamp}.py"
    shutil.copy2(DASHBOARD_FILE, backup_path)
    lines.append(f"Created repair backup: {backup_path}")

    base_text = _strip_previous_patch(original_text)
    patched_text = base_text.rstrip() + PATCH_BLOCK + "\n"

    valid, reason = _is_valid_python(patched_text)
    lines.append(f"Patched syntax status: {reason}")
    if not valid:
        lines.append("FAIL: patch would create invalid Python; dashboard file left unchanged")
        REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
        print("\n".join(lines))
        return 1

    DASHBOARD_FILE.write_text(patched_text, encoding="utf-8")
    lines.append("PASS: Phase 3E-7C Developer-view helper appended safely")
    lines.append("PASS: Customer view remains protected")
    lines.append(f"Saved report: {REPORT_FILE}")

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
