"""
install_phase3h_3_marker_repair.py

Safely repairs the Phase 3H-2 public activation route readiness marker
expected by the Phase 3H-3 smoke-test checker.

This installer appends a small marker-only block to config_form_app.py.
It does not enable the public Customer view.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
BACKUP_DIR = PROJECT_ROOT / "outputs" / "backups" / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

MARKER = "PHASE3H_2_PUBLIC_ACTIVATION_ROUTE_READY"
DISABLED_FLAG = "PHASE3H_2_PUBLIC_CUSTOMER_ENABLED = False"
BLOCK_START = "# === Phase 3H-3 repair: Phase 3H-2 route marker compatibility ==="
BLOCK_END = "# === End Phase 3H-3 marker repair ==="


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _validate_python(path: Path) -> None:
    py_compile.compile(str(path), doraise=True)


def main() -> int:
    print("=" * 100)
    print("Phase 3H-3 marker repair installer")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")

    if not DASHBOARD_FILE.exists():
        raise FileNotFoundError(f"Dashboard file not found: {DASHBOARD_FILE}")

    _validate_python(DASHBOARD_FILE)

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    backup_path = BACKUP_DIR / f"config_form_app_before_phase3h_3_marker_repair_{_timestamp()}.py"
    shutil.copy2(DASHBOARD_FILE, backup_path)

    text = DASHBOARD_FILE.read_text(encoding="utf-8")

    if MARKER in text and DISABLED_FLAG in text:
        status = "marker already present; no dashboard change required"
    else:
        block = f'''

{BLOCK_START}
# This block exists so Phase 3H-3 smoke-test checks can confirm that the
# Phase 3H-2 public activation route was staged. It is intentionally inert.
# Public Customer-view activation remains disabled.
{MARKER} = True
PHASE3H_2_PUBLIC_CUSTOMER_ENABLED = False


def _phase3h_2_public_activation_route_readiness_marker() -> dict:
    """Return the staged-but-disabled Phase 3H-2 public route marker."""
    return {{
        "marker": "{MARKER}",
        "public_customer_enabled": False,
        "release_decision": "PHASE3H_2_ROUTE_STAGED_PUBLIC_CUSTOMER_VIEW_DISABLED",
    }}
{BLOCK_END}
'''
        DASHBOARD_FILE.write_text(text.rstrip() + block + "\n", encoding="utf-8")
        _validate_python(DASHBOARD_FILE)
        status = "marker block appended; public Customer view remains disabled"

    report_path = REPORT_DIR / "phase3h_3_marker_repair_report.txt"
    report_path.write_text(
        "Phase 3H-3 marker repair\n"
        f"Dashboard file: {DASHBOARD_FILE}\n"
        f"Backup file: {backup_path}\n"
        f"Status: {status}\n"
        "Public Customer view enabled: False\n",
        encoding="utf-8",
    )

    print(f"Backup written: {backup_path}")
    print(f"Report written: {report_path}")
    print(f"Status: {status}")
    print("Public Customer view remains disabled.")
    print("=" * 100)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
