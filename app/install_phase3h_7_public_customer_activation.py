"""
install_phase3h_7_public_customer_activation.py

Guarded installer for Phase 3H-7 public Customer-view activation.

The installer:
1. Creates a timestamped backup of config_form_app.py.
2. Removes any prior Phase 3H-7 activation block.
3. Appends an inert, syntax-safe activation helper block at end of file.
4. Validates Python syntax before writing.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
BACKUP_DIR = PROJECT_ROOT / "outputs" / "backups" / "paid_simulator"
START_MARKER = "# BEGIN PHASE3H_7_PUBLIC_CUSTOMER_ACTIVATION"
END_MARKER = "# END PHASE3H_7_PUBLIC_CUSTOMER_ACTIVATION"

BLOCK = f'''
{START_MARKER}
# Controlled public Customer-view activation marker.
# Added by app/install_phase3h_7_public_customer_activation.py.
PHASE3H_7_PUBLIC_CUSTOMER_ACTIVATION_READY = "PHASE3H_7_PUBLIC_CUSTOMER_ACTIVATION_READY"
PHASE3H_7_PUBLIC_CUSTOMER_ENABLED = True
PHASE3H_7_RELEASE_DECISION = "PHASE3H_7_PUBLIC_CUSTOMER_VIEW_CONTROLLED_ACTIVATION_ENABLED"


def _render_phase3h_7_public_customer_activation():
    """Render the Phase 3H-7 public Customer-view activation helper when called."""
    from app.paid_simulator.phase3h_public_customer_activation import (
        render_phase3h_7_public_customer_activation,
    )

    return render_phase3h_7_public_customer_activation()
{END_MARKER}
'''


def remove_existing_block(text: str) -> str:
    start = text.find(START_MARKER)
    if start == -1:
        return text
    end = text.find(END_MARKER, start)
    if end == -1:
        return text[:start].rstrip() + "\n"
    end += len(END_MARKER)
    return (text[:start] + text[end:]).rstrip() + "\n"


def main() -> int:
    if not DASHBOARD_FILE.exists():
        print(f"ERROR: dashboard file not found: {DASHBOARD_FILE}")
        return 1

    py_compile.compile(str(DASHBOARD_FILE), doraise=True)

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"config_form_app_before_phase3h_7_{stamp}.py"
    shutil.copy2(DASHBOARD_FILE, backup)

    original = DASHBOARD_FILE.read_text(encoding="utf-8")
    cleaned = remove_existing_block(original)
    updated = cleaned.rstrip() + "\n\n" + BLOCK.lstrip()

    temp = DASHBOARD_FILE.with_suffix(".phase3h7.tmp.py")
    temp.write_text(updated, encoding="utf-8")
    try:
        py_compile.compile(str(temp), doraise=True)
    finally:
        temp.unlink(missing_ok=True)

    DASHBOARD_FILE.write_text(updated, encoding="utf-8")
    py_compile.compile(str(DASHBOARD_FILE), doraise=True)

    print("Phase 3H-7 controlled public Customer-view activation block installed.")
    print(f"Backup created: {backup}")
    print(f"Dashboard file: {DASHBOARD_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
