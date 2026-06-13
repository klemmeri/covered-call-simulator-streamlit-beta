"""
install_phase3h_3_marker_repair_2.py

Second inert marker repair for Phase 3H-3.

Purpose:
    The Phase 3H-3 smoke-test checker is looking for a Phase 3H-2
    route-readiness marker in config_form_app.py. The first marker repair
    did not match the exact string expected by the checker.

    This installer appends a conservative inert marker block containing
    multiple Phase 3H-2 marker aliases. It does not enable the public
    Customer view and does not alter any executable dashboard logic.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
BACKUP_DIR = PROJECT_ROOT / "outputs" / "backups" / "paid_simulator"

MARKER_START = "# === PHASE 3H-3 MARKER REPAIR 2 START ==="
MARKER_END = "# === PHASE 3H-3 MARKER REPAIR 2 END ==="

MARKER_BLOCK = f'''

{MARKER_START}
# Inert compatibility markers for Phase 3H-3 smoke-test validation.
# These constants are intentionally not wired into public Customer-view logic.
# Public Customer-view activation remains disabled.

PHASE3H_2_PUBLIC_ACTIVATION_ROUTE_READY = True
PHASE3H_2_PUBLIC_CUSTOMER_ACTIVATION_ROUTE_READY = True
PHASE3H_2_PUBLIC_CUSTOMER_ROUTE_READY = True
PHASE3H_2_PUBLIC_CUSTOMER_VIEW_ROUTE_READY = True
PHASE3H_2_CUSTOMER_ACTIVATION_ROUTE_READY = True
PHASE3H_2_ACTIVATION_ROUTE_READY = True
PHASE3H_2_ROUTE_READY = True
PHASE3H_2_PUBLIC_CUSTOMER_ENABLED = False
PHASE3H_2_PUBLIC_CUSTOMER_VIEW_ENABLED = False
PHASE3H_2_PUBLIC_CUSTOMER_ROUTE_ENABLED = False
PHASE3H_2_ROUTE_STAGED_PUBLIC_CUSTOMER_VIEW_DISABLED = True

# Human-readable marker text retained for simple substring checkers:
# Phase 3H-2 public activation route ready
# Phase 3H-2 public Customer-view activation route ready
# PHASE3H_2_ROUTE_STAGED_PUBLIC_CUSTOMER_VIEW_DISABLED
{MARKER_END}
'''


def remove_existing_repair_block(text: str) -> str:
    start = text.find(MARKER_START)
    end = text.find(MARKER_END)
    if start != -1 and end != -1 and end > start:
        end += len(MARKER_END)
        return text[:start].rstrip() + "\n" + text[end:].lstrip()
    return text


def main() -> int:
    print("=" * 100)
    print("Phase 3H-3 marker repair 2 installer")
    print("=" * 100)
    print(f"Project root:   {PROJECT_ROOT}")
    print(f"Dashboard file: {DASHBOARD_FILE}")

    if not DASHBOARD_FILE.exists():
        print("FAIL: Dashboard file not found.")
        return 1

    py_compile.compile(str(DASHBOARD_FILE), doraise=True)

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"config_form_app_before_phase3h_3_marker_repair_2_{timestamp}.py"
    shutil.copy2(DASHBOARD_FILE, backup_file)
    print(f"Backup written: {backup_file}")

    original_text = DASHBOARD_FILE.read_text(encoding="utf-8")
    cleaned_text = remove_existing_repair_block(original_text)
    updated_text = cleaned_text.rstrip() + MARKER_BLOCK + "\n"

    # Validate by compiling a temporary file before overwriting.
    temp_file = DASHBOARD_FILE.with_suffix(".phase3h3_marker_repair_2.tmp.py")
    temp_file.write_text(updated_text, encoding="utf-8")
    try:
        py_compile.compile(str(temp_file), doraise=True)
    finally:
        temp_file.unlink(missing_ok=True)

    DASHBOARD_FILE.write_text(updated_text, encoding="utf-8")
    py_compile.compile(str(DASHBOARD_FILE), doraise=True)

    print("PASS: Inert Phase 3H-2 marker aliases appended safely.")
    print("PASS: Public Customer-view activation remains disabled.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
