"""
Install Phase 3H-2 guarded public Customer-view activation route helper.

The installer appends a safe helper block to config_form_app.py while keeping
public Customer-view activation disabled. It creates a timestamped backup before
writing and validates syntax after writing.
"""

from __future__ import annotations

import ast
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
BACKUP_DIR = PROJECT_ROOT / "outputs" / "backups" / "paid_simulator"

START = "# === PHASE3H_2_PUBLIC_CUSTOMER_ACTIVATION_ROUTE_START ==="
END = "# === PHASE3H_2_PUBLIC_CUSTOMER_ACTIVATION_ROUTE_END ==="

BLOCK = f'''
{START}
PHASE3H_2_PUBLIC_CUSTOMER_ACTIVATION_ROUTE_READY = "PHASE3H_2_PUBLIC_CUSTOMER_ACTIVATION_ROUTE_READY"
PHASE3H_2_PUBLIC_CUSTOMER_ENABLED = False


def _render_phase3h_public_customer_activation_route(st_module=None):
    """Guarded Phase 3H-2 public Customer-view activation route helper."""
    from app.paid_simulator.phase3h_public_customer_activation_route import (
        render_phase3h_public_activation_route,
    )
    return render_phase3h_public_activation_route(streamlit_module=st_module)
{END}
'''


def _remove_existing_block(text: str) -> str:
    if START not in text:
        return text
    before, rest = text.split(START, 1)
    if END not in rest:
        return before.rstrip() + "\n"
    _, after = rest.split(END, 1)
    return before.rstrip() + "\n" + after.lstrip()


def main() -> int:
    print("=" * 100)
    print("Phase 3H-2 guarded public activation route installer")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")

    if not DASHBOARD_FILE.exists():
        print(f"FAIL Dashboard file not found: {DASHBOARD_FILE}")
        return 1

    original = DASHBOARD_FILE.read_text(encoding="utf-8")
    ast.parse(original)

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"config_form_app_before_phase3h_2_{stamp}.py"
    backup.write_text(original, encoding="utf-8")

    cleaned = _remove_existing_block(original)
    updated = cleaned.rstrip() + "\n\n" + BLOCK.lstrip()
    ast.parse(updated)
    DASHBOARD_FILE.write_text(updated, encoding="utf-8")

    print(f"PASS Backup written: {backup}")
    print(f"PASS Dashboard updated safely: {DASHBOARD_FILE}")
    print("PASS PHASE3H_2_PUBLIC_CUSTOMER_ENABLED remains False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
