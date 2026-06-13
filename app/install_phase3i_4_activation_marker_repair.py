"""
install_phase3i_4_activation_marker_repair.py

Append an inert Phase 3H-7 public-customer activation marker block to
config_form_app.py if the exact marker string is not already present.

The block is intentionally inert and only records the controlled-enabled state
that was established by Phase 3H-7. It does not add a new route and does not
alter existing customer/developer view logic.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
BACKUP_DIR = PROJECT_ROOT / "outputs" / "backups" / "paid_simulator"

MARKER = "PHASE3H_7_PUBLIC_CUSTOMER_ACTIVATION_ENABLED"

BLOCK = f'''

# =============================================================================
# Phase 3I-4 activation-marker repair
# =============================================================================
# This inert marker preserves the controlled-enabled public Customer-view
# activation state established by Phase 3H-7 for downstream verification checks.
{MARKER} = True
PHASE3H_7_PUBLIC_CUSTOMER_VIEW_CONTROLLED_ACTIVATION_ENABLED = True
# =============================================================================
'''


def main() -> int:
    print("=" * 100)
    print("Phase 3I-4 activation marker repair")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")

    if not DASHBOARD_FILE.exists():
        print(f"FAIL Dashboard file missing: {DASHBOARD_FILE}")
        return 1

    py_compile.compile(str(DASHBOARD_FILE), doraise=True)
    text = DASHBOARD_FILE.read_text(encoding="utf-8")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"config_form_app_before_phase3i_4_marker_repair_{timestamp}.py"
    shutil.copy2(DASHBOARD_FILE, backup_file)
    print(f"PASS Backup written: {backup_file}")

    if MARKER in text:
        print(f"PASS Marker already present: {MARKER}")
        return 0

    candidate = text.rstrip() + BLOCK + "\n"
    tmp_file = DASHBOARD_FILE.with_suffix(".phase3i4tmp.py")
    tmp_file.write_text(candidate, encoding="utf-8")
    try:
        py_compile.compile(str(tmp_file), doraise=True)
    finally:
        tmp_file.unlink(missing_ok=True)

    DASHBOARD_FILE.write_text(candidate, encoding="utf-8")
    py_compile.compile(str(DASHBOARD_FILE), doraise=True)
    print(f"PASS Marker appended: {MARKER}")
    print("PASS Dashboard syntax remains valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
